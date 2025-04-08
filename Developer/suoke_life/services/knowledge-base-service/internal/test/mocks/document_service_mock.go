package mocks

import (
	"context"

	"github.com/google/uuid"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
)

// MockDocumentService 文档服务接口的模拟实现
type MockDocumentService struct {
	mock.Mock
}

// GetDocumentByID 模拟根据ID获取文档
func (m *MockDocumentService) GetDocumentByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
	args := m.Called(ctx, id)

	if doc := args.Get(0); doc != nil {
		return doc.(*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// GetDocumentsByCategory 模拟根据分类获取文档
func (m *MockDocumentService) GetDocumentsByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error) {
	args := m.Called(ctx, categoryID)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// GetDocumentsByTags 模拟根据标签获取文档
func (m *MockDocumentService) GetDocumentsByTags(ctx context.Context, tags []string) ([]*entity.Document, error) {
	args := m.Called(ctx, tags)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// SearchDocuments 模拟搜索文档
func (m *MockDocumentService) SearchDocuments(ctx context.Context, query string) ([]*entity.Document, error) {
	args := m.Called(ctx, query)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// SemanticSearch 模拟语义搜索
func (m *MockDocumentService) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	args := m.Called(ctx, query, limit)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// CreateDocument 模拟创建文档
func (m *MockDocumentService) CreateDocument(ctx context.Context, opts service.DocumentOptions) (*entity.Document, error) {
	args := m.Called(ctx, opts)

	if doc := args.Get(0); doc != nil {
		return doc.(*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// UpdateDocument 模拟更新文档
func (m *MockDocumentService) UpdateDocument(ctx context.Context, id uuid.UUID, title, content, description string, contentType entity.ContentType, categoryID uuid.UUID, tags []string) (*entity.Document, error) {
	args := m.Called(ctx, id, title, content, description, contentType, categoryID, tags)

	if doc := args.Get(0); doc != nil {
		return doc.(*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// DeleteDocument 模拟删除文档
func (m *MockDocumentService) DeleteDocument(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// PublishDocument 模拟发布文档
func (m *MockDocumentService) PublishDocument(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// ArchiveDocument 模拟归档文档
func (m *MockDocumentService) ArchiveDocument(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// RegisterDocumentOnBlockchain 模拟在区块链上注册文档
func (m *MockDocumentService) RegisterDocumentOnBlockchain(ctx context.Context, id uuid.UUID) (string, error) {
	args := m.Called(ctx, id)
	return args.String(0), args.Error(1)
}
