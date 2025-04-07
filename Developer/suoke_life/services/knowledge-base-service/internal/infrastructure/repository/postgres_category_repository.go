package repository

import (
    "context"
    "database/sql"
    "fmt"
    
    "github.com/google/uuid"
    
    "knowledge-base-service/internal/domain/entity"
    "knowledge-base-service/internal/domain/repository"
    "knowledge-base-service/internal/infrastructure/database"
)

// PostgresCategoryRepository PostgreSQL分类存储库实现
type PostgresCategoryRepository struct {
    db database.DBManager
}

// NewCategoryRepository 创建新的分类存储库
func NewCategoryRepository(db database.DBManager) repository.CategoryRepository {
    return &PostgresCategoryRepository{db: db}
}

// FindByID 通过ID查找分类
func (r *PostgresCategoryRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Category, error) {
    query := `
        SELECT id, name, description, parent_id, path, created_at, updated_at
        FROM categories
        WHERE id = $1
    `
    
    row := r.db.QueryRow(ctx, query, id)
    
    category, err := r.scanCategory(row)
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, fmt.Errorf("查询分类失败: %w", err)
    }
    
    // 加载子分类
    children, err := r.FindByParent(ctx, &id)
    if err != nil {
        return nil, err
    }
    
    category.Children = children
    
    return category, nil
}

// FindAll 查找所有分类
func (r *PostgresCategoryRepository) FindAll(ctx context.Context) ([]*entity.Category, error) {
    // 只获取根分类
    rootCategories, err := r.FindByParent(ctx, nil)
    if err != nil {
        return nil, err
    }
    
    // 对于每个根分类，递归加载其子分类
    for _, category := range rootCategories {
        children, err := r.loadCategoryTree(ctx, category.ID)
        if err != nil {
            return nil, err
        }
        category.Children = children
    }
    
    return rootCategories, nil
}

// FindByParent 查找父分类下的子分类
func (r *PostgresCategoryRepository) FindByParent(ctx context.Context, parentID *uuid.UUID) ([]*entity.Category, error) {
    var query string
    var args []interface{}
    
    if parentID == nil {
        // 查找根分类
        query = `
            SELECT id, name, description, parent_id, path, created_at, updated_at
            FROM categories
            WHERE parent_id IS NULL
            ORDER BY name
        `
    } else {
        // 查找特定父分类下的子分类
        query = `
            SELECT id, name, description, parent_id, path, created_at, updated_at
            FROM categories
            WHERE parent_id = $1
            ORDER BY name
        `
        args = append(args, *parentID)
    }
    
    rows, err := r.db.Query(ctx, query, args...)
    if err != nil {
        return nil, fmt.Errorf("查询分类失败: %w", err)
    }
    defer rows.Close()
    
    return r.scanCategories(rows)
}

// FindByPath 通过路径查找分类
func (r *PostgresCategoryRepository) FindByPath(ctx context.Context, path string) (*entity.Category, error) {
    query := `
        SELECT id, name, description, parent_id, path, created_at, updated_at
        FROM categories
        WHERE path = $1
    `
    
    row := r.db.QueryRow(ctx, query, path)
    
    category, err := r.scanCategory(row)
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, fmt.Errorf("查询分类失败: %w", err)
    }
    
    // 加载子分类
    children, err := r.FindByParent(ctx, &category.ID)
    if err != nil {
        return nil, err
    }
    
    category.Children = children
    
    return category, nil
}

// Save 保存分类
func (r *PostgresCategoryRepository) Save(ctx context.Context, category *entity.Category) error {
    // 开始事务
    tx, err := r.db.Begin(ctx)
    if err != nil {
        return fmt.Errorf("开始事务失败: %w", err)
    }
    defer tx.Rollback()
    
    // 保存分类
    query := `
        INSERT INTO categories (
            id, name, description, parent_id, path, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7
        )
    `
    
    _, err = tx.Exec(query,
        category.ID,
        category.Name,
        category.Description,
        category.ParentID,
        category.Path,
        category.CreatedAt,
        category.UpdatedAt,
    )
    
    if err != nil {
        return fmt.Errorf("插入分类失败: %w", err)
    }
    
    // 递归保存子分类
    for _, child := range category.Children {
        err = r.saveCategory(ctx, tx, child)
        if err != nil {
            return err
        }
    }
    
    // 提交事务
    err = tx.Commit()
    if err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }
    
    return nil
}

// Update 更新分类
func (r *PostgresCategoryRepository) Update(ctx context.Context, category *entity.Category) error {
    // 开始事务
    tx, err := r.db.Begin(ctx)
    if err != nil {
        return fmt.Errorf("开始事务失败: %w", err)
    }
    defer tx.Rollback()
    
    // 更新分类
    query := `
        UPDATE categories SET
            name = $1,
            description = $2,
            parent_id = $3,
            path = $4,
            updated_at = $5
        WHERE id = $6
    `
    
    _, err = tx.Exec(query,
        category.Name,
        category.Description,
        category.ParentID,
        category.Path,
        category.UpdatedAt,
        category.ID,
    )
    
    if err != nil {
        return fmt.Errorf("更新分类失败: %w", err)
    }
    
    // 更新子分类
    for _, child := range category.Children {
        // 检查子分类是否已存在
        existingChild, err := r.FindByID(ctx, child.ID)
        if err != nil {
            return err
        }
        
        if existingChild != nil {
            // 更新现有子分类
            err = r.Update(ctx, child)
        } else {
            // 保存新子分类
            err = r.saveCategory(ctx, tx, child)
        }
        
        if err != nil {
            return err
        }
    }
    
    // 提交事务
    err = tx.Commit()
    if err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }
    
    return nil
}

// Delete 删除分类
func (r *PostgresCategoryRepository) Delete(ctx context.Context, id uuid.UUID) error {
    // 检查是否有文档使用该分类
    var count int
    countQuery := `
        SELECT COUNT(*) FROM documents WHERE category_id = $1
    `
    
    err := r.db.QueryRow(ctx, countQuery, id).Scan(&count)
    if err != nil {
        return fmt.Errorf("检查分类使用情况失败: %w", err)
    }
    
    if count > 0 {
        return fmt.Errorf("无法删除分类，有 %d 个文档使用此分类", count)
    }
    
    // 获取子分类
    children, err := r.FindByParent(ctx, &id)
    if err != nil {
        return err
    }
    
    // 如果有子分类，先删除子分类
    if len(children) > 0 {
        for _, child := range children {
            err = r.Delete(ctx, child.ID)
            if err != nil {
                return err
            }
        }
    }
    
    // 删除分类
    query := `DELETE FROM categories WHERE id = $1`
    _, err = r.db.Exec(ctx, query, id)
    if err != nil {
        return fmt.Errorf("删除分类失败: %w", err)
    }
    
    return nil
}

// 辅助方法

// scanCategory 扫描单个分类
func (r *PostgresCategoryRepository) scanCategory(row database.Row) (*entity.Category, error) {
    var category entity.Category
    var parentID sql.NullString
    
    err := row.Scan(
        &category.ID,
        &category.Name,
        &category.Description,
        &parentID,
        &category.Path,
        &category.CreatedAt,
        &category.UpdatedAt,
    )
    
    if err != nil {
        return nil, err
    }
    
    // 处理父ID
    if parentID.Valid {
        parentUUID, err := uuid.Parse(parentID.String)
        if err != nil {
            return nil, fmt.Errorf("解析父ID失败: %w", err)
        }
        category.ParentID = &parentUUID
    }
    
    category.Children = []*entity.Category{}
    
    return &category, nil
}

// scanCategories 扫描多个分类
func (r *PostgresCategoryRepository) scanCategories(rows database.Rows) ([]*entity.Category, error) {
    var categories []*entity.Category
    
    for rows.Next() {
        category, err := r.scanCategory(rows)
        if err != nil {
            return nil, err
        }
        
        categories = append(categories, category)
    }
    
    if rows.Err() != nil {
        return nil, rows.Err()
    }
    
    return categories, nil
}

// loadCategoryTree 递归加载分类树
func (r *PostgresCategoryRepository) loadCategoryTree(ctx context.Context, parentID uuid.UUID) ([]*entity.Category, error) {
    children, err := r.FindByParent(ctx, &parentID)
    if err != nil {
        return nil, err
    }
    
    for _, child := range children {
        grandchildren, err := r.loadCategoryTree(ctx, child.ID)
        if err != nil {
            return nil, err
        }
        child.Children = grandchildren
    }
    
    return children, nil
}

// saveCategory 递归保存分类
func (r *PostgresCategoryRepository) saveCategory(ctx context.Context, tx database.Transaction, category *entity.Category) error {
    query := `
        INSERT INTO categories (
            id, name, description, parent_id, path, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7
        )
    `
    
    _, err := tx.Exec(query,
        category.ID,
        category.Name,
        category.Description,
        category.ParentID,
        category.Path,
        category.CreatedAt,
        category.UpdatedAt,
    )
    
    if err != nil {
        return fmt.Errorf("插入分类失败: %w", err)
    }
    
    // 递归保存子分类
    for _, child := range category.Children {
        err = r.saveCategory(ctx, tx, child)
        if err != nil {
            return err
        }
    }
    
    return nil
}