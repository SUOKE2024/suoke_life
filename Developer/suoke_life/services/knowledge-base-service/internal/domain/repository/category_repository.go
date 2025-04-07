package repository

import (
    "context"
    
    "github.com/google/uuid"
    
    "knowledge-base-service/internal/domain/entity"
)

// CategoryRepository 分类存储库接口
type CategoryRepository interface {
    // FindByID 通过ID查找分类
    FindByID(ctx context.Context, id uuid.UUID) (*entity.Category, error)
    
    // FindAll 查找所有分类
    FindAll(ctx context.Context) ([]*entity.Category, error)
    
    // FindByParent 查找父分类下的子分类
    FindByParent(ctx context.Context, parentID *uuid.UUID) ([]*entity.Category, error)
    
    // FindByPath 通过路径查找分类
    FindByPath(ctx context.Context, path string) (*entity.Category, error)
    
    // Save 保存分类
    Save(ctx context.Context, category *entity.Category) error
    
    // Update 更新分类
    Update(ctx context.Context, category *entity.Category) error
    
    // Delete 删除分类
    Delete(ctx context.Context, id uuid.UUID) error
}