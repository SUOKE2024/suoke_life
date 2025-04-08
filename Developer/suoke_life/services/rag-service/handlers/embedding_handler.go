package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/internal/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// defaultEmbeddingHandler 默认嵌入处理程序实现
type defaultEmbeddingHandler struct {
	// 可以添加嵌入服务的引用
}

// RegisterRoutes 注册路由
func (h *defaultEmbeddingHandler) RegisterRoutes(router *gin.Engine) {
	// 创建嵌入API组
	embedGroup := router.Group("/api/embeddings")
	{
		// 嵌入接口
		embedGroup.POST("", h.EmbedHandler)
		
		// 模型列表接口
		embedGroup.GET("/models", h.ModelsHandler)
	}
}

// EmbedHandler 嵌入处理程序
func (h *defaultEmbeddingHandler) EmbedHandler(c *gin.Context) {
	var request models.EmbeddingRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求", "message": err.Error()})
		return
	}

	// 验证文本不为空
	if len(request.Texts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "文本列表不能为空"})
		return
	}

	// 确定使用的模型
	modelName := "text-embedding-3-small" // 默认模型
	if request.Model != "" {
		modelName = request.Model
	}

	// 创建选项
	options := embeddings.EmbeddingOptions{
		Model:     modelName,
		UseLocal:  false,
		Dimensions: 0, // 使用模型默认维度
		BatchSize: 32,
		UserId:    request.UserId,
	}

	// 创建嵌入模型
	embedder, err := embeddings.CreateEmbedder(options)
	if err != nil {
		logger.Errorf("创建嵌入模型失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建嵌入模型失败", "message": err.Error()})
		return
	}
	defer embedder.Close()

	// 生成嵌入向量
	startTime := c.MustGet("startTime").(int64)
	vectors, err := embedder.EmbedDocuments(c.Request.Context(), request.Texts)
	if err != nil {
		logger.Errorf("生成嵌入向量失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "生成嵌入向量失败", "message": err.Error()})
		return
	}

	// 计算token数量
	tokenCount := 0
	for _, text := range request.Texts {
		tokenCount += embedder.CountTokens(text)
	}

	// 构建响应
	response := models.EmbeddingResponse{
		Embeddings:  vectors,
		Model:       embedder.GetModelName(),
		Dimensions:  embedder.GetDimensions(),
		ProcessTime: float64(c.MustGet("endTime").(int64) - startTime) / 1000.0,
	}

	c.JSON(http.StatusOK, response)
}

// ModelsHandler 模型列表处理程序
func (h *defaultEmbeddingHandler) ModelsHandler(c *gin.Context) {
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