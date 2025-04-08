package reranker

import (
	"context"
	"fmt"
	"sort"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/tcm"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// CrossEncoderReranker 基于跨编码器的重排序器
type CrossEncoderReranker struct {
	// 模型名称
	modelName string
	
	// 模型端点
	endpoint string
	
	// API密钥
	apiKey string
	
	// 批处理大小
	batchSize int
	
	// 默认选项
	defaultOptions RerankerOptions
	
	// 中医特定模型配置
	tcmModelConfig map[string]interface{}
	
	// 日志器
	logger utils.Logger
	
	// 最大请求重试次数
	maxRetries int
	
	// HuggingFace客户端
	hfClient *HuggingFaceClient
	
	// 缓存
	cache *utils.LRUCache
	
	// 中医术语处理器
	tcmProcessor *tcm.TerminologyProcessor
	
	// 中医术语库路径
	tcmTermLibraryPath string
}

// NewCrossEncoderReranker 创建跨编码器重排序器
func NewCrossEncoderReranker(modelName, endpoint, apiKey string, options RerankerOptions, logger utils.Logger) *CrossEncoderReranker {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	if options.BatchSize <= 0 {
		options.BatchSize = 16
	}
	
	return &CrossEncoderReranker{
		modelName:     modelName,
		endpoint:      endpoint,
		apiKey:        apiKey,
		batchSize:     options.BatchSize,
		defaultOptions: options,
		logger:        logger,
		maxRetries:    3,
		tcmModelConfig: make(map[string]interface{}),
		cache:         utils.NewLRUCache(1000), // 默认缓存1000个查询结果
	}
}

// Name 获取重排序器名称
func (r *CrossEncoderReranker) Name() string {
	return fmt.Sprintf("cross-encoder-%s", r.modelName)
}

// Initialize 初始化重排序器
func (r *CrossEncoderReranker) Initialize(ctx context.Context) error {
	// 加载中医特定的模型配置
	if r.defaultOptions.TCMSpecific {
		r.tcmModelConfig["domain"] = "tcm"
		r.tcmModelConfig["use_tcm_synonyms"] = true
		r.tcmModelConfig["enhance_tcm_terms"] = true
		
		// 初始化中医术语处理器
		r.tcmProcessor = tcm.NewTerminologyProcessor(r.logger)
		if err := r.tcmProcessor.Initialize(ctx, r.tcmTermLibraryPath); err != nil {
			r.logger.Warn("初始化中医术语处理器失败，将使用默认术语", "error", err)
			// 加载默认术语
			r.tcmProcessor.loadDefaultTerms()
		}
	}
	
	// 初始化HuggingFace客户端
	r.hfClient = NewHuggingFaceClient(r.modelName, r.apiKey, r.logger)
	r.hfClient.SetMaxRetries(r.maxRetries)
	
	// 尝试获取模型信息验证连接
	_, err := r.hfClient.GetModelInfo(ctx)
	if err != nil {
		r.logger.Warn("获取模型信息失败，将在首次使用时重试", "error", err)
	}
	
	r.logger.Info("初始化跨编码器重排序器", "model", r.modelName, "endpoint", r.endpoint)
	return nil
}

// Close 关闭重排序器
func (r *CrossEncoderReranker) Close() error {
	return nil
}

// SetTCMTermLibraryPath 设置中医术语库路径
func (r *CrossEncoderReranker) SetTCMTermLibraryPath(path string) {
	r.tcmTermLibraryPath = path
}

// Rerank 对文档进行重排序
func (r *CrossEncoderReranker) Rerank(ctx context.Context, query string, docs []models.Document, options RerankerOptions) ([]models.Document, error) {
	if len(docs) == 0 {
		return docs, nil
	}
	
	startTime := time.Now()
	defer func() {
		r.logger.Debug("重排序完成", 
			"query", query, 
			"docs_count", len(docs), 
			"time_ms", time.Since(startTime).Milliseconds(),
		)
	}()
	
	// 合并选项
	opts := r.mergeOptions(options)
	
	// 生成缓存键
	cacheKey := r.generateCacheKey(query, docs, opts)
	
	// 检查缓存
	if cachedResult, found := r.cache.Get(cacheKey); found {
		r.logger.Debug("使用缓存的重排序结果", "query", query)
		return cachedResult.([]models.Document), nil
	}
	
	// 准备输入
	inputs := make([]string, len(docs))
	for i, doc := range docs {
		// 将查询和文档内容组合为跨编码器输入
		inputs[i] = r.prepareInput(query, doc.Content, opts)
	}
	
	// 计算相关性分数
	scores, err := r.computeScores(ctx, query, inputs, opts)
	if err != nil {
		return nil, fmt.Errorf("计算重排序分数失败: %w", err)
	}
	
	// 更新文档分数
	for i := range docs {
		if i < len(scores) {
			docs[i].RerankerScore = scores[i]
			
			// 如果启用了中医特性，根据中医术语匹配度调整分数
			if opts.TCMSpecific && r.tcmProcessor != nil {
				tcmRelevance := r.calculateTCMRelevance(query, docs[i].Content)
				
				// 将TCM相关性作为加权因子
				if tcmRelevance > 0 {
					// 记录原始分数和调整后的分数
					originalScore := docs[i].RerankerScore
					// 根据TCM相关性调整分数，最多增加20%
					docs[i].RerankerScore *= (1.0 + tcmRelevance * 0.2)
					
					r.logger.Debug("调整中医相关性分数", 
						"doc_id", docs[i].ID, 
						"tcm_relevance", tcmRelevance,
						"original_score", originalScore,
						"adjusted_score", docs[i].RerankerScore,
					)
				}
			}
		}
	}
	
	// 根据重排序分数排序
	sort.Slice(docs, func(i, j int) bool {
		return docs[i].RerankerScore > docs[j].RerankerScore
	})
	
	// 根据TopK截断结果
	if opts.TopK > 0 && opts.TopK < len(docs) {
		docs = docs[:opts.TopK]
	}
	
	// 根据分数阈值过滤
	if opts.ScoreThreshold > 0 {
		filteredDocs := make([]models.Document, 0, len(docs))
		for _, doc := range docs {
			if doc.RerankerScore >= opts.ScoreThreshold {
				filteredDocs = append(filteredDocs, doc)
			}
		}
		docs = filteredDocs
	}
	
	// 更新缓存
	r.cache.Set(cacheKey, docs)
	
	return docs, nil
}

// 计算中医相关性
func (r *CrossEncoderReranker) calculateTCMRelevance(query, content string) float64 {
	if r.tcmProcessor == nil {
		return 0.0
	}
	
	// 提取查询中的中医术语
	queryTerms := r.tcmProcessor.ExtractTerms(query)
	if len(queryTerms) == 0 {
		return 0.0 // 查询不包含中医术语
	}
	
	// 提取内容中的中医术语
	contentTerms := r.tcmProcessor.ExtractTerms(content)
	if len(contentTerms) == 0 {
		return 0.0 // 内容不包含中医术语
	}
	
	// 计算查询术语和内容术语的重叠
	queryTermMap := make(map[string]bool)
	for _, term := range queryTerms {
		queryTermMap[term.Term] = true
	}
	
	// 计算匹配数量和总权重
	matchCount := 0
	totalWeight := 0.0
	
	for _, term := range contentTerms {
		if queryTermMap[term.Term] {
			matchCount++
			totalWeight += term.Weight
		}
	}
	
	// 计算相关性分数
	if matchCount == 0 {
		return 0.0
	}
	
	// 基础分 + 术语匹配率 + 权重因子
	baseScore := 0.2 // 基础分
	matchRatio := float64(matchCount) / float64(len(queryTerms)) // 术语匹配率
	weightFactor := totalWeight / float64(len(contentTerms)) // 权重因子
	
	return baseScore + matchRatio*0.5 + weightFactor*0.3
}

// BatchRerank 批量重排序
func (r *CrossEncoderReranker) BatchRerank(ctx context.Context, query string, docsBatch [][]models.Document, options RerankerOptions) ([][]models.Document, error) {
	results := make([][]models.Document, len(docsBatch))
	
	for i, docs := range docsBatch {
		rerankedDocs, err := r.Rerank(ctx, query, docs, options)
		if err != nil {
			return nil, fmt.Errorf("批量重排序第%d批失败: %w", i, err)
		}
		results[i] = rerankedDocs
	}
	
	return results, nil
}

// 合并用户选项和默认选项
func (r *CrossEncoderReranker) mergeOptions(options RerankerOptions) RerankerOptions {
	result := r.defaultOptions
	
	if options.TopK > 0 {
		result.TopK = options.TopK
	}
	
	if options.ScoreThreshold > 0 {
		result.ScoreThreshold = options.ScoreThreshold
	}
	
	if options.BatchSize > 0 {
		result.BatchSize = options.BatchSize
	}
	
	if options.MaxInputLength > 0 {
		result.MaxInputLength = options.MaxInputLength
	}
	
	if options.UserID != "" {
		result.UserID = options.UserID
	}
	
	if options.Domain != "" {
		result.Domain = options.Domain
	}
	
	return result
}

// 准备输入
func (r *CrossEncoderReranker) prepareInput(query, content string, options RerankerOptions) string {
	// 对于中医特定的重排序，增强关键中医术语
	if options.TCMSpecific && r.tcmProcessor != nil {
		query = r.enhanceTCMTerms(query)
		content = r.enhanceTCMContent(content)
	}
	
	// 截断内容以适应最大输入长度
	if options.MaxInputLength > 0 && len(content) > options.MaxInputLength {
		content = content[:options.MaxInputLength]
	}
	
	// 组合查询和内容
	return fmt.Sprintf("%s [SEP] %s", query, content)
}

// 增强中医术语
func (r *CrossEncoderReranker) enhanceTCMTerms(text string) string {
	if r.tcmProcessor == nil {
		return text
	}
	
	return r.tcmProcessor.EnhanceText(text)
}

// 增强中医内容
func (r *CrossEncoderReranker) enhanceTCMContent(content string) string {
	if r.tcmProcessor == nil {
		return content
	}
	
	return r.tcmProcessor.EnhanceText(content)
}

// 计算相关性分数
func (r *CrossEncoderReranker) computeScores(ctx context.Context, query string, inputs []string, options RerankerOptions) ([]float64, error) {
	// 将输入分批处理
	batches := r.batchInputs(inputs, options.BatchSize)
	
	allScores := make([]float64, 0, len(inputs))
	
	// 如果HuggingFace客户端未初始化，则初始化
	if r.hfClient == nil {
		r.Initialize(ctx)
	}
	
	// 处理每个批次
	for batchIndex, batch := range batches {
		// 准备文本对（查询+文档内容）
		textPairs := make([][]string, len(batch))
		for i, input := range batch {
			// 分割输入以获取查询和文档内容
			textPairs[i] = []string{query, input}
		}
		
		// 使用HuggingFace客户端获取分数
		scores, err := r.hfClient.GetCrossEncoderScores(ctx, textPairs)
		if err != nil {
			return nil, fmt.Errorf("批次%d获取分数失败: %w", batchIndex, err)
		}
		
		// 添加分数到结果
		allScores = append(allScores, scores...)
		
		// 记录批次进度
		r.logger.Debug("完成批次处理", 
			"batch", batchIndex+1, 
			"total_batches", len(batches),
			"batch_size", len(batch),
		)
	}
	
	return allScores, nil
}

// 将输入分批
func (r *CrossEncoderReranker) batchInputs(inputs []string, batchSize int) [][]string {
	if batchSize <= 0 {
		batchSize = r.batchSize
	}
	
	batchCount := (len(inputs) + batchSize - 1) / batchSize
	batches := make([][]string, 0, batchCount)
	
	for i := 0; i < len(inputs); i += batchSize {
		end := i + batchSize
		if end > len(inputs) {
			end = len(inputs)
		}
		
		batches = append(batches, inputs[i:end])
	}
	
	return batches
}

// 生成缓存键
func (r *CrossEncoderReranker) generateCacheKey(query string, docs []models.Document, options RerankerOptions) string {
	// 使用查询和选项生成缓存键
	// 实际实现可以使用更复杂的逻辑，包括文档ID
	return fmt.Sprintf("%s_%d_%d_%v", 
		query, 
		options.TopK, 
		options.BatchSize,
		options.TCMSpecific,
	)
}