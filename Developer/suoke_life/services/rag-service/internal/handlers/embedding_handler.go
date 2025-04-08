package handlers

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/suoke/suoke_life/services/rag-service/internal/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// DefaultEmbeddingHandler 默认嵌入处理器
type DefaultEmbeddingHandler struct {
	embedder embeddings.TextEmbedder
	metrics  MetricsHandler
}

// NewEmbeddingHandler 创建新的嵌入处理器
func NewEmbeddingHandler(embedder embeddings.TextEmbedder, metrics MetricsHandler) EmbeddingHandler {
	return &DefaultEmbeddingHandler{
		embedder: embedder,
		metrics:  metrics,
	}
}

// Register 注册路由
func (h *DefaultEmbeddingHandler) Register(router interface{}) {
	r, ok := router.(*chi.Mux)
	if !ok {
		panic("router不是chi.Mux类型")
	}

	// 注册路由
	r.Group(func(r chi.Router) {
		r.Post("/api/v1/embeddings", h.CreateEmbeddingHandler)
		r.Get("/api/v1/embeddings/health", h.HealthCheckHandler)
	})
}

// CreateEmbeddingHandler 创建嵌入向量
func (h *DefaultEmbeddingHandler) CreateEmbeddingHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 解析请求
	var request models.EmbeddingRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "无效的请求参数", err)
		return
	}
	
	// 校验请求数据
	texts := request.Texts
	if len(texts) == 0 && request.Text != "" {
		texts = []string{request.Text}
	}
	
	if len(texts) == 0 {
		respondWithError(w, http.StatusBadRequest, "需要至少提供一个文本进行嵌入", nil)
		return
	}
	
	// 设置上下文
	ctx := r.Context()
	
	// 单个文本嵌入处理
	if len(texts) == 1 {
		embeddingVector, err := h.embedder.EmbedQuery(ctx, texts[0])
		if err != nil {
			respondWithError(w, http.StatusInternalServerError, "嵌入处理失败", err)
			return
		}
		
		// 计算token数
		tokenCount := h.embedder.CountTokens(texts[0])
		
		// 记录指标
		h.metrics.RecordTokens(h.embedder.GetModelName(), "embedding", tokenCount)
		h.metrics.RecordRequestDuration("embeddings", "create", time.Since(start).Seconds())
		
		// 构建响应
		response := models.EmbeddingResponse{
			Embedding:  embeddingVector,
			ModelName:  h.embedder.GetModelName(),
			Dimensions: h.embedder.GetDimensions(),
			TokenCount: tokenCount,
		}
		
		respondWithJSON(w, http.StatusOK, response)
		return
	}
	
	// 批量文本嵌入处理
	embeddings, err := h.embedder.EmbedDocuments(ctx, texts)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "批量嵌入处理失败", err)
		return
	}
	
	// 计算总token数
	totalTokens := 0
	for _, text := range texts {
		totalTokens += h.embedder.CountTokens(text)
	}
	
	// 记录指标
	h.metrics.RecordTokens(h.embedder.GetModelName(), "embedding", totalTokens)
	h.metrics.RecordRequestDuration("embeddings", "create_batch", time.Since(start).Seconds())
	
	// 构建响应
	response := models.EmbeddingResponse{
		Embeddings: embeddings,
		ModelName:  h.embedder.GetModelName(),
		Dimensions: h.embedder.GetDimensions(),
		TokenCount: totalTokens,
	}
	
	respondWithJSON(w, http.StatusOK, response)
}

// HealthCheckHandler 健康检查
func (h *DefaultEmbeddingHandler) HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 检查嵌入模型的状态
	isHealthy := true
	errorMessage := ""
	
	// 如果嵌入模型实现了IsHealthy方法，则调用检查
	if healthChecker, ok := h.embedder.(interface{ IsHealthy(context.Context) bool }); ok {
		isHealthy = healthChecker.IsHealthy(r.Context())
		if !isHealthy {
			errorMessage = "嵌入模型健康检查失败"
		}
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("embeddings", "health_check", time.Since(start).Seconds())
	
	// 根据健康状态返回响应
	if isHealthy {
		respondWithJSON(w, http.StatusOK, map[string]interface{}{
			"status":    "healthy",
			"model":     h.embedder.GetModelName(),
			"dimensions": h.embedder.GetDimensions(),
			"timestamp": time.Now(),
		})
	} else {
		respondWithJSON(w, http.StatusServiceUnavailable, map[string]interface{}{
			"status":  "unhealthy",
			"message": errorMessage,
			"model":   h.embedder.GetModelName(),
			"timestamp": time.Now(),
		})
	}
}

// ModelsHandler 模型列表处理程序
func (h *DefaultEmbeddingHandler) ModelsHandler(c *gin.Context) {
	// 返回支持的嵌入模型列表
	models := []gin.H{
		{
			"id":          "text-embedding-3-small",
			"name":        "OpenAI Small Embeddings",
			"description": "OpenAI小型嵌入模型",
			"dimensions":  1536,
			"provider":    "openai",
		},
		{
			"id":          "text-embedding-3-large",
			"name":        "OpenAI Large Embeddings",
			"description": "OpenAI大型嵌入模型",
			"dimensions":  3072,
			"provider":    "openai",
		},
		{
			"id":          "text-embedding-ada-002",
			"name":        "OpenAI Ada Embeddings",
			"description": "OpenAI Ada嵌入模型(旧版)",
			"dimensions":  1536,
			"provider":    "openai",
		},
		{
			"id":          "all-MiniLM-L6-v2",
			"name":        "MiniLM Embeddings",
			"description": "本地MiniLM嵌入模型",
			"dimensions":  384,
			"provider":    "local",
		},
	}

	c.JSON(http.StatusOK, models)
} 