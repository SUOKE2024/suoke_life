package proxy

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/suoke-life/api-gateway/internal/config"
)

// 模拟Logger
type mockLogger struct{}

func (m *mockLogger) Debug(msg string, args ...interface{}) {}
func (m *mockLogger) Info(msg string, args ...interface{})  {}
func (m *mockLogger) Warn(msg string, args ...interface{})  {}
func (m *mockLogger) Error(msg string, args ...interface{}) {}
func (m *mockLogger) Fatal(msg string, args ...interface{}) {}

// createBackendServer 创建模拟后端服务器
func createBackendServer(t *testing.T) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 记录请求头
		headers := make(map[string]string)
		for k, v := range r.Header {
			if len(v) > 0 {
				headers[k] = v[0]
			}
		}

		// 构造响应
		response := map[string]interface{}{
			"path":    r.URL.Path,
			"method":  r.Method,
			"headers": headers,
			"query":   r.URL.Query(),
		}
		
		// 如果是POST请求，读取请求体
		if r.Method == "POST" || r.Method == "PUT" {
			var bodyData map[string]interface{}
			if err := json.NewDecoder(r.Body).Decode(&bodyData); err == nil {
				response["body"] = bodyData
			}
		}
		
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(response)
	}))
}

func TestProxyIntegration(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)
	
	// 创建模拟后端服务器
	backendServer := createBackendServer(t)
	defer backendServer.Close()
	
	// 创建测试配置
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService: config.ServiceConfig{
				URL:           backendServer.URL,
				Timeout:       5,
				RetryCount:    1,
				RetryInterval: 1,
			},
		},
	}
	
	// 创建代理管理器
	log := &mockLogger{}
	proxyManager := NewProxyManager(cfg, log)
	
	// 创建Gin路由
	r := gin.New()
	r.GET("/api/users/:id", proxyManager.ProxyToService("user_service", "/users/:id"))
	r.POST("/api/users", proxyManager.ProxyToService("user_service", "/users"))
	
	// 测试GET请求代理
	t.Run("GET Proxy", func(t *testing.T) {
		req, _ := http.NewRequest("GET", "/api/users/123", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var resp map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		
		// 验证请求被正确代理
		assert.Equal(t, "/users/123", resp["path"])
		assert.Equal(t, "GET", resp["method"])
	})
	
	// 测试POST请求代理
	t.Run("POST Proxy", func(t *testing.T) {
		reqBody := map[string]interface{}{
			"name": "测试用户",
			"email": "test@example.com",
		}
		reqBodyBytes, _ := json.Marshal(reqBody)
		
		req, _ := http.NewRequest("POST", "/api/users", bytes.NewBuffer(reqBodyBytes))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var resp map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		
		// 验证请求被正确代理
		assert.Equal(t, "/users", resp["path"])
		assert.Equal(t, "POST", resp["method"])
		
		// 验证请求体
		body, ok := resp["body"].(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, "测试用户", body["name"])
		assert.Equal(t, "test@example.com", body["email"])
	})
}

func BenchmarkProxy(b *testing.B) {
	// 设置测试模式
	gin.SetMode(gin.ReleaseMode)
	
	// 创建模拟后端服务器
	backendServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintln(w, `{"status":"ok"}`)
	}))
	defer backendServer.Close()
	
	// 创建测试配置
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService: config.ServiceConfig{
				URL:           backendServer.URL,
				Timeout:       5,
				RetryCount:    0, // 禁用重试以提高基准测试性能
				RetryInterval: 0,
			},
		},
	}
	
	// 创建代理管理器
	log := &mockLogger{}
	proxyManager := NewProxyManager(cfg, log)
	
	// 创建Gin路由
	r := gin.New()
	r.GET("/api/benchmark", proxyManager.ProxyToService("user_service", "/benchmark"))
	
	// 创建请求
	req, _ := http.NewRequest("GET", "/api/benchmark", nil)
	
	// 运行基准测试
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
	}
} 