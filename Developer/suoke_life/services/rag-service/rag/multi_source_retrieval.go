package rag

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// SourceType 数据源类型
type SourceType string

const (
	// SourceInternal 内部知识库
	SourceInternal SourceType = "internal"
	
	// SourceWeb 互联网搜索
	SourceWeb SourceType = "web"
	
	// SourceKnowledgeGraph 知识图谱
	SourceKnowledgeGraph SourceType = "knowledge_graph"
	
	// SourceStructuredData 结构化数据
	SourceStructuredData SourceType = "structured_data"
	
	// SourceExpertSystem 专家系统
	SourceExpertSystem SourceType = "expert_system"
)

// RetrievalSource 检索源接口
type RetrievalSource interface {
	// Retrieve 从数据源检索内容
	Retrieve(ctx context.Context, query string, options map[string]interface{}) ([]models.SearchResult, error)
	
	// GetSourceType 获取数据源类型
	GetSourceType() SourceType
	
	// GetSourceName 获取数据源名称
	GetSourceName() string
	
	// GetMaxResults 获取最大结果数
	GetMaxResults() int
	
	// SetMaxResults 设置最大结果数
	SetMaxResults(max int)
	
	// GetRelevanceThreshold 获取相关性阈值
	GetRelevanceThreshold() float64
	
	// SetRelevanceThreshold 设置相关性阈值
	SetRelevanceThreshold(threshold float64)
	
	// IsEnabled 是否启用此数据源
	IsEnabled() bool
	
	// SetEnabled 设置是否启用此数据源
	SetEnabled(enabled bool)
}

// SourcePriority 数据源优先级
type SourcePriority struct {
	// 数据源类型
	SourceType SourceType
	
	// 优先级权重 (0-1)
	Weight float64
	
	// 最大结果数量
	MaxResults int
	
	// 相关性阈值
	RelevanceThreshold float64
}

// MultiSourceRetrievalOptions 多源检索选项
type MultiSourceRetrievalOptions struct {
	// 查询文本
	Query string
	
	// 领域
	Domain string
	
	// 用户ID
	UserID string
	
	// 是否启用互联网搜索
	EnableWebSearch bool
	
	// 是否启用知识图谱
	EnableKnowledgeGraph bool
	
	// 是否强制刷新缓存
	ForceRefresh bool
	
	// 每个源的最大结果数
	MaxResultsPerSource int
	
	// 源优先级排序
	SourcePriorities []SourcePriority
	
	// 响应超时时间（毫秒）
	TimeoutMs int
	
	// 是否应用去重
	ApplyDeduplication bool
	
	// 去重阈值
	DeduplicationThreshold float64
	
	// 是否结果融合
	ApplyFusion bool
	
	// 是否应用重排序
	ApplyReranking bool
	
	// 额外选项
	ExtraOptions map[string]interface{}
}

// MultiSourceRetrievalResult 多源检索结果
type MultiSourceRetrievalResult struct {
	// 合并后的结果
	Results []models.SearchResult
	
	// 各源的原始结果
	SourceResults map[SourceType][]models.SearchResult
	
	// 获取各源结果的耗时（毫秒）
	SourceLatencies map[SourceType]int64
	
	// 总体耗时（毫秒）
	TotalLatencyMs int64
	
	// 查询
	Query string
	
	// 是否成功
	Success bool
	
	// 错误信息
	Error string
	
	// 统计信息
	Stats map[string]interface{}
}

// MultiSourceRetriever 多源检索器
type MultiSourceRetriever struct {
	// 日志器
	logger utils.Logger
	
	// 数据源列表
	sources map[SourceType][]RetrievalSource
	
	// 缓存
	cache utils.Cache
	
	// LLM服务
	llmService utils.LLMService
	
	// 默认选项
	defaultOptions MultiSourceRetrievalOptions
	
	// 互斥锁
	mu sync.RWMutex
}

// NewMultiSourceRetriever 创建多源检索器
func NewMultiSourceRetriever(logger utils.Logger, llmService utils.LLMService) *MultiSourceRetriever {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &MultiSourceRetriever{
		logger:   logger,
		sources:  make(map[SourceType][]RetrievalSource),
		cache:    utils.NewLRUCache(1000),
		llmService: llmService,
		defaultOptions: MultiSourceRetrievalOptions{
			EnableWebSearch:       true,
			EnableKnowledgeGraph:  true,
			ForceRefresh:          false,
			MaxResultsPerSource:   10,
			TimeoutMs:             5000,
			ApplyDeduplication:    true,
			DeduplicationThreshold: 0.85,
			ApplyFusion:           true,
			ApplyReranking:        true,
			SourcePriorities: []SourcePriority{
				{SourceType: SourceInternal, Weight: 0.7, MaxResults: 15, RelevanceThreshold: 0.6},
				{SourceType: SourceKnowledgeGraph, Weight: 0.6, MaxResults: 10, RelevanceThreshold: 0.65},
				{SourceType: SourceWeb, Weight: 0.5, MaxResults: 5, RelevanceThreshold: 0.7},
				{SourceType: SourceStructuredData, Weight: 0.4, MaxResults: 5, RelevanceThreshold: 0.75},
				{SourceType: SourceExpertSystem, Weight: 0.8, MaxResults: 3, RelevanceThreshold: 0.8},
			},
			ExtraOptions: make(map[string]interface{}),
		},
	}
}

// RegisterSource 注册数据源
func (r *MultiSourceRetriever) RegisterSource(source RetrievalSource) {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	sourceType := source.GetSourceType()
	
	// 初始化数据源类型的切片（如果不存在）
	if _, exists := r.sources[sourceType]; !exists {
		r.sources[sourceType] = make([]RetrievalSource, 0)
	}
	
	// 添加数据源
	r.sources[sourceType] = append(r.sources[sourceType], source)
	
	r.logger.Info("注册数据源", "type", sourceType, "name", source.GetSourceName())
}

// UnregisterSource 注销数据源
func (r *MultiSourceRetriever) UnregisterSource(sourceType SourceType, sourceName string) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	sources, exists := r.sources[sourceType]
	if !exists {
		return false
	}
	
	for i, source := range sources {
		if source.GetSourceName() == sourceName {
			// 移除数据源
			r.sources[sourceType] = append(sources[:i], sources[i+1:]...)
			r.logger.Info("注销数据源", "type", sourceType, "name", sourceName)
			return true
		}
	}
	
	return false
}

// SetDefaultOptions 设置默认选项
func (r *MultiSourceRetriever) SetDefaultOptions(options MultiSourceRetrievalOptions) {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	r.defaultOptions = options
}

// GetDefaultOptions 获取默认选项
func (r *MultiSourceRetriever) GetDefaultOptions() MultiSourceRetrievalOptions {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	// 复制一份返回，避免外部修改
	options := r.defaultOptions
	
	// 深复制切片和map
	if r.defaultOptions.SourcePriorities != nil {
		options.SourcePriorities = make([]SourcePriority, len(r.defaultOptions.SourcePriorities))
		copy(options.SourcePriorities, r.defaultOptions.SourcePriorities)
	}
	
	if r.defaultOptions.ExtraOptions != nil {
		options.ExtraOptions = make(map[string]interface{})
		for k, v := range r.defaultOptions.ExtraOptions {
			options.ExtraOptions[k] = v
		}
	}
	
	return options
}

// GetSources 获取所有数据源
func (r *MultiSourceRetriever) GetSources() map[SourceType][]RetrievalSource {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	// 复制一份返回，避免外部修改
	result := make(map[SourceType][]RetrievalSource)
	
	for sourceType, sources := range r.sources {
		result[sourceType] = make([]RetrievalSource, len(sources))
		copy(result[sourceType], sources)
	}
	
	return result
}

// Retrieve 执行多源检索
func (r *MultiSourceRetriever) Retrieve(ctx context.Context, options MultiSourceRetrievalOptions) (*MultiSourceRetrievalResult, error) {
	startTime := time.Now()
	
	// 合并默认选项和传入选项
	opts := r.mergeOptions(options)
	
	// 检查缓存
	if !opts.ForceRefresh {
		cacheKey := r.getCacheKey(opts)
		if cached, found := r.cache.Get(cacheKey); found {
			if result, ok := cached.(*MultiSourceRetrievalResult); ok {
				return result, nil
			}
		}
	}
	
	// 创建结果结构
	result := &MultiSourceRetrievalResult{
		Results:        make([]models.SearchResult, 0),
		SourceResults:  make(map[SourceType][]models.SearchResult),
		SourceLatencies: make(map[SourceType]int64),
		Query:          opts.Query,
		Success:        true,
		Stats:          make(map[string]interface{}),
	}
	
	// 创建超时上下文
	timeout := time.Duration(opts.TimeoutMs) * time.Millisecond
	ctxWithTimeout, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()
	
	// 按优先级排序数据源
	prioritizedSources := r.getPrioritizedSources(opts)
	
	// 存储错误通道
	errChan := make(chan error, len(prioritizedSources))
	
	// 存储结果通道
	resultChan := make(chan struct {
		sourceType SourceType
		results    []models.SearchResult
		latency    int64
	}, len(prioritizedSources))
	
	// 创建等待组
	var wg sync.WaitGroup
	
	// 从每个数据源检索
	for _, sourcePriority := range prioritizedSources {
		sourceType := sourcePriority.SourceType
		sources, exists := r.sources[sourceType]
		
		if !exists || len(sources) == 0 {
			continue
		}
		
		// 根据数据源类型跳过禁用的类型
		if sourceType == SourceWeb && !opts.EnableWebSearch {
			continue
		}
		
		if sourceType == SourceKnowledgeGraph && !opts.EnableKnowledgeGraph {
			continue
		}
		
		// 为每个数据源启动goroutine
		for _, source := range sources {
			if !source.IsEnabled() {
				continue
			}
			
			wg.Add(1)
			
			go func(src RetrievalSource, srcType SourceType, priority SourcePriority) {
				defer wg.Done()
				
				// 应用数据源特定的设置
				originalMaxResults := src.GetMaxResults()
				originalThreshold := src.GetRelevanceThreshold()
				
				if priority.MaxResults > 0 {
					src.SetMaxResults(priority.MaxResults)
				}
				
				if priority.RelevanceThreshold > 0 {
					src.SetRelevanceThreshold(priority.RelevanceThreshold)
				}
				
				// 创建检索选项
				retrieveOptions := map[string]interface{}{
					"domain":      opts.Domain,
					"user_id":     opts.UserID,
					"force_refresh": opts.ForceRefresh,
				}
				
				// 添加额外选项
				for k, v := range opts.ExtraOptions {
					retrieveOptions[k] = v
				}
				
				// 检索结果
				sourceStartTime := time.Now()
				sourceResults, err := src.Retrieve(ctxWithTimeout, opts.Query, retrieveOptions)
				sourceLatency := time.Since(sourceStartTime).Milliseconds()
				
				// 恢复原始设置
				src.SetMaxResults(originalMaxResults)
				src.SetRelevanceThreshold(originalThreshold)
				
				if err != nil {
					errChan <- fmt.Errorf("从 %s(%s) 检索失败: %w", src.GetSourceName(), srcType, err)
					return
				}
				
				// 发送结果
				resultChan <- struct {
					sourceType SourceType
					results    []models.SearchResult
					latency    int64
				}{
					sourceType: srcType,
					results:    sourceResults,
					latency:    sourceLatency,
				}
			}(source, sourceType, sourcePriority)
		}
	}
	
	// 等待所有goroutine完成或上下文取消
	go func() {
		wg.Wait()
		close(resultChan)
		close(errChan)
	}()
	
	// 收集结果
	for {
		select {
		case <-ctxWithTimeout.Done():
			// 上下文取消或超时
			if ctxWithTimeout.Err() == context.DeadlineExceeded {
				result.Error = "检索超时"
			} else {
				result.Error = "检索被取消"
			}
			result.Success = false
			
			// 返回已收集的结果
			result.TotalLatencyMs = time.Since(startTime).Milliseconds()
			r.processResults(result, opts)
			return result, ctxWithTimeout.Err()
			
		case sourceResult, ok := <-resultChan:
			if !ok {
				// 通道已关闭，所有结果已处理
				goto ProcessResults
			}
			
			// 存储源结果
			result.SourceResults[sourceResult.sourceType] = sourceResult.results
			result.SourceLatencies[sourceResult.sourceType] = sourceResult.latency
			
		case err, ok := <-errChan:
			if !ok {
				// 通道已关闭，所有错误已处理
				continue
			}
			
			// 记录错误但继续处理
			r.logger.Warn("检索错误", "error", err)
		}
	}
	
ProcessResults:
	// 处理结果（融合、去重、重排序）
	r.processResults(result, opts)
	
	// 计算总耗时
	result.TotalLatencyMs = time.Since(startTime).Milliseconds()
	
	// 缓存结果
	if result.Success {
		cacheKey := r.getCacheKey(opts)
		r.cache.Set(cacheKey, result, time.Hour)
	}
	
	return result, nil
}

// mergeOptions 合并默认选项和传入选项
func (r *MultiSourceRetriever) mergeOptions(opts MultiSourceRetrievalOptions) MultiSourceRetrievalOptions {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	// 开始使用默认选项
	result := r.defaultOptions
	
	// 覆盖传入的非零值
	if opts.Query != "" {
		result.Query = opts.Query
	}
	
	if opts.Domain != "" {
		result.Domain = opts.Domain
	}
	
	if opts.UserID != "" {
		result.UserID = opts.UserID
	}
	
	// 布尔值需要特殊处理，只有当选项明确设置时才覆盖
	if opts.ForceRefresh {
		result.ForceRefresh = true
	}
	
	// 覆盖EnableWebSearch
	result.EnableWebSearch = opts.EnableWebSearch
	
	// 覆盖EnableKnowledgeGraph
	result.EnableKnowledgeGraph = opts.EnableKnowledgeGraph
	
	// 整数值需要检查是否为默认值
	if opts.MaxResultsPerSource > 0 {
		result.MaxResultsPerSource = opts.MaxResultsPerSource
	}
	
	if opts.TimeoutMs > 0 {
		result.TimeoutMs = opts.TimeoutMs
	}
	
	// 浮点数值
	if opts.DeduplicationThreshold > 0 {
		result.DeduplicationThreshold = opts.DeduplicationThreshold
	}
	
	// 数组需要检查是否为nil
	if opts.SourcePriorities != nil && len(opts.SourcePriorities) > 0 {
		result.SourcePriorities = opts.SourcePriorities
	}
	
	// 合并额外选项
	if opts.ExtraOptions != nil {
		for k, v := range opts.ExtraOptions {
			result.ExtraOptions[k] = v
		}
	}
	
	return result
}

// getCacheKey 生成缓存键
func (r *MultiSourceRetriever) getCacheKey(opts MultiSourceRetrievalOptions) string {
	return fmt.Sprintf("multisource:%s:%s:%s", opts.Query, opts.Domain, opts.UserID)
}

// getPrioritizedSources 获取优先级排序的数据源
func (r *MultiSourceRetriever) getPrioritizedSources(opts MultiSourceRetrievalOptions) []SourcePriority {
	// 复制优先级列表
	priorities := make([]SourcePriority, len(opts.SourcePriorities))
	copy(priorities, opts.SourcePriorities)
	
	// 根据权重排序
	sort.Slice(priorities, func(i, j int) bool {
		return priorities[i].Weight > priorities[j].Weight
	})
	
	return priorities
}

// processResults 处理检索结果
func (r *MultiSourceRetriever) processResults(result *MultiSourceRetrievalResult, opts MultiSourceRetrievalOptions) {
	// 统计各源的结果数量
	resultCounts := make(map[SourceType]int)
	for sourceType, sourceResults := range result.SourceResults {
		resultCounts[sourceType] = len(sourceResults)
	}
	result.Stats["source_result_counts"] = resultCounts
	
	// 合并所有结果
	allResults := make([]models.SearchResult, 0)
	for sourceType, sourceResults := range result.SourceResults {
		for _, res := range sourceResults {
			// 标记结果来源
			if res.Metadata.Properties == nil {
				res.Metadata.Properties = make(map[string]interface{})
			}
			res.Metadata.Properties["source_type"] = string(sourceType)
			
			// 根据源类型调整分数
			for _, priority := range opts.SourcePriorities {
				if priority.SourceType == sourceType {
					res.Score *= priority.Weight
					break
				}
			}
			
			allResults = append(allResults, res)
		}
	}
	
	// 去重
	if opts.ApplyDeduplication {
		allResults = r.deduplicateResults(allResults, opts.DeduplicationThreshold)
	}
	
	// 排序
	r.sortResults(allResults)
	
	// 如果启用了融合
	if opts.ApplyFusion {
		allResults = r.fuseResults(allResults, opts)
	}
	
	// 如果启用了重排序且有LLM服务
	if opts.ApplyReranking && r.llmService != nil {
		allResults = r.rerankResults(context.Background(), allResults, opts.Query)
	}
	
	// 更新结果
	result.Results = allResults
	result.Stats["total_results"] = len(allResults)
}

// deduplicateResults 去重结果
func (r *MultiSourceRetriever) deduplicateResults(results []models.SearchResult, threshold float64) []models.SearchResult {
	if len(results) <= 1 {
		return results
	}
	
	// 复制结果切片
	deduped := make([]models.SearchResult, 0, len(results))
	
	// 使用map跟踪已添加的结果
	added := make(map[string]bool)
	
	for _, result := range results {
		isDuplicate := false
		
		// 检查是否重复（根据ID）
		if added[result.ID] {
			continue
		}
		
		// 检查是否与已添加结果相似
		for _, existing := range deduped {
			similarity := utils.TextSimilarity(result.Content, existing.Content)
			if similarity >= threshold {
				isDuplicate = true
				
				// 如果新结果分数更高，替换旧结果
				if result.Score > existing.Score {
					// 从已添加集合中移除旧结果
					for i, item := range deduped {
						if item.ID == existing.ID {
							deduped[i] = result
							break
						}
					}
					
					added[result.ID] = true
					added[existing.ID] = false
				}
				
				break
			}
		}
		
		// 如果不是重复，添加到结果
		if !isDuplicate {
			deduped = append(deduped, result)
			added[result.ID] = true
		}
	}
	
	return deduped
}

// sortResults 排序结果
func (r *MultiSourceRetriever) sortResults(results []models.SearchResult) {
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})
}

// fuseResults 融合结果
func (r *MultiSourceRetriever) fuseResults(results []models.SearchResult, opts MultiSourceRetrievalOptions) []models.SearchResult {
	// 这里可以实现更复杂的融合逻辑，如RRF或CombSUM
	// 当前简单返回排序后的结果
	return results
}

// rerankResults 重排序结果
func (r *MultiSourceRetriever) rerankResults(ctx context.Context, results []models.SearchResult, query string) []models.SearchResult {
	if r.llmService == nil || len(results) <= 1 {
		return results
	}
	
	// 对结果进行重排序，这里只提供简化实现
	// 实际应用中可以使用更复杂的重排序模型
	
	return results
}

// WebSearchSource 互联网搜索源
type WebSearchSource struct {
	name               string
	searchService      utils.WebSearchService
	logger             utils.Logger
	maxResults         int
	relevanceThreshold float64
	enabled            bool
	webAPIConfig       map[string]interface{}
}

// NewWebSearchSource 创建互联网搜索源
func NewWebSearchSource(name string, searchService utils.WebSearchService, logger utils.Logger) *WebSearchSource {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &WebSearchSource{
		name:               name,
		searchService:      searchService,
		logger:             logger,
		maxResults:         10,
		relevanceThreshold: 0.5,
		enabled:            true,
		webAPIConfig:       make(map[string]interface{}),
	}
}

// GetSourceType 获取数据源类型
func (s *WebSearchSource) GetSourceType() SourceType {
	return SourceWeb
}

// GetSourceName 获取数据源名称
func (s *WebSearchSource) GetSourceName() string {
	return s.name
}

// GetMaxResults 获取最大结果数
func (s *WebSearchSource) GetMaxResults() int {
	return s.maxResults
}

// SetMaxResults 设置最大结果数
func (s *WebSearchSource) SetMaxResults(max int) {
	if max > 0 {
		s.maxResults = max
	}
}

// GetRelevanceThreshold 获取相关性阈值
func (s *WebSearchSource) GetRelevanceThreshold() float64 {
	return s.relevanceThreshold
}

// SetRelevanceThreshold 设置相关性阈值
func (s *WebSearchSource) SetRelevanceThreshold(threshold float64) {
	if threshold > 0 {
		s.relevanceThreshold = threshold
	}
}

// IsEnabled 是否启用
func (s *WebSearchSource) IsEnabled() bool {
	return s.enabled
}

// SetEnabled 设置是否启用
func (s *WebSearchSource) SetEnabled(enabled bool) {
	s.enabled = enabled
}

// Retrieve 从互联网检索内容
func (s *WebSearchSource) Retrieve(ctx context.Context, query string, options map[string]interface{}) ([]models.SearchResult, error) {
	if s.searchService == nil {
		return nil, fmt.Errorf("搜索服务未初始化")
	}
	
	// 准备搜索选项
	searchOpts := map[string]interface{}{
		"max_results": s.maxResults,
	}
	
	// 添加额外选项
	for k, v := range options {
		searchOpts[k] = v
	}
	
	// 执行搜索
	searchResults, err := s.searchService.Search(ctx, query, searchOpts)
	if err != nil {
		return nil, fmt.Errorf("互联网搜索失败: %w", err)
	}
	
	// 转换为标准搜索结果
	results := make([]models.SearchResult, 0, len(searchResults))
	for _, res := range searchResults {
		// 检查相关性是否达到阈值
		if res.Score < s.relevanceThreshold {
			continue
		}
		
		// 转换为标准结果格式
		result := models.SearchResult{
			ID:      res.ID,
			Content: res.Content,
			Source:  res.Source,
			Score:   res.Score,
			Metadata: models.DocumentMetadata{
				Properties: map[string]interface{}{
					"web_search_source": s.name,
					"url":               res.Source,
					"retrieved_at":      time.Now(),
				},
			},
		}
		
		// 添加额外元数据
		if res.Metadata != nil {
			for k, v := range res.Metadata {
				result.Metadata.Properties[k] = v
			}
		}
		
		results = append(results, result)
	}
	
	s.logger.Debug("互联网搜索完成", "source", s.name, "query", query, "results", len(results))
	return results, nil
} 