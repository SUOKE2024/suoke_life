package handlers

import (
	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/internal/rag"
)

// Handler 处理程序接口
type Handler interface {
	// RegisterRoutes 注册路由
	RegisterRoutes(router *gin.Engine)
}

// RAGHandler RAG处理程序
type RAGHandler interface {
	Handler

	// QueryHandler 查询处理程序
	QueryHandler(c *gin.Context)

	// StreamQueryHandler 流式查询处理程序
	StreamQueryHandler(c *gin.Context)

	// UploadDocumentHandler 上传文档处理程序
	UploadDocumentHandler(c *gin.Context)

	// CreateCollectionHandler 创建集合处理程序
	CreateCollectionHandler(c *gin.Context)

	// DeleteCollectionHandler 删除集合处理程序
	DeleteCollectionHandler(c *gin.Context)

	// ListCollectionsHandler 列出集合处理程序
	ListCollectionsHandler(c *gin.Context)

	// GetCollectionHandler 获取集合处理程序
	GetCollectionHandler(c *gin.Context)

	// DeleteDocumentHandler 删除文档处理程序
	DeleteDocumentHandler(c *gin.Context)

	// GetDocumentHandler 获取文档处理程序
	GetDocumentHandler(c *gin.Context)

	// SearchHandler 搜索处理程序
	SearchHandler(c *gin.Context)

	// CreateEmbeddingHandler 创建嵌入向量处理程序
	CreateEmbeddingHandler(c *gin.Context)

	// HealthCheckHandler 健康检查处理程序
	HealthCheckHandler(c *gin.Context)
}

// EmbeddingHandler 嵌入处理程序
type EmbeddingHandler interface {
	Handler

	// EmbedHandler 嵌入处理程序
	EmbedHandler(c *gin.Context)

	// ModelsHandler 模型列表处理程序
	ModelsHandler(c *gin.Context)
}

// MetricsHandler 指标处理程序
type MetricsHandler interface {
	Handler

	// MetricsHandler 指标处理程序
	MetricsHandler(c *gin.Context)
}

// 工厂函数 - 创建RAG处理程序
func NewRAGHandler(ragService rag.RAGService) RAGHandler {
	return &defaultRAGHandler{
		ragService: ragService,
	}
}

// 工厂函数 - 创建嵌入处理程序
func NewEmbeddingHandler() EmbeddingHandler {
	return &defaultEmbeddingHandler{}
}

// 工厂函数 - 创建指标处理程序
func NewMetricsHandler() MetricsHandler {
	return &defaultMetricsHandler{}
} 