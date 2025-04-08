package services

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/models"
)

// MockUserRepository 创建用户仓库的模拟实现
type MockUserRepository struct {
	mock.Mock
}

func (m *MockUserRepository) CreateUser(ctx context.Context, user *models.User) error {
	args := m.Called(ctx, user)
	return args.Error(0)
}

func (m *MockUserRepository) GetUserByID(ctx context.Context, id string) (*models.User, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) GetUserByUsername(ctx context.Context, username string) (*models.User, error) {
	args := m.Called(ctx, username)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) GetUserByEmail(ctx context.Context, email string) (*models.User, error) {
	args := m.Called(ctx, email)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) UpdateUser(ctx context.Context, user *models.User) error {
	args := m.Called(ctx, user)
	return args.Error(0)
}

func (m *MockUserRepository) DeleteUser(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockUserRepository) ListUsers(ctx context.Context, filter *models.UserFilter) ([]*models.User, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.User), args.Error(1)
}

func (m *MockUserRepository) CountUsers(ctx context.Context) (int64, error) {
	args := m.Called(ctx)
	return args.Get(0).(int64), args.Error(1)
}

// MockLogger 创建日志记录器的模拟实现
type MockLogger struct {
	mock.Mock
}

func (m *MockLogger) Debug(msg string, keysAndValues ...interface{}) {
	m.Called(msg, keysAndValues)
}

func (m *MockLogger) Info(msg string, keysAndValues ...interface{}) {
	m.Called(msg, keysAndValues)
}

func (m *MockLogger) Warn(msg string, keysAndValues ...interface{}) {
	m.Called(msg, keysAndValues)
}

func (m *MockLogger) Error(msg string, keysAndValues ...interface{}) {
	m.Called(msg, keysAndValues)
}

func (m *MockLogger) With(args ...interface{}) logger.Logger {
	m.Called(args)
	return m
}

// 测试CreateUser方法
func TestDefaultUserService_CreateUser(t *testing.T) {
	// 创建模拟对象
	mockRepo := new(MockUserRepository)
	mockLog := new(MockLogger)
	
	// 设置日志记录器期望
	mockLog.On("With", mock.Anything).Return(mockLog)
	mockLog.On("Info", mock.Anything, mock.Anything).Return()
	mockLog.On("Error", mock.Anything, mock.Anything).Return()
	
	// 创建测试服务
	userService := NewDefaultUserService(mockRepo, mockLog)
	
	// 创建测试上下文
	ctx := context.Background()

	t.Run("成功创建用户", func(t *testing.T) {
		// 设置模拟行为
		mockRepo.On("GetUserByUsername", ctx, "testuser").Return(nil, errors.New("用户不存在"))
		mockRepo.On("GetUserByEmail", ctx, "test@example.com").Return(nil, errors.New("邮箱不存在"))
		mockRepo.On("CreateUser", ctx, mock.AnythingOfType("*models.User")).Return(nil)
		
		// 执行测试方法
		user, err := userService.CreateUser(ctx, "testuser", "test@example.com")
		
		// 验证结果
		assert.NoError(t, err, "创建用户应该成功")
		assert.NotNil(t, user, "应该返回用户对象")
		assert.Equal(t, "testuser", user.Username, "用户名应该匹配")
		assert.Equal(t, "test@example.com", user.Email, "邮箱应该匹配")
		
		// 验证调用
		mockRepo.AssertExpectations(t)
	})
	
	t.Run("用户名已存在", func(t *testing.T) {
		// 重置模拟
		mockRepo = new(MockUserRepository)
		userService = NewDefaultUserService(mockRepo, mockLog)
		
		// 设置模拟行为
		existingUser := &models.User{
			ID:       "existing-id",
			Username: "existinguser",
			Email:    "existing@example.com",
		}
		mockRepo.On("GetUserByUsername", ctx, "existinguser").Return(existingUser, nil)
		
		// 执行测试方法
		_, err := userService.CreateUser(ctx, "existinguser", "new@example.com")
		
		// 验证结果
		assert.Error(t, err, "应该返回错误")
		assert.Contains(t, err.Error(), "用户名已存在", "错误消息应该说明用户名已存在")
		
		// 验证调用
		mockRepo.AssertExpectations(t)
	})
	
	t.Run("邮箱已存在", func(t *testing.T) {
		// 重置模拟
		mockRepo = new(MockUserRepository)
		userService = NewDefaultUserService(mockRepo, mockLog)
		
		// 设置模拟行为
		mockRepo.On("GetUserByUsername", ctx, "newuser").Return(nil, errors.New("用户不存在"))
		
		existingUser := &models.User{
			ID:       "existing-id",
			Username: "existinguser",
			Email:    "existing@example.com",
		}
		mockRepo.On("GetUserByEmail", ctx, "existing@example.com").Return(existingUser, nil)
		
		// 执行测试方法
		_, err := userService.CreateUser(ctx, "newuser", "existing@example.com")
		
		// 验证结果
		assert.Error(t, err, "应该返回错误")
		assert.Contains(t, err.Error(), "邮箱已存在", "错误消息应该说明邮箱已存在")
		
		// 验证调用
		mockRepo.AssertExpectations(t)
	})
}

// 测试GetUserByID方法
func TestDefaultUserService_GetUserByID(t *testing.T) {
	// 创建模拟对象
	mockRepo := new(MockUserRepository)
	mockLog := new(MockLogger)
	
	// 设置日志记录器期望
	mockLog.On("With", mock.Anything).Return(mockLog)
	mockLog.On("Info", mock.Anything, mock.Anything).Return()
	mockLog.On("Error", mock.Anything, mock.Anything).Return()
	
	// 创建测试服务
	userService := NewDefaultUserService(mockRepo, mockLog)
	
	// 创建测试上下文
	ctx := context.Background()
	
	t.Run("成功获取用户", func(t *testing.T) {
		// 创建测试用户
		testUser := &models.User{
			ID:          "test-id",
			Username:    "testuser",
			Email:       "test@example.com",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
			Preferences: []byte(`{"theme":"dark"}`),
		}
		
		// 设置模拟行为
		mockRepo.On("GetUserByID", ctx, "test-id").Return(testUser, nil)
		
		// 执行测试方法
		user, err := userService.GetUserByID(ctx, "test-id")
		
		// 验证结果
		assert.NoError(t, err, "获取用户应该成功")
		assert.NotNil(t, user, "应该返回用户对象")
		assert.Equal(t, testUser.ID, user.ID, "用户ID应该匹配")
		assert.Equal(t, testUser.Username, user.Username, "用户名应该匹配")
		
		// 验证调用
		mockRepo.AssertExpectations(t)
	})
	
	t.Run("用户不存在", func(t *testing.T) {
		// 重置模拟
		mockRepo = new(MockUserRepository)
		userService = NewDefaultUserService(mockRepo, mockLog)
		
		// 设置模拟行为
		mockRepo.On("GetUserByID", ctx, "non-existent-id").Return(nil, errors.New("用户不存在"))
		
		// 执行测试方法
		_, err := userService.GetUserByID(ctx, "non-existent-id")
		
		// 验证结果
		assert.Error(t, err, "应该返回错误")
		assert.Contains(t, err.Error(), "用户不存在", "错误消息应该说明用户不存在")
		
		// 验证调用
		mockRepo.AssertExpectations(t)
	})
}