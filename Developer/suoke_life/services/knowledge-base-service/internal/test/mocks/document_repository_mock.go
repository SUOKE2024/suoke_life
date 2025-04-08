package mocks

import (
	"context"

	"github.com/google/uuid"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
)

// MockDocumentRepository 文档仓储接口的模拟实现
type MockDocumentRepository struct {
	mock.Mock
}

// FindByID 模拟根据ID查找文档
func (m *MockDocumentRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
	args := m.Called(ctx, id)

	if doc := args.Get(0); doc != nil {
		return doc.(*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// FindByCategory 模拟根据分类查找文档
func (m *MockDocumentRepository) FindByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error) {
	args := m.Called(ctx, categoryID)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// FindByTags 模拟根据标签查找文档
func (m *MockDocumentRepository) FindByTags(ctx context.Context, tags []string) ([]*entity.Document, error) {
	args := m.Called(ctx, tags)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// Search 模拟全文搜索
func (m *MockDocumentRepository) Search(ctx context.Context, query string) ([]*entity.Document, error) {
	args := m.Called(ctx, query)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// SemanticSearch 模拟语义搜索
func (m *MockDocumentRepository) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	args := m.Called(ctx, query, limit)

	if docs := args.Get(0); docs != nil {
		return docs.([]*entity.Document), args.Error(1)
	}

	return nil, args.Error(1)
}

// Save 模拟保存文档
func (m *MockDocumentRepository) Save(ctx context.Context, document *entity.Document) error {
	args := m.Called(ctx, document)
	return args.Error(0)
}

// Update 模拟更新文档
func (m *MockDocumentRepository) Update(ctx context.Context, document *entity.Document) error {
	args := m.Called(ctx, document)
	return args.Error(0)
}

// Delete 模拟删除文档
func (m *MockDocumentRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// RegisterOnBlockchain 模拟在区块链上注册文档
func (m *MockDocumentRepository) RegisterOnBlockchain(ctx context.Context, document *entity.Document) (string, error) {
	args := m.Called(ctx, document)
	return args.String(0), args.Error(1)
}
