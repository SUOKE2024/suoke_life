package middleware

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// 本地实现MockBackendServer函数，避免循环导入
func createMockAuthServer(t *testing.T, path string, response interface{}, statusCode int) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 检查请求路径
		if r.URL.Path != path {
			t.Errorf("期望路径 %s, 实际路径 %s", path, r.URL.Path)
			w.WriteHeader(http.StatusNotFound)
			return
		}
		
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(statusCode)
		
		if response != nil {
			jsonResp, err := json.Marshal(response)
			if err != nil {
				t.Fatalf("无法序列化响应: %v", err)
			}
			fmt.Fprintln(w, string(jsonResp))
		}
	}))
}

func TestAuth_NoToken(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置Auth中间件
	config := JWTConfig{
		SigningKey:     "test_secret_key",
		ExpirationTime: 1 * time.Hour,
		RefreshTime:    30 * time.Minute,
		TokenLookup:    "header:Authorization",
		TokenHeadName:  "Bearer",
		AuthScheme:     "Bearer",
	}
	r.Use(JWTAuth(config))

	// 添加测试路由
	r.GET("/protected", func(c *gin.Context) {
		c.String(http.StatusOK, "访问成功")
	})

	// 测试无令牌
	req, _ := http.NewRequest("GET", "/protected", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestAuth_InvalidToken(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置Auth中间件
	config := JWTConfig{
		SigningKey:     "test_secret_key",
		ExpirationTime: 1 * time.Hour,
		RefreshTime:    30 * time.Minute,
		TokenLookup:    "header:Authorization",
		TokenHeadName:  "Bearer",
		AuthScheme:     "Bearer",
	}
	r.Use(JWTAuth(config))

	// 添加测试路由
	r.GET("/protected", func(c *gin.Context) {
		c.String(http.StatusOK, "访问成功")
	})

	// 测试无效令牌
	req, _ := http.NewRequest("GET", "/protected", nil)
	req.Header.Set("Authorization", "Bearer invalid-token")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestAuth_ValidToken(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 生成有效令牌
	config := JWTConfig{
		SigningKey:     "test_secret_key",
		ExpirationTime: 1 * time.Hour,
		RefreshTime:    30 * time.Minute,
		TokenLookup:    "header:Authorization",
		TokenHeadName:  "Bearer",
		AuthScheme:     "Bearer",
	}
	
	// 手动创建令牌
	token, err := generateToken("12345", "user", config)
	if err != nil {
		t.Fatalf("无法生成测试令牌: %v", err)
	}
	
	// 配置Auth中间件
	r.Use(JWTAuth(config))

	// 添加测试路由
	r.GET("/protected", func(c *gin.Context) {
		userID, exists := c.Get("userID")
		assert.True(t, exists)
		assert.Equal(t, "12345", userID)
		
		role, exists := c.Get("role")
		assert.True(t, exists)
		assert.Equal(t, "user", role)
		
		c.String(http.StatusOK, "访问成功")
	})

	// 测试有效令牌
	req, _ := http.NewRequest("GET", "/protected", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestAuth_ExpiredToken(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置Auth中间件
	config := JWTConfig{
		SigningKey:     "test_secret_key",
		ExpirationTime: -1 * time.Hour, // 一小时前过期
		RefreshTime:    30 * time.Minute,
		TokenLookup:    "header:Authorization",
		TokenHeadName:  "Bearer",
		AuthScheme:     "Bearer",
	}
	
	// 生成一个已过期的令牌
	token, err := generateToken("12345", "user", config)
	if err != nil {
		t.Fatalf("无法生成测试令牌: %v", err)
	}
	
	// 重置Config为正常配置，使用正确的验证密钥
	config.ExpirationTime = 1 * time.Hour
	r.Use(JWTAuth(config))

	// 添加测试路由
	r.GET("/protected", func(c *gin.Context) {
		c.String(http.StatusOK, "访问成功")
	})

	// 测试过期令牌
	req, _ := http.NewRequest("GET", "/protected", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

// MockLogger 简化的日志记录器
type MockLogger struct{}

func (m *MockLogger) Debug(msg string, args ...interface{}) {}
func (m *MockLogger) Info(msg string, args ...interface{})  {}
func (m *MockLogger) Warn(msg string, args ...interface{})  {}
func (m *MockLogger) Error(msg string, args ...interface{}) {}
func (m *MockLogger) Fatal(msg string, args ...interface{}) {} 