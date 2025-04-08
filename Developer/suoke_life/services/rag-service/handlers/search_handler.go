package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/factory"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
	"github.com/suoke/suoke_life/services/rag-service/rag"
)

// SearchHandler 搜索处理器
type SearchHandler struct {
	// 组件工厂
	factory *factory.ComponentFactory
	
	// 日志器
	logger utils.Logger
	
	// 缓存管理器
	cacheManager utils.CacheManager
	
	// 超时时间
	timeout time.Duration
}

// SearchRequest 搜索请求
type SearchRequest struct {
	// 查询文本
	Query string `json:"query" binding:"required"`
	
	// 返回结果数量
	TopK int `json:"top_k,omitempty"`
	
	// 用户ID
	UserID string `json:"user_id,omitempty"`
	
	// 查询领域
	Domain string `json:"domain,omitempty"`
	
	// 是否使用混合搜索
	UseHybrid bool `json:"use_hybrid,omitempty"`
	
	// 是否使用重排序
	UseRerank bool `json:"use_rerank,omitempty"`
	
	// 是否使用缓存
	UseCache bool `json:"use_cache,omitempty"`
	
	// 中医专用查询选项
	TCMOptions *TCMSearchOptions `json:"tcm_options,omitempty"`
	
	// 多模态搜索选项
	MultimodalOptions *MultimodalOptions `json:"multimodal_options,omitempty"`
	
	// 额外选项
	ExtraOptions map[string]interface{} `json:"extra_options,omitempty"`
}

// TCMSearchOptions 中医搜索选项
type TCMSearchOptions struct {
	// 症状
	Symptoms []string `json:"symptoms,omitempty"`
	
	// 舌诊信息
	TongueInfo map[string]string `json:"tongue_info,omitempty"`
	
	// 面诊信息
	FaceInfo map[string]string `json:"face_info,omitempty"`
	
	// 脉诊信息
	PulseInfo map[string]string `json:"pulse_info,omitempty"`
	
	// 其他四诊信息
	OtherInfo map[string]string `json:"other_info,omitempty"`
}

// MultimodalOptions 多模态搜索选项
type MultimodalOptions struct {
	// 图像URL
	ImageURLs []string `json:"image_urls,omitempty"`
	
	// 音频URL
	AudioURLs []string `json:"audio_urls,omitempty"`
	
	// 多模态权重 (0-1)
	Weight float64 `json:"weight,omitempty"`
}

// SearchResponse 搜索响应
type SearchResponse struct {
	// 检索结果
	Results []SearchResult `json:"results"`
	
	// 搜索统计信息
	Stats SearchStats `json:"stats"`
	
	// 错误信息
	Error string `json:"error,omitempty"`
}

// SearchResult 搜索结果
type SearchResult struct {
	// 文档ID
	ID string `json:"id"`
	
	// 内容
	Content string `json:"content"`
	
	// 分数
	Score float64 `json:"score"`
	
	// 来源
	Source string `json:"source,omitempty"`
	
	// 元数据
	Metadata map[string]interface{} `json:"metadata,omitempty"`
	
	// 片段
	Snippet string `json:"snippet,omitempty"`
}

// SearchStats 搜索统计信息
type SearchStats struct {
	// 搜索耗时
	ElapsedTime time.Duration `json:"elapsed_time"`
	
	// 向量搜索结果数
	VectorResults int `json:"vector_results,omitempty"`
	
	// 关键词搜索结果数
	KeywordResults int `json:"keyword_results,omitempty"`
	
	// 重排序结果数
	RerankedResults int `json:"reranked_results,omitempty"`
	
	// 向量权重
	VectorWeight float64 `json:"vector_weight,omitempty"`
	
	// 关键词权重
	KeywordWeight float64 `json:"keyword_weight,omitempty"`
	
	// 缓存命中
	CacheHit bool `json:"cache_hit,omitempty"`
	
	// 其他统计信息
	ExtraStats map[string]interface{} `json:"extra_stats,omitempty"`
}

// NewSearchHandler 创建搜索处理器
func NewSearchHandler(factoryInstance *factory.ComponentFactory, logger utils.Logger, cacheManager utils.CacheManager) *SearchHandler {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	if cacheManager == nil {
		cacheManager = utils.NewNoopCacheManager()
	}
	
	return &SearchHandler{
		factory:      factoryInstance,
		logger:       logger,
		cacheManager: cacheManager,
		timeout:      30 * time.Second,
	}
}

// HandleSearch 处理搜索请求
func (h *SearchHandler) HandleSearch(c *gin.Context) {
	var request SearchRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("无效的请求参数: %v", err)})
		return
	}
	
	// 设置默认值
	if request.TopK <= 0 {
		request.TopK = 10
	}
	
	if request.ExtraOptions == nil {
		request.ExtraOptions = make(map[string]interface{})
	}
	
	// 生成缓存键
	cacheKey := h.generateCacheKey(request)
	
	// 检查缓存
	if request.UseCache {
		if cachedData, found := h.cacheManager.Get(cacheKey); found {
			var response SearchResponse
			if err := json.Unmarshal([]byte(cachedData), &response); err == nil {
				response.Stats.CacheHit = true
				c.JSON(http.StatusOK, response)
				return
			}
		}
	}
	
	// 创建上下文
	ctx, cancel := context.WithTimeout(context.Background(), h.timeout)
	defer cancel()
	
	// 执行搜索
	response, err := h.performSearch(ctx, request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("搜索失败: %v", err)})
		return
	}
	
	// 缓存结果
	if request.UseCache {
		if respData, err := json.Marshal(response); err == nil {
			h.cacheManager.Set(cacheKey, string(respData), 10*time.Minute)
		}
	}
	
	c.JSON(http.StatusOK, response)
}

// performSearch 执行搜索
func (h *SearchHandler) performSearch(ctx context.Context, request SearchRequest) (*SearchResponse, error) {
	startTime := time.Now()
	
	// 创建响应
	response := &SearchResponse{
		Results: make([]SearchResult, 0),
		Stats: SearchStats{
			ExtraStats: make(map[string]interface{}),
		},
	}
	
	// 获取查询分析器
	queryAnalyzer, err := h.factory.GetQueryAnalyzer("simple")
	if err != nil {
		return nil, fmt.Errorf("获取查询分析器失败: %w", err)
	}
	
	// 分析查询
	analysisResult, err := queryAnalyzer.Analyze(ctx, request.Query)
	if err != nil {
		return nil, fmt.Errorf("分析查询失败: %w", err)
	}
	
	// 注入领域信息
	if request.Domain != "" {
		switch request.Domain {
		case "tcm", "中医":
			analysisResult.Domain = rag.DomainTCM
		case "nutrition", "营养":
			analysisResult.Domain = rag.DomainNutrition
		case "medicine", "医学":
			analysisResult.Domain = rag.DomainMedicine
		case "agriculture", "农业":
			analysisResult.Domain = rag.DomainAgriculture
		}
	}
	
	// 记录分析结果
	response.Stats.ExtraStats["query_type"] = string(analysisResult.Type)
	response.Stats.ExtraStats["query_domain"] = string(analysisResult.Domain)
	
	var searchResults []models.SearchResult
	
	// 选择搜索方法
	if request.UseHybrid {
		// 使用混合搜索
		hybridSearcher, err := h.factory.GetHybridSearcher("adaptive")
		if err != nil {
			return nil, fmt.Errorf("获取混合搜索器失败: %w", err)
		}
		
		// 获取权重调整器
		weightAdjuster, err := h.factory.GetWeightAdjuster("simple")
		if err != nil {
			h.logger.Warn("获取权重调整器失败，将使用默认权重", "error", err)
		}
		
		// 调整权重
		vectorWeight, keywordWeight := analysisResult.VectorWeight, analysisResult.KeywordWeight
		if weightAdjuster != nil {
			vectorWeight, keywordWeight, err = weightAdjuster.AdjustWeights(ctx, request.Query, analysisResult)
			if err != nil {
				h.logger.Warn("调整权重失败，将使用默认权重", "error", err)
			}
		}
		
		// 执行混合搜索
		searchResults, err = hybridSearcher.Search(ctx, request.Query, request.TopK, map[string]interface{}{
			"vector_weight":   vectorWeight,
			"keyword_weight":  keywordWeight,
			"domain":          string(analysisResult.Domain),
			"query_type":      string(analysisResult.Type),
			"keywords":        analysisResult.Keywords,
			"user_id":         request.UserID,
			"tcm_specific":    analysisResult.Domain == rag.DomainTCM || (request.TCMOptions != nil),
			"tcm_options":     request.TCMOptions,
			"multimodal_data": request.MultimodalOptions,
		})
		
		if err != nil {
			return nil, fmt.Errorf("混合搜索失败: %w", err)
		}
		
		// 记录统计信息
		response.Stats.VectorWeight = vectorWeight
		response.Stats.KeywordWeight = keywordWeight
		
	} else {
		// 使用向量搜索
		embedder, err := h.factory.GetEmbedder("default")
		if err != nil {
			return nil, fmt.Errorf("获取嵌入器失败: %w", err)
		}
		
		// 获取向量存储
		vectorStore, err := h.factory.GetVectorStore("default")
		if err != nil {
			return nil, fmt.Errorf("获取向量存储失败: %w", err)
		}
		
		// 嵌入查询
		queryEmbedding, err := embedder.EmbedQuery(ctx, request.Query)
		if err != nil {
			return nil, fmt.Errorf("嵌入查询失败: %w", err)
		}
		
		// 执行向量搜索
		searchResults, err = vectorStore.Search(ctx, queryEmbedding, request.TopK, nil)
		if err != nil {
			return nil, fmt.Errorf("向量搜索失败: %w", err)
		}
	}
	
	// 重排序
	if request.UseRerank && len(searchResults) > 0 {
		reranker, err := h.factory.GetReranker("cross-encoder")
		if err != nil {
			h.logger.Warn("获取重排序器失败，将使用原始结果", "error", err)
		} else {
			// 创建重排序选项
			options := request.createRerankerOptions()
			
			// 执行重排序
			rerankedResults, rerankErr := reranker.Rerank(ctx, request.Query, searchResults, options)
			if rerankErr != nil {
				h.logger.Warn("重排序失败，将使用原始结果", "error", rerankErr)
			} else {
				searchResults = rerankedResults
				response.Stats.RerankedResults = len(rerankedResults)
			}
		}
	}
	
	// 转换结果
	for _, result := range searchResults {
		response.Results = append(response.Results, SearchResult{
			ID:      result.ID,
			Content: result.Content,
			Score:   result.Score,
			Source:  result.Source,
			Metadata: result.Metadata.Properties,
			Snippet: result.Snippet,
		})
	}
	
	// 计算统计信息
	response.Stats.ElapsedTime = time.Since(startTime)
	
	return response, nil
}

// generateCacheKey 生成缓存键
func (h *SearchHandler) generateCacheKey(request SearchRequest) string {
	return fmt.Sprintf("search:%s:%s:%d:%t:%t", 
		request.Query, 
		request.Domain, 
		request.TopK, 
		request.UseHybrid, 
		request.UseRerank)
}

// createRerankerOptions 创建重排序选项
func (r *SearchRequest) createRerankerOptions() map[string]interface{} {
	options := map[string]interface{}{
		"top_k":         r.TopK,
		"user_id":       r.UserID,
		"use_cache":     r.UseCache,
		"include_metadata": true,
	}
	
	// 设置领域
	if r.Domain != "" {
		options["domain"] = r.Domain
	}
	
	// 设置中医选项
	if r.TCMOptions != nil {
		options["tcm_specific"] = true
		options["tcm_options"] = r.TCMOptions
	}
	
	// 添加额外选项
	for k, v := range r.ExtraOptions {
		options[k] = v
	}
	
	return options
}

// RegisterRoutes 注册路由
func (h *SearchHandler) RegisterRoutes(router *gin.Engine) {
	router.POST("/api/search", h.HandleSearch)
} 