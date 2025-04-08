package services

import (
	"context"
	"fmt"
	"time"

	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/models"
	"github.com/suoke-life/user-service/internal/repository"
)

// UserService 用户服务接口
type UserService interface {
	// 用户管理
	CreateUser(ctx context.Context, username, email string) (*models.User, error)
	GetUserByID(ctx context.Context, id string) (*models.User, error)
	GetUserByUsername(ctx context.Context, username string) (*models.User, error)
	GetUserByEmail(ctx context.Context, email string) (*models.User, error)
	UpdateUser(ctx context.Context, id string, update *models.UserUpdate) (*models.User, error)
	DeleteUser(ctx context.Context, id string) error
	ListUsers(ctx context.Context, filter *models.UserFilter) ([]*models.User, error)
	CountUsers(ctx context.Context) (int64, error)
	
	// 用户活动
	UpdateLastSeen(ctx context.Context, id string) error
	
	// 用户偏好
	UpdatePreferences(ctx context.Context, id string, prefs models.UserPrefs) error
	GetUserProfile(ctx context.Context, id string) (*models.UserProfile, error)
}

// DefaultUserService 默认用户服务实现
type DefaultUserService struct {
	userRepo repository.UserRepository
	logger   logger.Logger
}

// NewUserService 创建用户服务
func NewUserService(repo repository.UserRepository, log logger.Logger) UserService {
	return &DefaultUserService{
		userRepo: repo,
		logger:   log.With("component", "user_service"),
	}
}

// CreateUser 创建新用户
func (s *DefaultUserService) CreateUser(ctx context.Context, username, email string) (*models.User, error) {
	s.logger.Debug("创建用户", "username", username, "email", email)
	
	// 检查用户名是否已存在
	existingUser, err := s.userRepo.GetUserByUsername(ctx, username)
	if err != nil {
		return nil, fmt.Errorf("检查用户名失败: %w", err)
	}
	if existingUser != nil {
		return nil, fmt.Errorf("用户名已存在: %s", username)
	}
	
	// 检查邮箱是否已存在
	existingUser, err = s.userRepo.GetUserByEmail(ctx, email)
	if err != nil {
		return nil, fmt.Errorf("检查邮箱失败: %w", err)
	}
	if existingUser != nil {
		return nil, fmt.Errorf("邮箱已存在: %s", email)
	}
	
	// 创建新用户
	user := models.NewUser(username, email)
	
	// 保存用户
	if err := s.userRepo.CreateUser(ctx, user); err != nil {
		return nil, fmt.Errorf("保存用户失败: %w", err)
	}
	
	return user, nil
}

// GetUserByID 通过ID获取用户
func (s *DefaultUserService) GetUserByID(ctx context.Context, id string) (*models.User, error) {
	s.logger.Debug("通过ID获取用户", "id", id)
	
	user, err := s.userRepo.GetUserByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("通过ID获取用户失败: %w", err)
	}
	
	if user == nil {
		return nil, fmt.Errorf("用户不存在: %s", id)
	}
	
	return user, nil
}

// GetUserByUsername 通过用户名获取用户
func (s *DefaultUserService) GetUserByUsername(ctx context.Context, username string) (*models.User, error) {
	s.logger.Debug("通过用户名获取用户", "username", username)
	
	user, err := s.userRepo.GetUserByUsername(ctx, username)
	if err != nil {
		return nil, fmt.Errorf("通过用户名获取用户失败: %w", err)
	}
	
	if user == nil {
		return nil, fmt.Errorf("用户不存在: %s", username)
	}
	
	return user, nil
}

// GetUserByEmail 通过邮箱获取用户
func (s *DefaultUserService) GetUserByEmail(ctx context.Context, email string) (*models.User, error) {
	s.logger.Debug("通过邮箱获取用户", "email", email)
	
	user, err := s.userRepo.GetUserByEmail(ctx, email)
	if err != nil {
		return nil, fmt.Errorf("通过邮箱获取用户失败: %w", err)
	}
	
	if user == nil {
		return nil, fmt.Errorf("用户不存在: %s", email)
	}
	
	return user, nil
}

// UpdateUser 更新用户信息
func (s *DefaultUserService) UpdateUser(ctx context.Context, id string, update *models.UserUpdate) (*models.User, error) {
	s.logger.Debug("更新用户", "id", id)
	
	// 获取用户
	user, err := s.userRepo.GetUserByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("获取用户失败: %w", err)
	}
	
	if user == nil {
		return nil, fmt.Errorf("用户不存在: %s", id)
	}
	
	// 应用更新
	if update.DisplayName != nil {
		user.DisplayName = *update.DisplayName
	}
	
	if update.Avatar != nil {
		user.Avatar = *update.Avatar
	}
	
	if update.Bio != nil {
		user.Bio = *update.Bio
	}
	
	if update.Phone != nil {
		user.Phone = *update.Phone
	}
	
	if update.Preferences != nil {
		user.Preferences = *update.Preferences
	}
	
	// 更新时间戳
	user.UpdatedAt = time.Now()
	
	// 保存更新
	if err := s.userRepo.UpdateUser(ctx, user); err != nil {
		return nil, fmt.Errorf("更新用户失败: %w", err)
	}
	
	return user, nil
}

// DeleteUser 删除用户
func (s *DefaultUserService) DeleteUser(ctx context.Context, id string) error {
	s.logger.Debug("删除用户", "id", id)
	
	if err := s.userRepo.DeleteUser(ctx, id); err != nil {
		return fmt.Errorf("删除用户失败: %w", err)
	}
	
	return nil
}

// ListUsers 列出用户
func (s *DefaultUserService) ListUsers(ctx context.Context, filter *models.UserFilter) ([]*models.User, error) {
	s.logger.Debug("列出用户", "filter", filter)
	
	// 使用默认过滤器（如果未提供）
	if filter == nil {
		filter = &models.UserFilter{
			Limit:     50,
			Offset:    0,
			SortBy:    "created_at",
			SortOrder: "desc",
		}
	}
	
	// 应用默认限制（如果未提供）
	if filter.Limit <= 0 {
		filter.Limit = 50
	} else if filter.Limit > 100 {
		filter.Limit = 100 // 限制最大数量
	}
	
	users, err := s.userRepo.ListUsers(ctx, filter)
	if err != nil {
		return nil, fmt.Errorf("列出用户失败: %w", err)
	}
	
	return users, nil
}

// CountUsers 统计用户数量
func (s *DefaultUserService) CountUsers(ctx context.Context) (int64, error) {
	s.logger.Debug("统计用户数量")
	
	count, err := s.userRepo.CountUsers(ctx)
	if err != nil {
		return 0, fmt.Errorf("统计用户数量失败: %w", err)
	}
	
	return count, nil
}

// UpdateLastSeen 更新用户最后在线时间
func (s *DefaultUserService) UpdateLastSeen(ctx context.Context, id string) error {
	s.logger.Debug("更新用户最后在线时间", "id", id)
	
	if err := s.userRepo.UpdateLastSeen(ctx, id); err != nil {
		return fmt.Errorf("更新用户最后在线时间失败: %w", err)
	}
	
	return nil
}

// UpdatePreferences 更新用户偏好设置
func (s *DefaultUserService) UpdatePreferences(ctx context.Context, id string, prefs models.UserPrefs) error {
	s.logger.Debug("更新用户偏好设置", "id", id)
	
	if err := s.userRepo.UpdatePreferences(ctx, id, prefs); err != nil {
		return fmt.Errorf("更新用户偏好设置失败: %w", err)
	}
	
	return nil
}

// GetUserProfile 获取用户资料
func (s *DefaultUserService) GetUserProfile(ctx context.Context, id string) (*models.UserProfile, error) {
	s.logger.Debug("获取用户资料", "id", id)
	
	user, err := s.userRepo.GetUserByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("获取用户失败: %w", err)
	}
	
	if user == nil {
		return nil, fmt.Errorf("用户不存在: %s", id)
	}
	
	return user.ToProfile(), nil
} 