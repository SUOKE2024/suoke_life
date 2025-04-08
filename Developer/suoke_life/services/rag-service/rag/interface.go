package rag

import (
	"context"
	"io"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
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

	// HybridSearch 混合检索(向量+关键词)
	HybridSearch(ctx context.Context, collectionName string, query string, options models.HybridSearchOptions) ([]models.Document, error)
	
	// RewriteQuery 查询改写
	RewriteQuery(ctx context.Context, request models.QueryRewriteRequest) (*models.QueryRewriteResponse, error)
	
	// CreateMultiModalEmbedding 创建多模态嵌入向量
	CreateMultiModalEmbedding(ctx context.Context, request models.EmbeddingRequest) (*models.EmbeddingResponse, error)
	
	// UploadMultiModalDocument 上传多模态文档
	UploadMultiModalDocument(ctx context.Context, request models.DocumentUploadRequest) (*models.DocumentUploadResponse, error)
	
	// DecomposeQuery 分解复杂查询为多个子查询
	DecomposeQuery(ctx context.Context, query string, options map[string]interface{}) ([]string, error)
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
	
	// ImageEmbeddingModelName 图像嵌入模型名称
	ImageEmbeddingModelName string
	
	// AudioEmbeddingModelName 音频嵌入模型名称
	AudioEmbeddingModelName string
	
	// ChunkStrategy 文本分块策略 (fixed, sentence, paragraph, semantic)
	ChunkStrategy string
	
	// EnableHybridSearch 是否启用混合检索
	EnableHybridSearch bool
	
	// KeywordSearchModel 关键词搜索模型 (bm25, tfidf)
	KeywordSearchModel string
	
	// EnableQueryRewrite 是否启用查询改写
	EnableQueryRewrite bool
}

// NewRAGService 创建RAG服务
func NewRAGService(ctx context.Context, options RAGFactoryOptions) (RAGService, error) {
	// 暂时只提供默认的RAG服务实现
	return NewDefaultRAGService(nil, nil, 10, 1000, nil), nil
} 