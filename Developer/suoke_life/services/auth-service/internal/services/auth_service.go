package services

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/suoke-life/auth-service/internal/models"
	"github.com/suoke-life/auth-service/internal/repository"
	"github.com/suoke-life/shared/pkg/logger"
)

// 定义错误常量
var (
	ErrInvalidCredentials = errors.New("无效的凭据")
	ErrUserNotFound       = errors.New("用户不存在")
	ErrEmailExists        = errors.New("邮箱已存在")
	ErrUsernameExists     = errors.New("用户名已存在")
)

// AuthService 认证服务接口
type AuthService interface {
	Register(ctx context.Context, reg *models.UserRegistration) (*models.User, error)
	Login(ctx context.Context, login *models.UserLogin) (*models.User, error)
	ValidateCredentials(ctx context.Context, email, password string) (*models.User, error)
	GetUserByID(ctx context.Context, userID string) (*models.User, error)
	ResetPassword(ctx context.Context, userID, newPassword string) error
	ListUsers(ctx context.Context, offset, limit int) ([]*models.User, int, error)
}

// DefaultAuthService 默认认证服务实现
type DefaultAuthService struct {
	userRepo repository.UserRepository
	logger   logger.Logger
}

// 确保DefaultAuthService实现了AuthService接口
var _ AuthService = (*DefaultAuthService)(nil)

// NewAuthService 创建新的认证服务
func NewAuthService(userRepo repository.UserRepository, log logger.Logger) *DefaultAuthService {
	return &DefaultAuthService{
		userRepo: userRepo,
		logger:   log.With("service", "auth"),
	}
}

// Register 注册新用户
func (s *DefaultAuthService) Register(ctx context.Context, reg *models.UserRegistration) (*models.User, error) {
	// 检查邮箱是否已存在
	existingUser, err := s.userRepo.GetByEmail(ctx, reg.Email)
	if err == nil && existingUser != nil {
		return nil, ErrEmailExists
	}

	// 检查用户名是否已存在
	existingUser, err = s.userRepo.GetByUsername(ctx, reg.Username)
	if err == nil && existingUser != nil {
		return nil, ErrUsernameExists
	}

	// 创建新用户
	user := &models.User{
		Username:       reg.Username,
		Email:          reg.Email,
		Role:           models.RoleUser, // 默认为普通用户
		Active:         true,
		EmailVerified:  false,
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
	}

	// 设置密码
	if err := user.SetPassword(reg.Password); err != nil {
		s.logger.Error("设置密码失败", "error", err)
		return nil, fmt.Errorf("设置密码失败: %w", err)
	}

	// 生成唯一ID
	user.ID = models.GenerateUniqueID()

	// 保存用户
	if err := s.userRepo.Create(ctx, user); err != nil {
		s.logger.Error("创建用户失败", "error", err)
		return nil, fmt.Errorf("创建用户失败: %w", err)
	}

	return user, nil
}

// Login 用户登录
func (s *DefaultAuthService) Login(ctx context.Context, login *models.UserLogin) (*models.User, error) {
	// 验证凭据
	user, err := s.ValidateCredentials(ctx, login.Username, login.Password)
	if err != nil {
		return nil, err
	}

	// 更新最后登录时间
	if err := s.userRepo.UpdateLastLogin(ctx, user.ID); err != nil {
		s.logger.Warn("更新最后登录时间失败", "error", err, "user", user.ID)
		// 不返回错误，继续登录流程
	}

	return user, nil
}

// ValidateCredentials 验证用户凭据
func (s *DefaultAuthService) ValidateCredentials(ctx context.Context, username, password string) (*models.User, error) {
	// 通过用户名获取用户
	user, err := s.userRepo.GetByUsername(ctx, username)
	if err != nil {
		return nil, ErrInvalidCredentials
	}

	// 检查用户是否激活
	if !user.Active {
		return nil, errors.New("用户已被禁用")
	}

	// 验证密码
	if !user.CheckPassword(password) {
		return nil, ErrInvalidCredentials
	}

	return user, nil
}

// GetUserByID 通过ID获取用户
func (s *DefaultAuthService) GetUserByID(ctx context.Context, userID string) (*models.User, error) {
	user, err := s.userRepo.GetByID(ctx, userID)
	if err != nil {
		return nil, ErrUserNotFound
	}
	return user, nil
}

// ResetPassword 重置用户密码
func (s *DefaultAuthService) ResetPassword(ctx context.Context, userID, newPassword string) error {
	// 获取用户
	user, err := s.userRepo.GetByID(ctx, userID)
	if err != nil {
		return ErrUserNotFound
	}

	// 设置新密码
	if err := user.SetPassword(newPassword); err != nil {
		return fmt.Errorf("设置密码失败: %w", err)
	}

	// 更新用户信息
	if err := s.userRepo.Update(ctx, user); err != nil {
		return fmt.Errorf("更新用户失败: %w", err)
	}

	return nil
}

// ListUsers 列出用户
func (s *DefaultAuthService) ListUsers(ctx context.Context, offset, limit int) ([]*models.User, int, error) {
	// 获取用户列表
	users, err := s.userRepo.List(ctx, offset, limit)
	if err != nil {
		return nil, 0, fmt.Errorf("列出用户失败: %w", err)
	}

	// 获取用户总数
	count, err := s.userRepo.Count(ctx)
	if err != nil {
		return nil, 0, fmt.Errorf("获取用户总数失败: %w", err)
	}

	return users, count, nil
}