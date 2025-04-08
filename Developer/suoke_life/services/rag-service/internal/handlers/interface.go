package handlers

import (
	"net/http"
)

// Handler 基础处理器接口
type Handler interface {
	// Register 注册路由
	Register(router interface{})
}

// RAGHandler RAG处理器接口
type RAGHandler interface {
	Handler

	// QueryHandler 查询处理
	QueryHandler(w http.ResponseWriter, r *http.Request)

	// StreamQueryHandler 流式查询处理
	StreamQueryHandler(w http.ResponseWriter, r *http.Request)

	// UploadDocumentHandler 上传文档处理
	UploadDocumentHandler(w http.ResponseWriter, r *http.Request)

	// GetDocumentHandler 获取文档
	GetDocumentHandler(w http.ResponseWriter, r *http.Request)

	// DeleteDocumentHandler 删除文档
	DeleteDocumentHandler(w http.ResponseWriter, r *http.Request)

	// CreateCollectionHandler 创建集合
	CreateCollectionHandler(w http.ResponseWriter, r *http.Request)

	// DeleteCollectionHandler 删除集合
	DeleteCollectionHandler(w http.ResponseWriter, r *http.Request)

	// ListCollectionsHandler 列出集合
	ListCollectionsHandler(w http.ResponseWriter, r *http.Request)

	// GetCollectionHandler 获取集合信息
	GetCollectionHandler(w http.ResponseWriter, r *http.Request)

	// SearchHandler 搜索处理
	SearchHandler(w http.ResponseWriter, r *http.Request)

	// HealthCheckHandler 健康检查
	HealthCheckHandler(w http.ResponseWriter, r *http.Request)
}

// EmbeddingHandler 嵌入处理器接口
type EmbeddingHandler interface {
	Handler

	// CreateEmbeddingHandler 创建嵌入向量
	CreateEmbeddingHandler(w http.ResponseWriter, r *http.Request)

	// HealthCheckHandler 健康检查
	HealthCheckHandler(w http.ResponseWriter, r *http.Request)
}

// MetricsHandler 指标处理器接口
type MetricsHandler interface {
	Handler

	// RecordRequest 记录请求
	RecordRequest(method, endpoint, status string)

	// RecordTokens 记录token数
	RecordTokens(model, tokenType string, count int)

	// RecordRequestDuration 记录请求耗时
	RecordRequestDuration(method, endpoint string, durationSeconds float64)

	// GetTotalRequests 获取总请求数
	GetTotalRequests() int64

	// GetTotalTokens 获取总Token数
	GetTotalTokens() int64

	// GetRequestDurationAvg 获取请求平均耗时
	GetRequestDurationAvg() float64

	// GetMetricsHandler 获取指标处理器的HTTP处理函数
	GetMetricsHandler() http.Handler
}
