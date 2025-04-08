package embeddings

import (
	"context"
	"fmt"
	"path/filepath"
	"strings"
	"sync"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// TCMEmbedder 中医领域特化嵌入器
type TCMEmbedder struct {
	// 基础嵌入器
	baseEmbedder Embedder
	
	// 微调模型路径
	fineTunedModelPath string
	
	// 中医术语处理器
	terminologyProcessor *utils.TCMTerminologyProcessor
	
	// 术语表
	terminology map[string]string
	
	// 中医概念向量映射
	conceptVectors map[string][]float32
	
	// 日志器
	logger utils.Logger
	
	// 嵌入向量维度
	dimensions int
	
	// 模型名称
	modelName string
	
	// 缓存
	cache utils.Cache
	
	// 互斥锁
	mu sync.RWMutex
}

// NewTCMEmbedder 创建中医领域特化嵌入器
func NewTCMEmbedder(baseEmbedder Embedder, modelPath string, logger utils.Logger) *TCMEmbedder {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &TCMEmbedder{
		baseEmbedder:         baseEmbedder,
		fineTunedModelPath:   filepath.Join(modelPath, "tcm_embedding"),
		terminologyProcessor: nil, // 将在Initialize中初始化
		terminology:          make(map[string]string),
		conceptVectors:       make(map[string][]float32),
		logger:               logger,
		dimensions:           baseEmbedder.Dimensions(),
		modelName:            fmt.Sprintf("tcm-specialized-%s", baseEmbedder.Name()),
		cache:                utils.NewLRUCache(1000),
	}
}

// Initialize 初始化嵌入模型
func (e *TCMEmbedder) Initialize(ctx context.Context) error {
	// 初始化基础嵌入器
	if err := e.baseEmbedder.Initialize(ctx); err != nil {
		return fmt.Errorf("初始化基础嵌入器失败: %w", err)
	}
	
	// 初始化术语处理器
	processor, err := utils.NewTCMTerminologyProcessor(
		filepath.Join(e.fineTunedModelPath, "terminology.json"),
		e.logger,
	)
	if err != nil {
		e.logger.Warn("初始化中医术语处理器失败，将使用基础嵌入功能", "error", err)
	} else {
		e.terminologyProcessor = processor
		e.terminology = processor.GetTerminologyMap()
	}
	
	// 加载预计算的中医概念向量
	if err := e.loadConceptVectors(); err != nil {
		e.logger.Warn("加载中医概念向量失败", "error", err)
	}
	
	e.logger.Info("初始化中医领域特化嵌入器完成")
	return nil
}

// 加载预计算的中医概念向量
func (e *TCMEmbedder) loadConceptVectors() error {
	conceptsPath := filepath.Join(e.fineTunedModelPath, "concept_vectors.json")
	
	vectors, err := utils.LoadEmbeddingVectors(conceptsPath)
	if err != nil {
		return err
	}
	
	e.mu.Lock()
	defer e.mu.Unlock()
	
	e.conceptVectors = vectors
	e.logger.Info("加载中医概念向量完成", "count", len(vectors))
	
	return nil
}

// Name 返回嵌入模型名称
func (e *TCMEmbedder) Name() string {
	return e.modelName
}

// Dimensions 返回嵌入向量维度
func (e *TCMEmbedder) Dimensions() int {
	return e.dimensions
}

// Close 关闭嵌入模型
func (e *TCMEmbedder) Close() error {
	return e.baseEmbedder.Close()
}

// EmbedQuery 对查询文本进行嵌入
func (e *TCMEmbedder) EmbedQuery(ctx context.Context, query string) ([]float32, error) {
	// 检查缓存
	if cached, found := e.cache.Get(fmt.Sprintf("query:%s", query)); found {
		if embedding, ok := cached.([]float32); ok {
			return embedding, nil
		}
	}
	
	// 中医术语处理
	enhancedQuery := query
	if e.terminologyProcessor != nil {
		processed, keywords := e.terminologyProcessor.ProcessQuery(query)
		if processed != query {
			e.logger.Debug("查询经过中医术语处理", 
				"original", query, 
				"processed", processed,
				"keywords", keywords)
			enhancedQuery = processed
		}
	}
	
	// 使用基础嵌入器生成嵌入向量
	baseEmbedding, err := e.baseEmbedder.EmbedQuery(ctx, enhancedQuery)
	if err != nil {
		return nil, fmt.Errorf("基础嵌入失败: %w", err)
	}
	
	// 增强嵌入向量
	finalEmbedding := e.enhanceEmbedding(baseEmbedding, query)
	
	// 缓存结果
	e.cache.Set(fmt.Sprintf("query:%s", query), finalEmbedding, 0)
	
	return finalEmbedding, nil
}

// EmbedDocuments 对多个文档进行嵌入
func (e *TCMEmbedder) EmbedDocuments(ctx context.Context, documents []string) ([][]float32, error) {
	// 检查是否有可用的缓存结果
	cachedResults := make([][]float32, len(documents))
	remainingDocs := make([]string, 0)
	remainingIndexes := make([]int, 0)
	
	for i, doc := range documents {
		cacheKey := fmt.Sprintf("doc:%s", utils.MD5(doc))
		if cached, found := e.cache.Get(cacheKey); found {
			if embedding, ok := cached.([]float32); ok {
				cachedResults[i] = embedding
				continue
			}
		}
		remainingDocs = append(remainingDocs, doc)
		remainingIndexes = append(remainingIndexes, i)
	}
	
	// 如果所有文档都在缓存中找到，直接返回
	if len(remainingDocs) == 0 {
		return cachedResults, nil
	}
	
	// 中医术语处理
	enhancedDocs := make([]string, len(remainingDocs))
	for i, doc := range remainingDocs {
		enhancedDocs[i] = doc
		if e.terminologyProcessor != nil {
			processed, _ := e.terminologyProcessor.ProcessDocument(doc)
			if processed != doc {
				enhancedDocs[i] = processed
			}
		}
	}
	
	// 使用基础嵌入器生成嵌入向量
	baseEmbeddings, err := e.baseEmbedder.EmbedDocuments(ctx, enhancedDocs)
	if err != nil {
		return nil, fmt.Errorf("基础嵌入失败: %w", err)
	}
	
	// 增强每个嵌入向量并存入缓存
	for i, baseEmbedding := range baseEmbeddings {
		docIndex := remainingIndexes[i]
		finalEmbedding := e.enhanceEmbedding(baseEmbedding, remainingDocs[i])
		cachedResults[docIndex] = finalEmbedding
		
		// 缓存结果
		cacheKey := fmt.Sprintf("doc:%s", utils.MD5(remainingDocs[i]))
		e.cache.Set(cacheKey, finalEmbedding, 0)
	}
	
	return cachedResults, nil
}

// enhanceEmbedding 增强基础嵌入向量以适应中医领域
func (e *TCMEmbedder) enhanceEmbedding(baseEmbedding []float32, text string) []float32 {
	// 克隆基础嵌入向量
	enhancedEmbedding := make([]float32, len(baseEmbedding))
	copy(enhancedEmbedding, baseEmbedding)
	
	// 提取文本中的中医概念
	e.mu.RLock()
	defer e.mu.RUnlock()
	
	// 如果没有概念向量数据，直接返回基础嵌入
	if len(e.conceptVectors) == 0 {
		return baseEmbedding
	}
	
	// 查找文本中的中医概念并增强相应的向量维度
	for concept, vector := range e.conceptVectors {
		if strings.Contains(text, concept) {
			// 根据概念向量对嵌入向量进行增强
			for i := 0; i < len(enhancedEmbedding) && i < len(vector); i++ {
				// 使用加权混合增强，保留原向量特性
				enhancedEmbedding[i] = enhancedEmbedding[i]*0.7 + vector[i]*0.3
			}
		}
	}
	
	// 向量归一化
	utils.NormalizeVector(enhancedEmbedding)
	
	return enhancedEmbedding
}

// AnalyzeTerms 分析文本中的中医术语
func (e *TCMEmbedder) AnalyzeTerms(text string) map[string]string {
	if e.terminologyProcessor == nil {
		return make(map[string]string)
	}
	
	return e.terminologyProcessor.ExtractTerms(text)
}

// GetDomainKeywords 获取文本中的领域关键词
func (e *TCMEmbedder) GetDomainKeywords(text string) []string {
	if e.terminologyProcessor == nil {
		return nil
	}
	
	_, keywords := e.terminologyProcessor.ProcessQuery(text)
	return keywords
}

// EnhanceMetadata 增强文档元数据
func (e *TCMEmbedder) EnhanceMetadata(ctx context.Context, metadata *models.DocumentMetadata, text string) {
	if metadata.Properties == nil {
		metadata.Properties = make(map[string]interface{})
	}
	
	// 添加领域
	metadata.Properties["domain"] = "tcm"
	
	// 提取中医术语
	if e.terminologyProcessor != nil {
		terms := e.terminologyProcessor.ExtractTerms(text)
		if len(terms) > 0 {
			metadata.Properties["tcm_terms"] = terms
		}
		
		// 检测中医证型
		patterns := e.terminologyProcessor.DetectPatterns(text)
		if len(patterns) > 0 {
			metadata.Properties["tcm_patterns"] = patterns
		}
		
		// 检测中医方剂
		formulas := e.terminologyProcessor.DetectFormulas(text)
		if len(formulas) > 0 {
			metadata.Properties["tcm_formulas"] = formulas
		}
	}
} 