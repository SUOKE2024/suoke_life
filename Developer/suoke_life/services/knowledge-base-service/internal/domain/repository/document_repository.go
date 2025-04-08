package repository

import (
	"context"
	"github.com/google/uuid"
	"knowledge-base-service/internal/domain/entity"
)

// DocumentRepository 文档仓储接口
type DocumentRepository interface {
	// 根据ID查找文档
	FindByID(ctx context.Context, id uuid.UUID) (*entity.Document, error)

	// 根据分类查找文档
	FindByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error)

	// 根据标签查找文档
	FindByTags(ctx context.Context, tags []string) ([]*entity.Document, error)

	// 全文搜索
	Search(ctx context.Context, query string) ([]*entity.Document, error)

	// 语义搜索
	SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error)

	// 保存文档
	Save(ctx context.Context, document *entity.Document) error

	// 更新文档
	Update(ctx context.Context, document *entity.Document) error

	// 删除文档
	Delete(ctx context.Context, id uuid.UUID) error

	// 在区块链上注册文档
	RegisterOnBlockchain(ctx context.Context, document *entity.Document) (string, error)
}
