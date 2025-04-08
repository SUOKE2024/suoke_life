
package rag

import (
	"context"
	"io"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/rag"
)

// RAGService RAG服务接口
type RAGService interface {
	// Initialize 初始化RAG服务
	Initialize(ctx context.Context) error

	// Close 关闭RAG服务
	Close() error

	// Query 执行RAG查询
	Query(ctx context.Context, request models.QueryRequest) (*models.QueryResult, error)

	// StreamQuery 执行流式RAG查询
	StreamQuery(ctx context.Context, request models.QueryRequest, writer io.Writer) error

	// UploadDocument 上传文档
	UploadDocument(ctx context.Context, request models.DocumentUploadRequest) (*models.DocumentUploadResponse, error)

	// CreateCollection 创建集合
	CreateCollection(ctx context.Context, request models.CollectionCreateRequest) (*models.Collection, error)

	// DeleteCollection 删除集合
	DeleteCollection(ctx context.Context, name string) error

	// ListCollections 列出所有集合
	ListCollections(ctx context.Context) ([]models.Collection, error)

	// GetCollection 获取集合信息
	GetCollection(ctx context.Context, name string) (*models.Collection, error)

	// DeleteDocument 删除文档
	DeleteDocument(ctx context.Context, collectionName string, documentID string) error

	// GetDocument 获取文档
	GetDocument(ctx context.Context, collectionName string, documentID string) (*models.Document, error)

	// Search 在集合中搜索
	Search(ctx context.Context, collectionName string, query string, limit int, filter map[string]interface{}) ([]models.Document, error)

	// CreateEmbedding 创建嵌入向量
	CreateEmbedding(ctx context.Context, texts []string, options map[string]interface{}) (*models.EmbeddingResponse, error)

	// HealthCheck 健康检查
	HealthCheck(ctx context.Context) error
}

// RAGFactoryOptions RAG工厂选项
type RAGFactoryOptions struct {
	// VectorStoreName 向量存储名称
	VectorStoreName string

	// EmbeddingModelName 嵌入模型名称
	EmbeddingModelName string

	// LLMName 大语言模型名称
	LLMName string

	// UseReranker 是否使用重排序器
	UseReranker bool

	// RerankerModelName 重排序模型名称
	RerankerModelName string

	// ConfigPath 配置文件路径
	ConfigPath string

	// ChunkSize 文本分块大小
	ChunkSize int

	// ChunkOverlap 分块重叠大小
	ChunkOverlap int

	// MaxConcurrentRequests 最大并发请求数
	MaxConcurrentRequests int

	// EnableWebSearch 是否启用网络搜索
	EnableWebSearch bool
}

// NewRAGService 创建RAG服务
func NewRAGService(ctx context.Context, options RAGFactoryOptions) (RAGService, error) {
	// 导入rag包中的DefaultRAGService实现
	defaultService := rag.NewDefaultRAGService(nil, nil, 10, 1000, nil)
	
	// 包装成实现了RAGService接口的类型
	return &ragServiceWrapper{
		impl: defaultService,
	}, nil
}

// ragServiceWrapper 包装rag包中的DefaultRAGService，确保实现RAGService接口
type ragServiceWrapper struct {
	impl *rag.DefaultRAGService
}

// Initialize 初始化RAG服务
func (w *ragServiceWrapper) Initialize(ctx context.Context) error {
	return w.impl.Initialize(ctx)
}

// Close 关闭RAG服务
func (w *ragServiceWrapper) Close() error {
	return w.impl.Close()
}

// Query 执行RAG查询
func (w *ragServiceWrapper) Query(ctx context.Context, request models.QueryRequest) (*models.QueryResult, error) {
	return w.impl.Query(ctx, request)
}

// StreamQuery 执行流式RAG查询
func (w *ragServiceWrapper) StreamQuery(ctx context.Context, request models.QueryRequest, writer io.Writer) error {
	return w.impl.StreamQuery(ctx, request, writer)
}

// UploadDocument 上传文档
func (w *ragServiceWrapper) UploadDocument(ctx context.Context, request models.DocumentUploadRequest) (*models.DocumentUploadResponse, error) {
	return w.impl.UploadDocument(ctx, request)
}

// CreateCollection 创建集合
func (w *ragServiceWrapper) CreateCollection(ctx context.Context, request models.CollectionCreateRequest) (*models.Collection, error) {
	return w.impl.CreateCollection(ctx, request)
}

// DeleteCollection 删除集合
func (w *ragServiceWrapper) DeleteCollection(ctx context.Context, name string) error {
	return w.impl.DeleteCollection(ctx, name)
}

// ListCollections 列出所有集合
func (w *ragServiceWrapper) ListCollections(ctx context.Context) ([]models.Collection, error) {
	return w.impl.ListCollections(ctx)
}

// GetCollection 获取集合信息
func (w *ragServiceWrapper) GetCollection(ctx context.Context, name string) (*models.Collection, error) {
	return w.impl.GetCollection(ctx, name)
}

// DeleteDocument 删除文档
func (w *ragServiceWrapper) DeleteDocument(ctx context.Context, collectionName string, documentID string) error {
	return w.impl.DeleteDocument(ctx, collectionName, documentID)
}

// GetDocument 获取文档
func (w *ragServiceWrapper) GetDocument(ctx context.Context, collectionName string, documentID string) (*models.Document, error) {
	return w.impl.GetDocument(ctx, collectionName, documentID)
}

// Search 在集合中搜索
func (w *ragServiceWrapper) Search(ctx context.Context, collectionName string, query string, limit int, filter map[string]interface{}) ([]models.Document, error) {
	return w.impl.Search(ctx, collectionName, query, limit, filter)
}

// CreateEmbedding 创建嵌入向量
func (w *ragServiceWrapper) CreateEmbedding(ctx context.Context, texts []string, options map[string]interface{}) (*models.EmbeddingResponse, error) {
	return w.impl.CreateEmbedding(ctx, texts, options)
}

// HealthCheck 健康检查
func (w *ragServiceWrapper) HealthCheck(ctx context.Context) error {
	return w.impl.HealthCheck(ctx)
} 