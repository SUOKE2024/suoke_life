package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/rag"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// defaultRAGHandler 默认RAG处理程序实现
type defaultRAGHandler struct {
	ragService rag.RAGService
}

// RegisterRoutes 注册路由
func (h *defaultRAGHandler) RegisterRoutes(router *gin.Engine) {
	// 创建RAG API组
	ragGroup := router.Group("/api/rag")
	{
		// 查询接口
		ragGroup.POST("/query", h.QueryHandler)
		ragGroup.POST("/stream", h.StreamQueryHandler)

		// 文档管理接口
		ragGroup.POST("/upload", h.UploadDocumentHandler)
		ragGroup.DELETE("/documents/:collection/:id", h.DeleteDocumentHandler)
		ragGroup.GET("/documents/:collection/:id", h.GetDocumentHandler)

		// 集合管理接口
		ragGroup.POST("/collections", h.CreateCollectionHandler)
		ragGroup.DELETE("/collections/:name", h.DeleteCollectionHandler)
		ragGroup.GET("/collections", h.ListCollectionsHandler)
		ragGroup.GET("/collections/:name", h.GetCollectionHandler)

		// 搜索接口
		ragGroup.POST("/search/:collection", h.SearchHandler)

		// 嵌入向量接口
		ragGroup.POST("/embed", h.CreateEmbeddingHandler)

		// 健康检查接口
		ragGroup.GET("/health", h.HealthCheckHandler)
	}
}

// QueryHandler 查询处理程序
func (h *defaultRAGHandler) QueryHandler(c *gin.Context) {
	var request models.QueryRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求", "message": err.Error()})
		return
	}

	// 禁用流式响应 (使用非流式处理)
	request.Stream = false

	// 执行RAG查询
	result, err := h.ragService.Query(c.Request.Context(), request)
	if err != nil {
		logger.Errorf("RAG查询失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "RAG查询失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

// StreamQueryHandler 流式查询处理程序
func (h *defaultRAGHandler) StreamQueryHandler(c *gin.Context) {
	var request models.QueryRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求", "message": err.Error()})
		return
	}

	// 强制启用流式响应
	request.Stream = true

	// 设置响应头
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("Transfer-Encoding", "chunked")

	// 创建写入器
	flusher := c.Writer

	// 执行流式RAG查询
	err := h.ragService.StreamQuery(c.Request.Context(), request, flusher)
	if err != nil {
		logger.Errorf("流式RAG查询失败: %v", err)
		// 由于已经开始流式响应，这里只能记录错误，无法改变状态码
	}
}

// UploadDocumentHandler 上传文档处理程序
func (h *defaultRAGHandler) UploadDocumentHandler(c *gin.Context) {
	var request models.DocumentUploadRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求", "message": err.Error()})
		return
	}

	// 执行文档上传
	response, err := h.ragService.UploadDocument(c.Request.Context(), request)
	if err != nil {
		logger.Errorf("文档上传失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "文档上传失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// CreateCollectionHandler 创建集合处理程序
func (h *defaultRAGHandler) CreateCollectionHandler(c *gin.Context) {
	var request models.CollectionCreateRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求", "message": err.Error()})
		return
	}

	// 执行集合创建
	collection, err := h.ragService.CreateCollection(c.Request.Context(), request)
	if err != nil {
		logger.Errorf("创建集合失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建集合失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, collection)
}

// DeleteCollectionHandler 删除集合处理程序
func (h *defaultRAGHandler) DeleteCollectionHandler(c *gin.Context) {
	name := c.Param("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "集合名不能为空"})
		return
	}

	// 执行集合删除
	err := h.ragService.DeleteCollection(c.Request.Context(), name)
	if err != nil {
		logger.Errorf("删除集合失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除集合失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "集合已删除"})
}

// ListCollectionsHandler 列出集合处理程序
func (h *defaultRAGHandler) ListCollectionsHandler(c *gin.Context) {
	// 执行集合列表获取
	collections, err := h.ragService.ListCollections(c.Request.Context())
	if err != nil {
		logger.Errorf("获取集合列表失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取集合列表失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, collections)
}

// GetCollectionHandler 获取集合处理程序
func (h *defaultRAGHandler) GetCollectionHandler(c *gin.Context) {
	name := c.Param("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "集合名不能为空"})
		return
	}

	// 执行集合获取
	collection, err := h.ragService.GetCollection(c.Request.Context(), name)
	if err != nil {
		logger.Errorf("获取集合失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取集合失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, collection)
}

// DeleteDocumentHandler 删除文档处理程序
func (h *defaultRAGHandler) DeleteDocumentHandler(c *gin.Context) {
	collection := c.Param("collection")
	id := c.Param("id")
	if collection == "" || id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "集合名和文档ID不能为空"})
		return
	}

	// 执行文档删除
	err := h.ragService.DeleteDocument(c.Request.Context(), collection, id)
	if err != nil {
		logger.Errorf("删除文档失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除文档失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "文档已删除"})
}

// GetDocumentHandler 获取文档处理程序
func (h *defaultRAGHandler) GetDocumentHandler(c *gin.Context) {
	collection := c.Param("collection")
	id := c.Param("id")
	if collection == "" || id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "集合名和文档ID不能为空"})
		return
	}

	// 执行文档获取
	document, err := h.ragService.GetDocument(c.Request.Context(), collection, id)
	if err != nil {
		logger.Errorf("获取文档失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取文档失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, document)
}

// SearchHandler 搜索处理程序
func (h *defaultRAGHandler) SearchHandler(c *gin.Context) {
	collection := c.Param("collection")
	if collection == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "集合名不能为空"})
		return
	}

	// 获取查询参数
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "查询参数不能为空"})
		return
	}

	limit := 10 // 默认限制为10
	if limitStr := c.Query("limit"); limitStr != "" {
		if limitVal, err := strconv.Atoi(limitStr); err == nil {
			limit = limitVal
		}
	}

	// 执行搜索
	results, err := h.ragService.Search(c.Request.Context(), collection, query, limit, nil)
	if err != nil {
		logger.Errorf("搜索失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "搜索失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, results)
}

// CreateEmbeddingHandler 创建嵌入向量处理程序
func (h *defaultRAGHandler) CreateEmbeddingHandler(c *gin.Context) {
	var request models.EmbeddingRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求", "message": err.Error()})
		return
	}

	// 构建选项
	options := map[string]interface{}{
		"model": request.Model,
	}

	// 执行嵌入向量创建
	response, err := h.ragService.CreateEmbedding(c.Request.Context(), request.Texts, options)
	if err != nil {
		logger.Errorf("创建嵌入向量失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建嵌入向量失败", "message": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// HealthCheckHandler 健康检查处理程序
func (h *defaultRAGHandler) HealthCheckHandler(c *gin.Context) {
	// 执行健康检查
	err := h.ragService.HealthCheck(c.Request.Context())
	if err != nil {
		logger.Errorf("健康检查失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"status": "unhealthy", "error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "healthy"})
} 