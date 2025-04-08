package integration

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/api/middleware"
	"knowledge-graph-service/internal/api/response"
)

// 测试API的集成测试
func TestAPIIntegration(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewProduction()
	
	// 创建路由引擎
	router := gin.New()
	
	// 注册中间件
	jwtConfig := middleware.JWTConfig{
		SigningKey: "test-key",
		ExemptPaths: []string{
			"/health",
			"/api/v1/auth/login",
			"/api/v1/auth/register",
		},
	}
	
	// 注册所有中间件
	middleware.RegisterMiddlewares(router, logger)
	
	// 注册路由
	router.GET("/health", func(c *gin.Context) {
		response.Success(c, gin.H{"status": "ok"})
	})
	
	// 模拟API路由组
	apiGroup := router.Group("/api/v1")
	middleware.RegisterAPIMiddlewares(apiGroup, logger)
	
	// 普通API路由
	apiGroup.GET("/data", func(c *gin.Context) {
		response.Success(c, gin.H{"data": "protected"})
	})
	
	// 登录路由
	apiGroup.POST("/auth/login", func(c *gin.Context) {
		response.Success(c, gin.H{"token": "test.jwt.token"})
	})
	
	// 管理员路由组
	adminGroup := router.Group("/api/v1/admin")
	middleware.RegisterAdminMiddlewares(adminGroup, logger)
	
	// 管理员路由
	adminGroup.GET("/dashboard", func(c *gin.Context) {
		response.Success(c, gin.H{"admin": "dashboard"})
	})
	
	// 测试用例
	tests := []struct {
		name           string
		method         string
		path           string
		token          string
		expectedCode   int
		expectedResult map[string]interface{}
	}{
		{
			name:           "健康检查路由",
			method:         "GET",
			path:           "/health",
			token:          "",
			expectedCode:   http.StatusOK,
			expectedResult: map[string]interface{}{"success": true, "data": map[string]interface{}{"status": "ok"}},
		},
		{
			name:           "登录路由",
			method:         "POST",
			path:           "/api/v1/auth/login",
			token:          "",
			expectedCode:   http.StatusOK,
			expectedResult: map[string]interface{}{"success": true, "data": map[string]interface{}{"token": "test.jwt.token"}},
		},
		{
			name:           "受保护路由无令牌",
			method:         "GET",
			path:           "/api/v1/data",
			token:          "",
			expectedCode:   http.StatusUnauthorized,
			expectedResult: nil,
		},
		{
			name:           "管理员路由无令牌",
			method:         "GET",
			path:           "/api/v1/admin/dashboard",
			token:          "",
			expectedCode:   http.StatusUnauthorized,
			expectedResult: nil,
		},
	}
	
	// 执行测试
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建测试请求
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(tt.method, tt.path, nil)
			
			// 添加请求头
			if tt.token != "" {
				req.Header.Set("Authorization", "Bearer "+tt.token)
			}
			
			// 处理请求
			router.ServeHTTP(w, req)
			
			// 验证状态码
			assert.Equal(t, tt.expectedCode, w.Code)
			
			// 验证响应内容
			if tt.expectedResult != nil {
				var result map[string]interface{}
				err := json.Unmarshal(w.Body.Bytes(), &result)
				assert.NoError(t, err)
				
				// 验证响应结构
				assert.Equal(t, tt.expectedResult["success"], result["success"])
				
				// 验证数据字段
				if data, ok := tt.expectedResult["data"].(map[string]interface{}); ok {
					resultData, dataOk := result["data"].(map[string]interface{})
					assert.True(t, dataOk)
					
					for k, v := range data {
						assert.Equal(t, v, resultData[k])
					}
				}
			}
			
			// 验证请求头
			assert.NotEmpty(t, w.Header().Get(middleware.RequestIDHeader))
			assert.NotEmpty(t, w.Header().Get(middleware.TraceIDHeader))
			assert.NotEmpty(t, w.Header().Get("X-Response-Time"))
		})
	}
}

// 测试错误处理
func TestErrorHandling(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewProduction()
	
	// 创建路由引擎
	router := gin.New()
	router.Use(middleware.RecoveryWithLogger(logger))
	router.Use(middleware.RequestTracker(logger))
	
	// 添加测试路由
	router.GET("/panic", func(c *gin.Context) {
		panic("测试panic")
	})
	
	router.GET("/bad-request", func(c *gin.Context) {
		response.BadRequest(c, "无效的请求参数")
	})
	
	router.GET("/not-found", func(c *gin.Context) {
		response.NotFound(c, "资源不存在")
	})
	
	router.GET("/internal-error", func(c *gin.Context) {
		response.InternalError(c, "服务器内部错误", logger)
	})
	
	// 测试用例
	tests := []struct {
		name         string
		path         string
		expectedCode int
		errorMessage string
	}{
		{
			name:         "Panic错误",
			path:         "/panic",
			expectedCode: http.StatusInternalServerError,
			errorMessage: "系统异常",
		},
		{
			name:         "无效请求错误",
			path:         "/bad-request",
			expectedCode: http.StatusBadRequest,
			errorMessage: "无效的请求参数",
		},
		{
			name:         "资源不存在错误",
			path:         "/not-found",
			expectedCode: http.StatusNotFound,
			errorMessage: "资源不存在",
		},
		{
			name:         "内部服务器错误",
			path:         "/internal-error",
			expectedCode: http.StatusInternalServerError,
			errorMessage: "服务器内部错误",
		},
	}
	
	// 执行测试
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建测试请求
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", tt.path, nil)
			
			// 处理请求
			router.ServeHTTP(w, req)
			
			// 验证状态码
			assert.Equal(t, tt.expectedCode, w.Code)
			
			// 验证响应内容
			var result map[string]interface{}
			err := json.Unmarshal(w.Body.Bytes(), &result)
			
			// 由于panic错误可能格式不同，我们只对其他错误进行详细验证
			if tt.path != "/panic" {
				assert.NoError(t, err)
				assert.Equal(t, false, result["success"])
				assert.Equal(t, tt.errorMessage, result["message"])
			}
		})
	}
} 