package repository

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"

	"github.com/jmoiron/sqlx"
	"github.com/suoke-life/auth-service/internal/models"
	"github.com/suoke-life/shared/pkg/logger"
)

// UserRepository 用户存储库接口
type UserRepository interface {
	Create(ctx context.Context, user *models.User) error
	GetByID(ctx context.Context, id string) (*models.User, error)
	GetByEmail(ctx context.Context, email string) (*models.User, error)
	GetByUsername(ctx context.Context, username string) (*models.User, error)
	Update(ctx context.Context, user *models.User) error
	UpdateLastLogin(ctx context.Context, userID string) error
	Delete(ctx context.Context, userID string) error
	List(ctx context.Context, offset, limit int) ([]*models.User, error)
	Count(ctx context.Context) (int, error)
}

// SQLUserRepository SQL用户存储库实现
type SQLUserRepository struct {
	db     *sqlx.DB
	logger logger.Logger
}

// 确保SQLUserRepository实现了UserRepository接口
var _ UserRepository = (*SQLUserRepository)(nil)

// NewSQLUserRepository 创建新的SQL用户存储库
func NewSQLUserRepository(db *sqlx.DB, log logger.Logger) *SQLUserRepository {
	return &SQLUserRepository{
		db:     db,
		logger: log.With("repository", "user"),
	}
}

// Create 创建新用户
func (r *SQLUserRepository) Create(ctx context.Context, user *models.User) error {
	query := `
		INSERT INTO users (
			id, username, email, password_hash, role, active, 
			email_verified, created_at, updated_at, last_login
		) VALUES (
			:id, :username, :email, :password_hash, :role, :active, 
			:email_verified, :created_at, :updated_at, :last_login
		)
	`

	user.CreatedAt = time.Now()
	user.UpdatedAt = user.CreatedAt

	_, err := r.db.NamedExecContext(ctx, query, user)
	if err != nil {
		r.logger.Error("创建用户失败", "error", err, "user", user.ID)
		return fmt.Errorf("创建用户失败: %w", err)
	}

	return nil
}

// GetByID 通过ID获取用户
func (r *SQLUserRepository) GetByID(ctx context.Context, id string) (*models.User, error) {
	query := `
		SELECT * FROM users WHERE id = $1
	`

	var user models.User
	err := r.db.GetContext(ctx, &user, query, id)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, fmt.Errorf("未找到用户: %s", id)
		}
		r.logger.Error("获取用户失败", "error", err, "id", id)
		return nil, fmt.Errorf("获取用户失败: %w", err)
	}

	return &user, nil
}

// GetByEmail 通过邮箱获取用户
func (r *SQLUserRepository) GetByEmail(ctx context.Context, email string) (*models.User, error) {
	query := `
		SELECT * FROM users WHERE email = $1
	`

	var user models.User
	err := r.db.GetContext(ctx, &user, query, email)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, fmt.Errorf("未找到用户: %s", email)
		}
		r.logger.Error("获取用户失败", "error", err, "email", email)
		return nil, fmt.Errorf("获取用户失败: %w", err)
	}

	return &user, nil
}

// GetByUsername 通过用户名获取用户
func (r *SQLUserRepository) GetByUsername(ctx context.Context, username string) (*models.User, error) {
	query := `
		SELECT * FROM users WHERE username = $1
	`

	var user models.User
	err := r.db.GetContext(ctx, &user, query, username)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, fmt.Errorf("未找到用户: %s", username)
		}
		r.logger.Error("获取用户失败", "error", err, "username", username)
		return nil, fmt.Errorf("获取用户失败: %w", err)
	}

	return &user, nil
}

// Update 更新用户信息
func (r *SQLUserRepository) Update(ctx context.Context, user *models.User) error {
	query := `
		UPDATE users
		SET username = :username,
			email = :email,
			password_hash = :password_hash,
			role = :role,
			active = :active,
			email_verified = :email_verified,
			updated_at = :updated_at
		WHERE id = :id
	`

	user.UpdatedAt = time.Now()

	_, err := r.db.NamedExecContext(ctx, query, user)
	if err != nil {
		r.logger.Error("更新用户失败", "error", err, "user", user.ID)
		return fmt.Errorf("更新用户失败: %w", err)
	}

	return nil
}

// UpdateLastLogin 更新用户最后登录时间
func (r *SQLUserRepository) UpdateLastLogin(ctx context.Context, userID string) error {
	query := `
		UPDATE users
		SET last_login = $1
		WHERE id = $2
	`

	now := time.Now()
	_, err := r.db.ExecContext(ctx, query, now, userID)
	if err != nil {
		r.logger.Error("更新用户最后登录时间失败", "error", err, "user", userID)
		return fmt.Errorf("更新用户最后登录时间失败: %w", err)
	}

	return nil
}

// Delete 删除用户
func (r *SQLUserRepository) Delete(ctx context.Context, userID string) error {
	query := `
		DELETE FROM users WHERE id = $1
	`

	_, err := r.db.ExecContext(ctx, query, userID)
	if err != nil {
		r.logger.Error("删除用户失败", "error", err, "user", userID)
		return fmt.Errorf("删除用户失败: %w", err)
	}

	return nil
}

// List 列出用户
func (r *SQLUserRepository) List(ctx context.Context, offset, limit int) ([]*models.User, error) {
	query := `
		SELECT * FROM users
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	users := []*models.User{}
	err := r.db.SelectContext(ctx, &users, query, limit, offset)
	if err != nil {
		r.logger.Error("列出用户失败", "error", err)
		return nil, fmt.Errorf("列出用户失败: %w", err)
	}

	return users, nil
}

// Count 获取用户总数
func (r *SQLUserRepository) Count(ctx context.Context) (int, error) {
	query := `
		SELECT COUNT(*) FROM users
	`

	var count int
	err := r.db.GetContext(ctx, &count, query)
	if err != nil {
		r.logger.Error("获取用户总数失败", "error", err)
		return 0, fmt.Errorf("获取用户总数失败: %w", err)
	}

	return count, nil
} 