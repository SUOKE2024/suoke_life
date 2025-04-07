package mocks

import (
	"context"
	
	"github.com/google/uuid"
	"github.com/stretchr/testify/mock"
	
	"knowledge-base-service/internal/domain/entity"
)

// MockCategoryRepository 模拟分类存储库
type MockCategoryRepository struct {
	mock.Mock
}

// FindByID 通过ID查找分类
func (m *MockCategoryRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Category, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Category), args.Error(1)
}

// FindAll 查找所有分类
func (m *MockCategoryRepository) FindAll(ctx context.Context) ([]*entity.Category, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*entity.Category), args.Error(1)
}

// FindByParent 查找父分类下的子分类
func (m *MockCategoryRepository) FindByParent(ctx context.Context, parentID *uuid.UUID) ([]*entity.Category, error) {
	args := m.Called(ctx, parentID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*entity.Category), args.Error(1)
}

// FindByPath 通过路径查找分类
func (m *MockCategoryRepository) FindByPath(ctx context.Context, path string) (*entity.Category, error) {
	args := m.Called(ctx, path)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Category), args.Error(1)
}

// Save 保存分类
func (m *MockCategoryRepository) Save(ctx context.Context, category *entity.Category) error {
	args := m.Called(ctx, category)
	return args.Error(0)
}

// Update 更新分类
func (m *MockCategoryRepository) Update(ctx context.Context, category *entity.Category) error {
	args := m.Called(ctx, category)
	return args.Error(0)
}

// Delete 删除分类
func (m *MockCategoryRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
} 