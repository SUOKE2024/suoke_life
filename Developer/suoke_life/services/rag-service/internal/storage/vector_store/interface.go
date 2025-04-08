package vector_store

import (
	"context"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
)

// VectorStore 向量存储接口
type VectorStore interface {
	// Initialize 初始化向量存储
	Initialize(ctx context.Context) error

	// Close 关闭向量存储连接
	Close() error

	// CreateCollection 创建集合
	CreateCollection(ctx context.Context, name string, dimension int, description string) error

	// DeleteCollection 删除集合
	DeleteCollection(ctx context.Context, name string) error

	// ListCollections 列出所有集合
	ListCollections(ctx context.Context) ([]models.Collection, error)

	// GetCollection 获取指定集合信息
	GetCollection(ctx context.Context, name string) (*models.Collection, error)

	// CollectionExists 检查集合是否存在
	CollectionExists(ctx context.Context, name string) (bool, error)

	// UpsertDocuments 批量更新或插入文档
	UpsertDocuments(ctx context.Context, collectionName string, documents []models.Document) ([]string, error)

	// UpsertDocument 更新或插入单个文档
	UpsertDocument(ctx context.Context, collectionName string, document models.Document) (string, error)

	// DeleteDocument 删除文档
	DeleteDocument(ctx context.Context, collectionName string, documentID string) error

	// DeleteDocuments 批量删除文档
	DeleteDocuments(ctx context.Context, collectionName string, documentIDs []string) error

	// DeleteDocumentsByFilter 根据过滤条件删除文档
	DeleteDocumentsByFilter(ctx context.Context, collectionName string, filter map[string]interface{}) error

	// GetDocument 获取文档
	GetDocument(ctx context.Context, collectionName string, documentID string) (*models.Document, error)

	// SimilaritySearch 相似度搜索
	SimilaritySearch(
		ctx context.Context,
		collectionName string,
		queryVector []float32,
		limit int,
		filter map[string]interface{},
		includeVector bool,
	) ([]models.Document, error)

	// SimilaritySearchByText 通过文本进行相似度搜索
	SimilaritySearchByText(
		ctx context.Context,
		collectionName string,
		query string,
		limit int,
		filter map[string]interface{},
		includeVector bool,
	) ([]models.Document, error)

	// MMRSearch 最大边缘相关性搜索
	MMRSearch(
		ctx context.Context,
		collectionName string,
		queryVector []float32,
		limit int,
		lambdaMultiplier float64,
		filter map[string]interface{},
		includeVector bool,
	) ([]models.Document, error)

	// CountDocuments 计算文档数量
	CountDocuments(ctx context.Context, collectionName string, filter map[string]interface{}) (int, error)

	// Search 高级搜索接口
	Search(
		ctx context.Context,
		collectionName string,
		queryVector []float32,
		queryType models.QueryType,
		limit int,
		filter map[string]interface{},
		includeVector bool,
		options map[string]interface{},
	) ([]models.Document, error)

	// SimilaritySearchWithScore 带分数的相似度搜索
	SimilaritySearchWithScore(
		ctx context.Context,
		collectionName string,
		queryVector []float32,
		limit int,
		filter map[string]interface{},
		includeVector bool,
	) ([]models.Document, error)

	// GetDocumentBatch 批量获取文档
	GetDocumentBatch(ctx context.Context, collectionName string, documentIDs []string) ([]models.Document, error)
} 