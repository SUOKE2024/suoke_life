package mocks

import (
	"context"

	"github.com/google/uuid"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
)

// MockCategoryRepository 分类仓储接口的模拟实现
type MockCategoryRepository struct {
	mock.Mock
}

// FindByID 模拟根据ID查找分类
func (m *MockCategoryRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Category, error) {
	args := m.Called(ctx, id)

	if cat := args.Get(0); cat != nil {
		return cat.(*entity.Category), args.Error(1)
	}

	return nil, args.Error(1)
}

// FindAll 模拟查找所有分类
func (m *MockCategoryRepository) FindAll(ctx context.Context) ([]*entity.Category, error) {
	args := m.Called(ctx)

	if categories := args.Get(0); categories != nil {
		return categories.([]*entity.Category), args.Error(1)
	}

	return nil, args.Error(1)
}

// FindByParent 模拟查找父分类下的子分类
func (m *MockCategoryRepository) FindByParent(ctx context.Context, parentID *uuid.UUID) ([]*entity.Category, error) {
	args := m.Called(ctx, parentID)

	if categories := args.Get(0); categories != nil {
		return categories.([]*entity.Category), args.Error(1)
	}

	return nil, args.Error(1)
}

// FindByPath 模拟通过路径查找分类
func (m *MockCategoryRepository) FindByPath(ctx context.Context, path string) (*entity.Category, error) {
	args := m.Called(ctx, path)

	if category := args.Get(0); category != nil {
		return category.(*entity.Category), args.Error(1)
	}

	return nil, args.Error(1)
}

// Save 模拟保存分类
func (m *MockCategoryRepository) Save(ctx context.Context, category *entity.Category) error {
	args := m.Called(ctx, category)
	return args.Error(0)
}

// Update 模拟更新分类
func (m *MockCategoryRepository) Update(ctx context.Context, category *entity.Category) error {
	args := m.Called(ctx, category)
	return args.Error(0)
}

// Delete 模拟删除分类
func (m *MockCategoryRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}
