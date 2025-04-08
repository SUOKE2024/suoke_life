package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/jmoiron/sqlx"
	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/models"
)

// UserRepository 用户仓库接口
type UserRepository interface {
	// 基础CRUD操作
	CreateUser(ctx context.Context, user *models.User) error
	GetUserByID(ctx context.Context, id string) (*models.User, error)
	GetUserByUsername(ctx context.Context, username string) (*models.User, error)
	GetUserByEmail(ctx context.Context, email string) (*models.User, error)
	UpdateUser(ctx context.Context, user *models.User) error
	DeleteUser(ctx context.Context, id string) error
	
	// 查询操作
	ListUsers(ctx context.Context, filter *models.UserFilter) ([]*models.User, error)
	CountUsers(ctx context.Context) (int64, error)
	
	// 特殊操作
	UpdateLastSeen(ctx context.Context, id string) error
	UpdatePreferences(ctx context.Context, id string, prefs models.UserPrefs) error
}

// SQLUserRepository SQL实现的用户仓库
type SQLUserRepository struct {
	db     *sqlx.DB
	logger logger.Logger
}

// NewSQLUserRepository 创建SQL用户仓库
func NewSQLUserRepository(db *sqlx.DB, log logger.Logger) *SQLUserRepository {
	return &SQLUserRepository{
		db:     db,
		logger: log.With("component", "user_repository"),
	}
}

// CreateUser 创建新用户
func (r *SQLUserRepository) CreateUser(ctx context.Context, user *models.User) error {
	r.logger.Debug("创建用户", "username", user.Username, "email", user.Email)
	
	// 转换偏好设置为JSON
	prefsJSON, err := json.Marshal(user.Preferences)
	if err != nil {
		return fmt.Errorf("序列化用户偏好失败: %w", err)
	}
	
	query := `
		INSERT INTO users (
			id, username, email, phone, display_name, avatar, bio, 
			preferences, created_at, updated_at, last_seen
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
		)
	`
	
	_, err = r.db.ExecContext(
		ctx, 
		query,
		user.ID,
		user.Username,
		user.Email,
		user.Phone,
		user.DisplayName,
		user.Avatar,
		user.Bio,
		prefsJSON,
		user.CreatedAt,
		user.UpdatedAt,
		user.LastSeen,
	)
	
	if err != nil {
		return fmt.Errorf("插入用户数据失败: %w", err)
	}
	
	return nil
}

// GetUserByID 通过ID获取用户
func (r *SQLUserRepository) GetUserByID(ctx context.Context, id string) (*models.User, error) {
	r.logger.Debug("通过ID获取用户", "id", id)
	
	var user models.User
	var prefsJSON []byte
	
	query := `
		SELECT 
			id, username, email, phone, display_name, avatar, bio, 
			preferences, created_at, updated_at, last_seen
		FROM users
		WHERE id = $1
	`
	
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.Phone,
		&user.DisplayName,
		&user.Avatar,
		&user.Bio,
		&prefsJSON,
		&user.CreatedAt,
		&user.UpdatedAt,
		&user.LastSeen,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // 未找到用户
		}
		return nil, fmt.Errorf("查询用户数据失败: %w", err)
	}
	
	// 解析偏好设置
	if err := json.Unmarshal(prefsJSON, &user.Preferences); err != nil {
		return nil, fmt.Errorf("解析用户偏好失败: %w", err)
	}
	
	return &user, nil
}

// GetUserByUsername 通过用户名获取用户
func (r *SQLUserRepository) GetUserByUsername(ctx context.Context, username string) (*models.User, error) {
	r.logger.Debug("通过用户名获取用户", "username", username)
	
	var user models.User
	var prefsJSON []byte
	
	query := `
		SELECT 
			id, username, email, phone, display_name, avatar, bio, 
			preferences, created_at, updated_at, last_seen
		FROM users
		WHERE username = $1
	`
	
	err := r.db.QueryRowContext(ctx, query, username).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.Phone,
		&user.DisplayName,
		&user.Avatar,
		&user.Bio,
		&prefsJSON,
		&user.CreatedAt,
		&user.UpdatedAt,
		&user.LastSeen,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // 未找到用户
		}
		return nil, fmt.Errorf("查询用户数据失败: %w", err)
	}
	
	// 解析偏好设置
	if err := json.Unmarshal(prefsJSON, &user.Preferences); err != nil {
		return nil, fmt.Errorf("解析用户偏好失败: %w", err)
	}
	
	return &user, nil
}

// GetUserByEmail 通过邮箱获取用户
func (r *SQLUserRepository) GetUserByEmail(ctx context.Context, email string) (*models.User, error) {
	r.logger.Debug("通过邮箱获取用户", "email", email)
	
	var user models.User
	var prefsJSON []byte
	
	query := `
		SELECT 
			id, username, email, phone, display_name, avatar, bio, 
			preferences, created_at, updated_at, last_seen
		FROM users
		WHERE email = $1
	`
	
	err := r.db.QueryRowContext(ctx, query, email).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.Phone,
		&user.DisplayName,
		&user.Avatar,
		&user.Bio,
		&prefsJSON,
		&user.CreatedAt,
		&user.UpdatedAt,
		&user.LastSeen,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // 未找到用户
		}
		return nil, fmt.Errorf("查询用户数据失败: %w", err)
	}
	
	// 解析偏好设置
	if err := json.Unmarshal(prefsJSON, &user.Preferences); err != nil {
		return nil, fmt.Errorf("解析用户偏好失败: %w", err)
	}
	
	return &user, nil
}

// UpdateUser 更新用户信息
func (r *SQLUserRepository) UpdateUser(ctx context.Context, user *models.User) error {
	r.logger.Debug("更新用户", "id", user.ID)
	
	// 更新时间戳
	user.UpdatedAt = time.Now()
	
	// 转换偏好设置为JSON
	prefsJSON, err := json.Marshal(user.Preferences)
	if err != nil {
		return fmt.Errorf("序列化用户偏好失败: %w", err)
	}
	
	query := `
		UPDATE users
		SET 
			username = $1,
			email = $2,
			phone = $3,
			display_name = $4,
			avatar = $5,
			bio = $6,
			preferences = $7,
			updated_at = $8,
			last_seen = $9
		WHERE id = $10
	`
	
	result, err := r.db.ExecContext(
		ctx,
		query,
		user.Username,
		user.Email,
		user.Phone,
		user.DisplayName,
		user.Avatar,
		user.Bio,
		prefsJSON,
		user.UpdatedAt,
		user.LastSeen,
		user.ID,
	)
	
	if err != nil {
		return fmt.Errorf("更新用户数据失败: %w", err)
	}
	
	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("获取影响行数失败: %w", err)
	}
	
	if rows == 0 {
		return fmt.Errorf("用户不存在: %s", user.ID)
	}
	
	return nil
}

// DeleteUser 删除用户
func (r *SQLUserRepository) DeleteUser(ctx context.Context, id string) error {
	r.logger.Debug("删除用户", "id", id)
	
	query := `DELETE FROM users WHERE id = $1`
	
	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("删除用户失败: %w", err)
	}
	
	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("获取影响行数失败: %w", err)
	}
	
	if rows == 0 {
		return fmt.Errorf("用户不存在: %s", id)
	}
	
	return nil
}

// ListUsers 列出用户
func (r *SQLUserRepository) ListUsers(ctx context.Context, filter *models.UserFilter) ([]*models.User, error) {
	r.logger.Debug("列出用户", "filter", filter)
	
	// 构建查询
	baseQuery := `
		SELECT 
			id, username, email, phone, display_name, avatar, bio, 
			preferences, created_at, updated_at, last_seen
		FROM users
	`
	
	// 构建WHERE子句
	whereClause := ""
	args := []interface{}{}
	argIndex := 1
	
	if filter.Username != "" {
		whereClause += fmt.Sprintf(" username LIKE $%d", argIndex)
		args = append(args, "%"+filter.Username+"%")
		argIndex++
	}
	
	if filter.Email != "" {
		if whereClause != "" {
			whereClause += " AND"
		}
		whereClause += fmt.Sprintf(" email LIKE $%d", argIndex)
		args = append(args, "%"+filter.Email+"%")
		argIndex++
	}
	
	if filter.DisplayName != "" {
		if whereClause != "" {
			whereClause += " AND"
		}
		whereClause += fmt.Sprintf(" display_name LIKE $%d", argIndex)
		args = append(args, "%"+filter.DisplayName+"%")
		argIndex++
	}
	
	// 添加WHERE子句（如果有）
	if whereClause != "" {
		baseQuery += " WHERE" + whereClause
	}
	
	// 添加排序
	if filter.SortBy != "" {
		baseQuery += fmt.Sprintf(" ORDER BY %s", filter.SortBy)
		if filter.SortOrder != "" {
			baseQuery += " " + filter.SortOrder
		} else {
			baseQuery += " ASC"
		}
	} else {
		baseQuery += " ORDER BY created_at DESC"
	}
	
	// 添加分页
	if filter.Limit > 0 {
		baseQuery += fmt.Sprintf(" LIMIT $%d", argIndex)
		args = append(args, filter.Limit)
		argIndex++
		
		if filter.Offset > 0 {
			baseQuery += fmt.Sprintf(" OFFSET $%d", argIndex)
			args = append(args, filter.Offset)
		}
	}
	
	// 执行查询
	rows, err := r.db.QueryContext(ctx, baseQuery, args...)
	if err != nil {
		return nil, fmt.Errorf("查询用户列表失败: %w", err)
	}
	defer rows.Close()
	
	// 解析结果
	var users []*models.User
	
	for rows.Next() {
		var user models.User
		var prefsJSON []byte
		
		err := rows.Scan(
			&user.ID,
			&user.Username,
			&user.Email,
			&user.Phone,
			&user.DisplayName,
			&user.Avatar,
			&user.Bio,
			&prefsJSON,
			&user.CreatedAt,
			&user.UpdatedAt,
			&user.LastSeen,
		)
		
		if err != nil {
			return nil, fmt.Errorf("扫描用户数据失败: %w", err)
		}
		
		// 解析偏好设置
		if err := json.Unmarshal(prefsJSON, &user.Preferences); err != nil {
			return nil, fmt.Errorf("解析用户偏好失败: %w", err)
		}
		
		users = append(users, &user)
	}
	
	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("行迭代失败: %w", err)
	}
	
	return users, nil
}

// CountUsers 统计用户数量
func (r *SQLUserRepository) CountUsers(ctx context.Context) (int64, error) {
	r.logger.Debug("统计用户数量")
	
	var count int64
	query := `SELECT COUNT(*) FROM users`
	
	err := r.db.QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("统计用户数量失败: %w", err)
	}
	
	return count, nil
}

// UpdateLastSeen 更新用户最后在线时间
func (r *SQLUserRepository) UpdateLastSeen(ctx context.Context, id string) error {
	r.logger.Debug("更新用户最后在线时间", "id", id)
	
	now := time.Now()
	query := `UPDATE users SET last_seen = $1 WHERE id = $2`
	
	result, err := r.db.ExecContext(ctx, query, now, id)
	if err != nil {
		return fmt.Errorf("更新最后在线时间失败: %w", err)
	}
	
	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("获取影响行数失败: %w", err)
	}
	
	if rows == 0 {
		return fmt.Errorf("用户不存在: %s", id)
	}
	
	return nil
}

// UpdatePreferences 更新用户偏好设置
func (r *SQLUserRepository) UpdatePreferences(ctx context.Context, id string, prefs models.UserPrefs) error {
	r.logger.Debug("更新用户偏好设置", "id", id)
	
	// 转换偏好设置为JSON
	prefsJSON, err := json.Marshal(prefs)
	if err != nil {
		return fmt.Errorf("序列化用户偏好失败: %w", err)
	}
	
	now := time.Now()
	query := `UPDATE users SET preferences = $1, updated_at = $2 WHERE id = $3`
	
	result, err := r.db.ExecContext(ctx, query, prefsJSON, now, id)
	if err != nil {
		return fmt.Errorf("更新偏好设置失败: %w", err)
	}
	
	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("获取影响行数失败: %w", err)
	}
	
	if rows == 0 {
		return fmt.Errorf("用户不存在: %s", id)
	}
	
	return nil
} 