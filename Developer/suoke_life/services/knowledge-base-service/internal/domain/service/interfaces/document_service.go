package interfaces

import (
	"context"
	"github.com/google/uuid"
	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
)

// DocumentService 文档服务接口
type DocumentService interface {
	GetDocumentByID(ctx context.Context, id uuid.UUID) (*entity.Document, error)
	GetDocumentsByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error)
	GetDocumentsByTags(ctx context.Context, tags []string) ([]*entity.Document, error)
	SearchDocuments(ctx context.Context, query string) ([]*entity.Document, error)
	SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error)
	CreateDocument(ctx context.Context, opts service.DocumentOptions) (*entity.Document, error)
	UpdateDocument(ctx context.Context, id uuid.UUID, title, content, description string, contentType entity.ContentType, categoryID uuid.UUID, tags []string) (*entity.Document, error)
	PublishDocument(ctx context.Context, id uuid.UUID) error
	ArchiveDocument(ctx context.Context, id uuid.UUID) error
	DeleteDocument(ctx context.Context, id uuid.UUID) error
	RegisterDocumentOnBlockchain(ctx context.Context, id uuid.UUID) (string, error)
}
