package rag

import (
	"context"
	"fmt"
	"math"
	"sort"
	"strings"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// HybridSearcher 混合检索器接口
type HybridSearcher interface {
	// Search 执行混合检索
	Search(ctx context.Context, collectionName string, query string, options models.HybridSearchOptions) ([]models.Document, error)
	
	// Initialize 初始化混合检索器
	Initialize(ctx context.Context) error
	
	// Close 关闭混合检索器
	Close() error
}

// AdaptiveHybridSearcher 自适应混合检索器实现
type AdaptiveHybridSearcher struct {
	// 向量搜索器
	vectorSearcher VectorSearcher
	
	// 关键词搜索器
	keywordSearcher KeywordSearcher
	
	// 查询分析器
	queryAnalyzer QueryAnalyzer
	
	// 日志器
	logger utils.Logger
	
	// 最大并发请求数
	maxConcurrentRequests int
	
	// 默认选项
	defaultOptions models.HybridSearchOptions
	
	// 权重调整器
	weightAdjuster WeightAdjuster
}

// VectorSearcher 向量搜索器接口
type VectorSearcher interface {
	// Search 执行向量搜索
	Search(ctx context.Context, collectionName string, vector []float32, limit int, filter map[string]interface{}) ([]models.Document, error)
}

// KeywordSearcher 关键词搜索器接口
type KeywordSearcher interface {
	// Search 执行关键词搜索
	Search(ctx context.Context, collectionName string, query string, limit int, filter map[string]interface{}) ([]models.Document, error)
}

// QueryAnalyzer 查询分析器接口
type QueryAnalyzer interface {
	// Analyze 分析查询，返回查询类型和关键词
	Analyze(ctx context.Context, query string) (QueryAnalysisResult, error)
}

// QueryAnalysisResult 查询分析结果
type QueryAnalysisResult struct {
	// QueryType 查询类型 (keyword, semantic, hybrid)
	QueryType string
	
	// Keywords 关键词列表
	Keywords []string
	
	// KeywordWeight 推荐的关键词权重 (0-1)
	KeywordWeight float64
	
	// VectorWeight 推荐的向量权重 (0-1)
	VectorWeight float64
	
	// IsTCMQuery 是否为中医相关查询
	IsTCMQuery bool
	
	// DomainSpecific 领域特定信息
	DomainSpecific map[string]interface{}
}

// WeightAdjuster 权重调整器接口
type WeightAdjuster interface {
	// AdjustWeights 根据查询和历史数据调整混合检索权重
	AdjustWeights(ctx context.Context, query string, options *models.HybridSearchOptions) error
}

// NewAdaptiveHybridSearcher 创建自适应混合检索器
func NewAdaptiveHybridSearcher(
	vectorSearcher VectorSearcher,
	keywordSearcher KeywordSearcher,
	queryAnalyzer QueryAnalyzer,
	weightAdjuster WeightAdjuster,
	options models.HybridSearchOptions,
	logger utils.Logger,
) *AdaptiveHybridSearcher {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	// 设置默认值
	if options.VectorWeight <= 0 && options.KeywordWeight <= 0 {
		options.VectorWeight = 0.7
		options.KeywordWeight = 0.3
	}
	
	if options.TopK <= 0 {
		options.TopK = 10
	}
	
	if options.VectorTopK <= 0 {
		options.VectorTopK = options.TopK * 2
	}
	
	if options.KeywordTopK <= 0 {
		options.KeywordTopK = options.TopK * 2
	}
	
	return &AdaptiveHybridSearcher{
		vectorSearcher:        vectorSearcher,
		keywordSearcher:       keywordSearcher,
		queryAnalyzer:         queryAnalyzer,
		weightAdjuster:        weightAdjuster,
		logger:                logger,
		maxConcurrentRequests: 5,
		defaultOptions:        options,
	}
}

// Initialize 初始化混合检索器
func (s *AdaptiveHybridSearcher) Initialize(ctx context.Context) error {
	s.logger.Info("初始化自适应混合检索器")
	return nil
}

// Close 关闭混合检索器
func (s *AdaptiveHybridSearcher) Close() error {
	return nil
}

// Search 执行混合检索
func (s *AdaptiveHybridSearcher) Search(ctx context.Context, collectionName string, query string, options models.HybridSearchOptions) ([]models.Document, error) {
	startTime := time.Now()
	defer func() {
		s.logger.Debug("混合检索完成",
			"query", query,
			"collection", collectionName,
			"time_ms", time.Since(startTime).Milliseconds(),
		)
	}()
	
	// 合并选项
	opts := s.mergeOptions(options)
	
	// 分析查询
	if s.queryAnalyzer != nil {
		analysis, err := s.queryAnalyzer.Analyze(ctx, query)
		if err != nil {
			s.logger.Warn("查询分析失败", "error", err)
		} else {
			// 根据分析结果调整权重
			s.adjustWeightsByAnalysis(&opts, analysis)
			
			// 记录分析结果
			s.logger.Debug("查询分析结果", 
				"query_type", analysis.QueryType,
				"keywords", strings.Join(analysis.Keywords, ","),
				"vector_weight", analysis.VectorWeight,
				"keyword_weight", analysis.KeywordWeight,
				"is_tcm", analysis.IsTCMQuery,
			)
		}
	}
	
	// 如果配置了权重调整器，进一步调整权重
	if s.weightAdjuster != nil {
		if err := s.weightAdjuster.AdjustWeights(ctx, query, &opts); err != nil {
			s.logger.Warn("权重调整失败", "error", err)
		}
	}
	
	// 如果权重之和不为1，则归一化
	weightSum := opts.VectorWeight + opts.KeywordWeight
	if weightSum > 0 && math.Abs(weightSum-1.0) > 0.001 {
		opts.VectorWeight = opts.VectorWeight / weightSum
		opts.KeywordWeight = opts.KeywordWeight / weightSum
	}
	
	// 用于存储结果的通道
	vectorResultCh := make(chan []models.Document, 1)
	keywordResultCh := make(chan []models.Document, 1)
	vectorErrCh := make(chan error, 1)
	keywordErrCh := make(chan error, 1)
	
	// 向量检索
	if opts.VectorWeight > 0 {
		go func() {
			// 这里应执行向量检索，但在示例中我们模拟返回结果
			// 在实际实现中，应使用s.vectorSearcher执行检索
			vectorResults := []models.Document{}
			// 模拟向量检索错误
			vectorErrCh <- nil
			vectorResultCh <- vectorResults
		}()
	} else {
		vectorResultCh <- nil
		vectorErrCh <- nil
	}
	
	// 关键词检索
	if opts.KeywordWeight > 0 {
		go func() {
			// 这里应执行关键词检索，但在示例中我们模拟返回结果
			// 在实际实现中，应使用s.keywordSearcher执行检索
			keywordResults, err := s.keywordSearcher.Search(ctx, collectionName, query, opts.KeywordTopK, nil)
			keywordErrCh <- err
			keywordResultCh <- keywordResults
		}()
	} else {
		keywordResultCh <- nil
		keywordErrCh <- nil
	}
	
	// 等待结果
	vectorResults := <-vectorResultCh
	keywordResults := <-keywordResultCh
	vectorErr := <-vectorErrCh
	keywordErr := <-keywordErrCh
	
	// 检查错误
	if vectorErr != nil && keywordErr != nil {
		return nil, fmt.Errorf("向量检索和关键词检索均失败: %v, %v", vectorErr, keywordErr)
	}
	
	if vectorErr != nil && opts.VectorWeight > 0 {
		s.logger.Warn("向量检索失败，使用关键词检索结果", "error", vectorErr)
		if keywordResults != nil {
			return keywordResults, nil
		}
		return nil, vectorErr
	}
	
	if keywordErr != nil && opts.KeywordWeight > 0 {
		s.logger.Warn("关键词检索失败，使用向量检索结果", "error", keywordErr)
		if vectorResults != nil {
			return vectorResults, nil
		}
		return nil, keywordErr
	}
	
	// 合并结果
	mergedResults, err := s.mergeResults(vectorResults, keywordResults, opts)
	if err != nil {
		return nil, fmt.Errorf("合并结果失败: %w", err)
	}
	
	// 根据TopK限制结果数量
	if opts.TopK > 0 && len(mergedResults) > opts.TopK {
		mergedResults = mergedResults[:opts.TopK]
	}
	
	return mergedResults, nil
}

// 合并选项
func (s *AdaptiveHybridSearcher) mergeOptions(options models.HybridSearchOptions) models.HybridSearchOptions {
	result := s.defaultOptions
	
	if options.VectorWeight > 0 {
		result.VectorWeight = options.VectorWeight
	}
	
	if options.KeywordWeight > 0 {
		result.KeywordWeight = options.KeywordWeight
	}
	
	if options.TopK > 0 {
		result.TopK = options.TopK
	}
	
	if options.VectorTopK > 0 {
		result.VectorTopK = options.VectorTopK
	}
	
	if options.KeywordTopK > 0 {
		result.KeywordTopK = options.KeywordTopK
	}
	
	if options.RerankerEnabled {
		result.RerankerEnabled = true
	}
	
	if options.RerankerTopK > 0 {
		result.RerankerTopK = options.RerankerTopK
	}
	
	return result
}

// 根据查询分析结果调整权重
func (s *AdaptiveHybridSearcher) adjustWeightsByAnalysis(options *models.HybridSearchOptions, analysis QueryAnalysisResult) {
	switch analysis.QueryType {
	case "keyword":
		// 偏向关键词检索
		options.KeywordWeight = math.Max(options.KeywordWeight, 0.7)
		options.VectorWeight = 1.0 - options.KeywordWeight
	case "semantic":
		// 偏向语义检索
		options.VectorWeight = math.Max(options.VectorWeight, 0.7)
		options.KeywordWeight = 1.0 - options.VectorWeight
	case "hybrid":
		// 使用分析推荐的权重
		if analysis.VectorWeight > 0 && analysis.KeywordWeight > 0 {
			options.VectorWeight = analysis.VectorWeight
			options.KeywordWeight = analysis.KeywordWeight
		}
	}
	
	// 如果是中医查询，根据经验调整权重
	if analysis.IsTCMQuery {
		// 中医查询通常需要更多关键词匹配
		options.KeywordWeight = math.Max(options.KeywordWeight, 0.4)
		options.VectorWeight = 1.0 - options.KeywordWeight
	}
}

// 合并向量检索和关键词检索结果
func (s *AdaptiveHybridSearcher) mergeResults(
	vectorResults []models.Document,
	keywordResults []models.Document,
	options models.HybridSearchOptions,
) ([]models.Document, error) {
	// 如果只有一种类型的结果，直接返回
	if len(vectorResults) == 0 && len(keywordResults) == 0 {
		return nil, nil
	}
	
	if len(vectorResults) == 0 {
		return keywordResults, nil
	}
	
	if len(keywordResults) == 0 {
		return vectorResults, nil
	}
	
	// 创建文档ID到文档的映射
	docMap := make(map[string]*models.Document)
	
	// 添加向量结果
	for i := range vectorResults {
		doc := vectorResults[i]
		doc.Score = doc.Score * options.VectorWeight
		docMap[doc.ID] = &doc
	}
	
	// 添加或更新关键词结果
	for i := range keywordResults {
		doc := keywordResults[i]
		if existing, found := docMap[doc.ID]; found {
			// 如果文档已存在，更新分数
			existing.Score += doc.Score * options.KeywordWeight
			existing.KeywordScore = doc.Score
		} else {
			// 否则添加新文档
			doc.Score = doc.Score * options.KeywordWeight
			doc.KeywordScore = doc.Score
			docMap[doc.ID] = &doc
		}
	}
	
	// 转换回切片
	results := make([]models.Document, 0, len(docMap))
	for _, doc := range docMap {
		results = append(results, *doc)
	}
	
	// 根据分数排序
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})
	
	return results, nil
}

// SimpleQueryAnalyzer 简单查询分析器实现
type SimpleQueryAnalyzer struct {
	// 中医术语库
	tcmTerms []string
	
	// 停用词
	stopwords map[string]bool
}

// NewSimpleQueryAnalyzer 创建简单查询分析器
func NewSimpleQueryAnalyzer(tcmTerms []string, stopwords []string) *SimpleQueryAnalyzer {
	stopwordMap := make(map[string]bool)
	for _, word := range stopwords {
		stopwordMap[word] = true
	}
	
	return &SimpleQueryAnalyzer{
		tcmTerms:  tcmTerms,
		stopwords: stopwordMap,
	}
}

// Analyze 分析查询
func (a *SimpleQueryAnalyzer) Analyze(ctx context.Context, query string) (QueryAnalysisResult, error) {
	result := QueryAnalysisResult{
		QueryType:     "hybrid",
		Keywords:      []string{},
		KeywordWeight: 0.3,
		VectorWeight:  0.7,
		IsTCMQuery:    false,
		DomainSpecific: make(map[string]interface{}),
	}
	
	// 分词处理（示例实现，实际应使用适当的分词工具）
	words := strings.Fields(query)
	
	// 提取关键词
	for _, word := range words {
		word = strings.ToLower(strings.TrimSpace(word))
		if word == "" || a.stopwords[word] {
			continue
		}
		result.Keywords = append(result.Keywords, word)
	}
	
	// 检查是否为中医查询
	for _, term := range a.tcmTerms {
		if strings.Contains(strings.ToLower(query), strings.ToLower(term)) {
			result.IsTCMQuery = true
			result.DomainSpecific["tcm_term"] = term
			break
		}
	}
	
	// 确定查询类型
	if len(result.Keywords) <= 2 {
		// 短查询通常更语义化
		result.QueryType = "semantic"
		result.VectorWeight = 0.8
		result.KeywordWeight = 0.2
	} else if a.containsSpecialChars(query) || a.containsExactPhrases(query) {
		// 包含特殊字符或精确短语的查询更依赖关键词
		result.QueryType = "keyword"
		result.VectorWeight = 0.4
		result.KeywordWeight = 0.6
	} else if a.isQuestionQuery(query) {
		// 问题查询通常更语义化
		result.QueryType = "semantic"
		result.VectorWeight = 0.7
		result.KeywordWeight = 0.3
	}
	
	// 如果是中医查询，调整权重
	if result.IsTCMQuery {
		result.KeywordWeight = math.Max(result.KeywordWeight, 0.4)
		result.VectorWeight = 1.0 - result.KeywordWeight
	}
	
	return result, nil
}

// 检查查询是否包含特殊字符
func (a *SimpleQueryAnalyzer) containsSpecialChars(query string) bool {
	specialChars := []string{"\"", "+", "-", "&", "|", "!", "(", ")", "{", "}", "[", "]", "^", "~", "*", "?", ":"}
	for _, char := range specialChars {
		if strings.Contains(query, char) {
			return true
		}
	}
	return false
}

// 检查查询是否包含精确短语
func (a *SimpleQueryAnalyzer) containsExactPhrases(query string) bool {
	return strings.Contains(query, "\"")
}

// 检查是否为问题查询
func (a *SimpleQueryAnalyzer) isQuestionQuery(query string) bool {
	questionMarkers := []string{"?", "吗", "什么", "如何", "怎么", "为什么", "哪些", "是否", "能否"}
	for _, marker := range questionMarkers {
		if strings.Contains(query, marker) {
			return true
		}
	}
	return false
}

// SimpleWeightAdjuster 简单权重调整器实现
type SimpleWeightAdjuster struct {
	// 可以在这里添加学习历史等信息
}

// NewSimpleWeightAdjuster 创建简单权重调整器
func NewSimpleWeightAdjuster() *SimpleWeightAdjuster {
	return &SimpleWeightAdjuster{}
}

// AdjustWeights 调整权重
func (a *SimpleWeightAdjuster) AdjustWeights(ctx context.Context, query string, options *models.HybridSearchOptions) error {
	// 示例实现，实际应根据历史数据和学习结果进行调整
	// 这里只是简单地检查查询长度
	
	if len(query) < 10 {
		// 短查询更依赖向量检索
		options.VectorWeight = math.Max(options.VectorWeight, 0.7)
		options.KeywordWeight = 1.0 - options.VectorWeight
	} else if len(query) > 50 {
		// 长查询可能包含更多关键词信息
		options.KeywordWeight = math.Max(options.KeywordWeight, 0.4)
		options.VectorWeight = 1.0 - options.KeywordWeight
	}
	
	return nil
} 