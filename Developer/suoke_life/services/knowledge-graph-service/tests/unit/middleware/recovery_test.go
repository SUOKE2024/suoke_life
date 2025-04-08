package middleware_test

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/api/middleware"
)

func TestRecoveryWithLogger(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewDevelopment()

	tests := []struct {
		name         string
		panicValue   interface{}
		expectedCode int
	}{
		{
			name:         "无panic情况",
			panicValue:   nil,
			expectedCode: http.StatusOK,
		},
		{
			name:         "panic错误类型",
			panicValue:   errors.New("测试错误"),
			expectedCode: http.StatusInternalServerError,
		},
		{
			name:         "panic字符串类型",
			panicValue:   "测试错误字符串",
			expectedCode: http.StatusInternalServerError,
		},
		{
			name:         "panic其他类型",
			panicValue:   123,
			expectedCode: http.StatusInternalServerError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建测试上下文
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)
			c.Request = httptest.NewRequest("GET", "/api/v1/data", nil)
			
			// 请求追踪信息
			c.Set(middleware.RequestIDKey, "test-request-id")
			c.Set("TraceID", "test-trace-id")

			// 创建恢复中间件
			recoveryMiddleware := middleware.RecoveryWithLogger(logger)

			// 测试处理函数
			testHandler := func(c *gin.Context) {
				if tt.panicValue != nil {
					panic(tt.panicValue)
				}
				c.Status(http.StatusOK)
			}

			// 执行测试
			recoveryFunc := recoveryMiddleware(c)
			
			// 判断是否会有panic产生
			if tt.panicValue != nil {
				// 应该捕获panic，不会导致测试失败
				assert.NotPanics(t, func() {
					defer recoveryFunc()
					testHandler(c)
				})
				
				// 验证状态码
				assert.Equal(t, tt.expectedCode, w.Code)
			} else {
				// 没有panic时正常执行
				recoveryFunc()
				testHandler(c)
				assert.Equal(t, tt.expectedCode, w.Code)
			}
		})
	}
}

func TestCustomRecovery(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewDevelopment()

	// 自定义错误处理函数
	customHandlerCalled := false
	customValue := 0
	
	customHandler := func(c *gin.Context, err any) {
		customHandlerCalled = true
		if val, ok := err.(int); ok {
			customValue = val
		}
		c.JSON(http.StatusTeapot, gin.H{"error": "自定义错误处理"})
	}

	// 创建测试上下文
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest("GET", "/api/v1/data", nil)

	// 创建中间件
	customRecovery := middleware.CustomRecovery(logger, customHandler)

	// 执行中间件
	customRecoveryFunc := customRecovery(c)
	
	// 测试自定义handler是否被调用
	assert.NotPanics(t, func() {
		defer customRecoveryFunc()
		panic(42) // 使用数字作为panic值
	})
	
	// 验证结果
	assert.True(t, customHandlerCalled)
	assert.Equal(t, 42, customValue)
	assert.Equal(t, http.StatusTeapot, w.Code)
}

func TestDefaultRecoveryHandler(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	
	// 创建测试上下文
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	// 调用默认处理函数
	middleware.DefaultRecoveryHandler(c, "测试错误")
	
	// 验证状态码和响应体
	assert.Equal(t, http.StatusInternalServerError, w.Code)
	assert.Contains(t, w.Body.String(), "系统异常")
}

func TestRecoveryMiddleware(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	
	// 创建测试上下文
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest("GET", "/api/v1/data", nil)
	
	// 创建中间件
	recovery := middleware.RecoveryMiddleware()
	
	// 执行中间件
	recoveryFunc := recovery(c)
	
	// 模拟panic
	assert.NotPanics(t, func() {
		defer recoveryFunc()
		panic("测试RecoveryMiddleware")
	})
	
	// 验证结果
	assert.Equal(t, http.StatusInternalServerError, w.Code)
}

// 测试中间件是否会影响正常流程
func TestRecoveryNoPanic(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewDevelopment()
	
	// 创建路由
	router := gin.New()
	router.Use(middleware.RecoveryWithLogger(logger))
	
	// 添加测试路由
	router.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "正常响应")
	})
	
	// 创建测试请求
	w := httptest.NewRecorder()
	req := httptest.NewRequest("GET", "/test", nil)
	
	// 处理请求
	router.ServeHTTP(w, req)
	
	// 验证结果
	assert.Equal(t, http.StatusOK, w.Code)
	assert.Equal(t, "正常响应", w.Body.String())
} 