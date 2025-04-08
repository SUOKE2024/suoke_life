package controllers

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/models"
)

// 创建一个模拟的用户服务
type mockUserService struct {
	mock.Mock
}

func (m *mockUserService) CreateUser(ctx *gin.Context, username string, email string) (*models.User, error) {
	args := m.Called(ctx, username, email)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *mockUserService) GetUserByID(ctx *gin.Context, id string) (*models.User, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *mockUserService) GetUserByUsername(ctx *gin.Context, username string) (*models.User, error) {
	args := m.Called(ctx, username)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *mockUserService) UpdateUser(ctx *gin.Context, id string, update *models.UserUpdate) (*models.User, error) {
	args := m.Called(ctx, id, update)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *mockUserService) DeleteUser(ctx *gin.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func setupUserTest() (*UserController, *mockUserService, *gin.Engine) {
	// 设置Gin测试环境
	gin.SetMode(gin.TestMode)
	router := gin.New()
	
	// 创建模拟服务和控制器
	mockService := new(mockUserService)
	log := logger.NewZapLogger("test")
	controller := NewUserController(mockService, log)
	
	return controller, mockService, router
}

func TestCreateUser(t *testing.T) {
	controller, mockService, router := setupUserTest()
	
	// 设置测试路由
	router.POST("/users", controller.CreateUser)
	
	t.Run("创建用户成功", func(t *testing.T) {
		// 准备模拟请求
		reqBody, _ := json.Marshal(map[string]string{
			"username": "testuser",
			"email":    "test@example.com",
		})
		
		// 模拟服务返回
		testUser := &models.User{
			ID:       "123",
			Username: "testuser",
			Email:    "test@example.com",
		}
		mockService.On("CreateUser", mock.Anything, "testuser", "test@example.com").
			Return(testUser, nil).Once()
		
		// 执行请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(reqBody))
		req.Header.Set("Content-Type", "application/json")
		router.ServeHTTP(w, req)
		
		// 验证响应
		assert.Equal(t, http.StatusCreated, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.Nil(t, err)
		assert.Equal(t, "用户创建成功", response["message"])
		
		// 验证模拟服务是否按预期被调用
		mockService.AssertExpectations(t)
	})
	
	t.Run("用户名已存在", func(t *testing.T) {
		// 准备模拟请求
		reqBody, _ := json.Marshal(map[string]string{
			"username": "existinguser",
			"email":    "test@example.com",
		})
		
		// 模拟服务返回错误
		mockService.On("CreateUser", mock.Anything, "existinguser", "test@example.com").
			Return(nil, errors.New("用户名已存在: existinguser")).Once()
		
		// 执行请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(reqBody))
		req.Header.Set("Content-Type", "application/json")
		router.ServeHTTP(w, req)
		
		// 验证响应
		assert.Equal(t, http.StatusConflict, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.Nil(t, err)
		assert.Equal(t, "用户名已存在", response["error"])
		
		// 验证模拟服务是否按预期被调用
		mockService.AssertExpectations(t)
	})
	
	t.Run("无效请求", func(t *testing.T) {
		// 准备模拟请求 - 缺少必填字段
		reqBody, _ := json.Marshal(map[string]string{
			"username": "testuser",
			// 缺少 email
		})
		
		// 执行请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(reqBody))
		req.Header.Set("Content-Type", "application/json")
		router.ServeHTTP(w, req)
		
		// 验证响应
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.Nil(t, err)
		assert.Equal(t, "无效的请求", response["error"])
	})
}

func TestGetUser(t *testing.T) {
	controller, mockService, router := setupUserTest()
	
	// 设置测试路由
	router.GET("/users/:id", controller.GetUser)
	
	t.Run("获取用户成功", func(t *testing.T) {
		// 模拟服务返回
		testUser := &models.User{
			ID:       "123",
			Username: "testuser",
			Email:    "test@example.com",
		}
		mockService.On("GetUserByID", mock.Anything, "123").
			Return(testUser, nil).Once()
		
		// 执行请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/users/123", nil)
		router.ServeHTTP(w, req)
		
		// 验证响应
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.Nil(t, err)
		
		userMap := response["user"].(map[string]interface{})
		assert.Equal(t, "testuser", userMap["username"])
		
		// 验证模拟服务是否按预期被调用
		mockService.AssertExpectations(t)
	})
	
	t.Run("用户不存在", func(t *testing.T) {
		// 模拟服务返回错误
		mockService.On("GetUserByID", mock.Anything, "999").
			Return(nil, errors.New("用户不存在: 999")).Once()
		
		// 执行请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/users/999", nil)
		router.ServeHTTP(w, req)
		
		// 验证响应
		assert.Equal(t, http.StatusNotFound, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.Nil(t, err)
		assert.Equal(t, "用户不存在", response["error"])
		
		// 验证模拟服务是否按预期被调用
		mockService.AssertExpectations(t)
	})
}

// 健康检查测试
func TestHealthCheck(t *testing.T) {
	controller, _, router := setupUserTest()
	
	// 添加健康检查路由
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"service": "user-service",
		})
	})
	
	// 执行请求
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	router.ServeHTTP(w, req)
	
	// 验证响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.Nil(t, err)
	assert.Equal(t, "healthy", response["status"])
	assert.Equal(t, "user-service", response["service"])
}