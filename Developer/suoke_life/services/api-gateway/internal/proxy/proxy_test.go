package proxy

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/suoke-life/api-gateway/internal/config"
)

// 创建模拟服务
func createMockBackendServer() *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"message": "Hello from backend"}`))
	}))
}

// 创建模拟错误服务
func createMockErrorServer() *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(`{"error": "Internal Server Error"}`))
	}))
}

type MockLogger struct{}

func (m *MockLogger) Debug(msg string, args ...interface{}) {}
func (m *MockLogger) Info(msg string, args ...interface{})  {}
func (m *MockLogger) Warn(msg string, args ...interface{})  {}
func (m *MockLogger) Error(msg string, args ...interface{}) {}
func (m *MockLogger) Fatal(msg string, args ...interface{}) {}

func TestServiceProxy_Proxy(t *testing.T) {
	// 创建模拟后端服务
	mockServer := createMockBackendServer()
	defer mockServer.Close()

	// 创建 ServiceProxy
	serviceConfig := config.ServiceConfig{
		URL:           mockServer.URL,
		Timeout:       5,
		RetryCount:    3,
		RetryInterval: 1,
	}
	proxy := NewServiceProxy("test-service", serviceConfig, &MockLogger{})

	// 创建 Gin 引擎和路由
	gin.SetMode(gin.TestMode)
	router := gin.New()
	
	// 注册代理路由
	router.Any("/test/*path", proxy.Proxy("/endpoint"))

	// 创建测试请求
	req := httptest.NewRequest("GET", "/test/endpoint", nil)
	resp := httptest.NewRecorder()

	// 执行请求
	router.ServeHTTP(resp, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, resp.Code)
	assert.Contains(t, resp.Body.String(), "Hello from backend")
}

func TestServiceProxy_ProxyWithError(t *testing.T) {
	// 创建模拟错误服务
	mockServer := createMockErrorServer()
	defer mockServer.Close()

	// 创建 ServiceProxy
	serviceConfig := config.ServiceConfig{
		URL:           mockServer.URL,
		Timeout:       5,
		RetryCount:    0, // 不重试
		RetryInterval: 1,
	}
	proxy := NewServiceProxy("error-service", serviceConfig, &MockLogger{})

	// 创建 Gin 引擎和路由
	gin.SetMode(gin.TestMode)
	router := gin.New()
	
	// 注册代理路由
	router.Any("/error/*path", proxy.Proxy("/endpoint"))

	// 创建测试请求
	req := httptest.NewRequest("GET", "/error/endpoint", nil)
	resp := httptest.NewRecorder()

	// 执行请求
	router.ServeHTTP(resp, req)

	// 验证响应
	assert.Equal(t, http.StatusInternalServerError, resp.Code)
	assert.Contains(t, resp.Body.String(), "Internal Server Error")
}

func TestServiceProxy_ProxyWithRetry(t *testing.T) {
	// 创建模拟错误服务
	mockServer := createMockErrorServer()
	defer mockServer.Close()

	// 创建 ServiceProxy 并启用重试
	serviceConfig := config.ServiceConfig{
		URL:           mockServer.URL,
		Timeout:       1,
		RetryCount:    2,
		RetryInterval: 1,
	}
	proxy := NewServiceProxy("retry-service", serviceConfig, &MockLogger{})

	// 创建 Gin 引擎和路由
	gin.SetMode(gin.TestMode)
	router := gin.New()
	
	// 注册代理路由
	router.Any("/retry/*path", proxy.Proxy("/endpoint"))

	// 创建测试请求
	req := httptest.NewRequest("GET", "/retry/endpoint", nil)
	resp := httptest.NewRecorder()

	// 执行请求
	router.ServeHTTP(resp, req)

	// 验证响应
	assert.Equal(t, http.StatusInternalServerError, resp.Code)
	assert.Contains(t, resp.Body.String(), "Internal Server Error")
}