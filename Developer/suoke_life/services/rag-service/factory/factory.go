package factory

import (
	"context"
	"fmt"
	"sync"

	"github.com/suoke/suoke_life/services/rag-service/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
	"github.com/suoke/suoke_life/services/rag-service/rag"
	"github.com/suoke/suoke_life/services/rag-service/reranker"
)

// ComponentFactory 组件工厂，负责创建和管理各种组件
type ComponentFactory struct {
	// 可用的嵌入器
	embedders map[string]embeddings.Embedder
	
	// 可用的重排序器
	rerankers map[string]reranker.Reranker
	
	// 可用的混合检索器
	hybridSearchers map[string]rag.HybridSearcher
	
	// 可用的查询分析器
	queryAnalyzers map[string]rag.QueryAnalyzer
	
	// 创建器锁
	mu sync.RWMutex
	
	// 日志器
	logger utils.Logger
	
	// 组件配置
	config map[string]interface{}
}

// NewComponentFactory 创建组件工厂
func NewComponentFactory(config map[string]interface{}, logger utils.Logger) *ComponentFactory {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &ComponentFactory{
		embedders:       make(map[string]embeddings.Embedder),
		rerankers:       make(map[string]reranker.Reranker),
		hybridSearchers: make(map[string]rag.HybridSearcher),
		queryAnalyzers:  make(map[string]rag.QueryAnalyzer),
		logger:          logger,
		config:          config,
	}
}

// RegisterEmbedder 注册嵌入器
func (f *ComponentFactory) RegisterEmbedder(name string, embedder embeddings.Embedder) {
	f.mu.Lock()
	defer f.mu.Unlock()
	
	f.embedders[name] = embedder
	f.logger.Debug("注册嵌入器", "name", name)
}

// RegisterReranker 注册重排序器
func (f *ComponentFactory) RegisterReranker(name string, reranker reranker.Reranker) {
	f.mu.Lock()
	defer f.mu.Unlock()
	
	f.rerankers[name] = reranker
	f.logger.Debug("注册重排序器", "name", name)
}

// RegisterHybridSearcher 注册混合检索器
func (f *ComponentFactory) RegisterHybridSearcher(name string, searcher rag.HybridSearcher) {
	f.mu.Lock()
	defer f.mu.Unlock()
	
	f.hybridSearchers[name] = searcher
	f.logger.Debug("注册混合检索器", "name", name)
}

// RegisterQueryAnalyzer 注册查询分析器
func (f *ComponentFactory) RegisterQueryAnalyzer(name string, analyzer rag.QueryAnalyzer) {
	f.mu.Lock()
	defer f.mu.Unlock()
	
	f.queryAnalyzers[name] = analyzer
	f.logger.Debug("注册查询分析器", "name", name)
}

// GetEmbedder 获取嵌入器
func (f *ComponentFactory) GetEmbedder(name string) (embeddings.Embedder, error) {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	if embedder, ok := f.embedders[name]; ok {
		return embedder, nil
	}
	
	return nil, fmt.Errorf("未找到嵌入器: %s", name)
}

// GetReranker 获取重排序器
func (f *ComponentFactory) GetReranker(name string) (reranker.Reranker, error) {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	if reranker, ok := f.rerankers[name]; ok {
		return reranker, nil
	}
	
	return nil, fmt.Errorf("未找到重排序器: %s", name)
}

// GetHybridSearcher 获取混合检索器
func (f *ComponentFactory) GetHybridSearcher(name string) (rag.HybridSearcher, error) {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	if searcher, ok := f.hybridSearchers[name]; ok {
		return searcher, nil
	}
	
	return nil, fmt.Errorf("未找到混合检索器: %s", name)
}

// GetQueryAnalyzer 获取查询分析器
func (f *ComponentFactory) GetQueryAnalyzer(name string) (rag.QueryAnalyzer, error) {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	if analyzer, ok := f.queryAnalyzers[name]; ok {
		return analyzer, nil
	}
	
	return nil, fmt.Errorf("未找到查询分析器: %s", name)
}

// ListEmbedders 列出所有嵌入器
func (f *ComponentFactory) ListEmbedders() []string {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	names := make([]string, 0, len(f.embedders))
	for name := range f.embedders {
		names = append(names, name)
	}
	
	return names
}

// ListRerankers 列出所有重排序器
func (f *ComponentFactory) ListRerankers() []string {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	names := make([]string, 0, len(f.rerankers))
	for name := range f.rerankers {
		names = append(names, name)
	}
	
	return names
}

// ListHybridSearchers 列出所有混合检索器
func (f *ComponentFactory) ListHybridSearchers() []string {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	names := make([]string, 0, len(f.hybridSearchers))
	for name := range f.hybridSearchers {
		names = append(names, name)
	}
	
	return names
}

// ListQueryAnalyzers 列出所有查询分析器
func (f *ComponentFactory) ListQueryAnalyzers() []string {
	f.mu.RLock()
	defer f.mu.RUnlock()
	
	names := make([]string, 0, len(f.queryAnalyzers))
	for name := range f.queryAnalyzers {
		names = append(names, name)
	}
	
	return names
}

// CreateDefaultComponents 创建默认组件
func (f *ComponentFactory) CreateDefaultComponents(ctx context.Context) error {
	// 创建默认嵌入器
	if err := f.createDefaultEmbedders(ctx); err != nil {
		return fmt.Errorf("创建默认嵌入器失败: %w", err)
	}
	
	// 创建默认重排序器
	if err := f.createDefaultRerankers(ctx); err != nil {
		return fmt.Errorf("创建默认重排序器失败: %w", err)
	}
	
	// 创建默认混合检索器
	if err := f.createDefaultHybridSearchers(ctx); err != nil {
		return fmt.Errorf("创建默认混合检索器失败: %w", err)
	}
	
	// 创建默认查询分析器
	if err := f.createDefaultQueryAnalyzers(ctx); err != nil {
		return fmt.Errorf("创建默认查询分析器失败: %w", err)
	}
	
	return nil
}

// CreateCrossEncoderReranker 创建跨编码器重排序器
func (f *ComponentFactory) CreateCrossEncoderReranker(ctx context.Context, name string, modelName string, endpoint string, apiKey string, options reranker.RerankerOptions) (reranker.Reranker, error) {
	reranker := reranker.NewCrossEncoderReranker(modelName, endpoint, apiKey, options, f.logger)
	
	// 如果配置了中医术语库路径
	if tcmTermLibraryPath, ok := f.config["tcm_term_library"].(string); ok && options.TCMSpecific {
		reranker.SetTCMTermLibraryPath(tcmTermLibraryPath)
	}
	
	// 初始化重排序器
	if err := reranker.Initialize(ctx); err != nil {
		return nil, fmt.Errorf("初始化跨编码器重排序器失败: %w", err)
	}
	
	// 注册重排序器
	f.RegisterReranker(name, reranker)
	
	return reranker, nil
}

// CreateAdaptiveHybridSearcher 创建自适应混合检索器
func (f *ComponentFactory) CreateAdaptiveHybridSearcher(ctx context.Context, name string, vectorSearcher rag.VectorSearcher, keywordSearcher rag.KeywordSearcher, options map[string]interface{}) (rag.HybridSearcher, error) {
	// 创建查询分析器
	queryAnalyzer, err := f.createQueryAnalyzer(ctx, options)
	if err != nil {
		return nil, fmt.Errorf("创建查询分析器失败: %w", err)
	}
	
	// 创建权重调整器
	weightAdjuster := rag.NewSimpleWeightAdjuster()
	
	// 解析混合检索选项
	hybridOptions := f.parseHybridOptions(options)
	
	// 创建混合检索器
	searcher := rag.NewAdaptiveHybridSearcher(
		vectorSearcher,
		keywordSearcher,
		queryAnalyzer,
		weightAdjuster,
		hybridOptions,
		f.logger,
	)
	
	// 初始化
	if err := searcher.Initialize(ctx); err != nil {
		return nil, fmt.Errorf("初始化自适应混合检索器失败: %w", err)
	}
	
	// 注册
	f.RegisterHybridSearcher(name, searcher)
	
	return searcher, nil
}

// 创建默认嵌入器
func (f *ComponentFactory) createDefaultEmbedders(ctx context.Context) error {
	// 此处实现创建默认嵌入器的逻辑
	return nil
}

// 创建默认重排序器
func (f *ComponentFactory) createDefaultRerankers(ctx context.Context) error {
	// 此处实现创建默认重排序器的逻辑
	return nil
}

// 创建默认混合检索器
func (f *ComponentFactory) createDefaultHybridSearchers(ctx context.Context) error {
	// 此处实现创建默认混合检索器的逻辑
	return nil
}

// 创建默认查询分析器
func (f *ComponentFactory) createDefaultQueryAnalyzers(ctx context.Context) error {
	// 此处实现创建默认查询分析器的逻辑
	return nil
}

// 创建查询分析器
func (f *ComponentFactory) createQueryAnalyzer(ctx context.Context, options map[string]interface{}) (rag.QueryAnalyzer, error) {
	// 获取中医术语
	var tcmTerms []string
	if tcmTermsInterface, ok := options["tcm_terms"].([]interface{}); ok {
		for _, term := range tcmTermsInterface {
			if termStr, ok := term.(string); ok {
				tcmTerms = append(tcmTerms, termStr)
			}
		}
	}
	
	// 获取停用词
	var stopwords []string
	if stopwordsInterface, ok := options["stopwords"].([]interface{}); ok {
		for _, word := range stopwordsInterface {
			if wordStr, ok := word.(string); ok {
				stopwords = append(stopwords, wordStr)
			}
		}
	}
	
	// 创建简单查询分析器
	return rag.NewSimpleQueryAnalyzer(tcmTerms, stopwords), nil
}

// 解析混合检索选项
func (f *ComponentFactory) parseHybridOptions(options map[string]interface{}) rag.HybridSearchOptions {
	result := rag.HybridSearchOptions{}
	
	// 向量权重
	if weight, ok := options["vector_weight"].(float64); ok {
		result.VectorWeight = weight
	} else {
		result.VectorWeight = 0.7 // 默认值
	}
	
	// 关键词权重
	if weight, ok := options["keyword_weight"].(float64); ok {
		result.KeywordWeight = weight
	} else {
		result.KeywordWeight = 0.3 // 默认值
	}
	
	// 结果数量
	if topK, ok := options["top_k"].(int); ok {
		result.TopK = topK
	} else {
		result.TopK = 10 // 默认值
	}
	
	// 向量结果数量
	if vectorTopK, ok := options["vector_top_k"].(int); ok {
		result.VectorTopK = vectorTopK
	} else {
		result.VectorTopK = 20 // 默认值
	}
	
	// 关键词结果数量
	if keywordTopK, ok := options["keyword_top_k"].(int); ok {
		result.KeywordTopK = keywordTopK
	} else {
		result.KeywordTopK = 20 // 默认值
	}
	
	// 重排序相关
	if rerankerEnabled, ok := options["reranker_enabled"].(bool); ok {
		result.RerankerEnabled = rerankerEnabled
	}
	
	if rerankerTopK, ok := options["reranker_top_k"].(int); ok {
		result.RerankerTopK = rerankerTopK
	}
	
	return result
} 