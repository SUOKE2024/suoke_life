package middleware_test

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/api/middleware"
)

func TestRequestTracker(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewDevelopment()

	// 测试用例
	tests := []struct {
		name              string
		requestID         string
		method            string
		path              string
		expectedRequestID bool
		expectedTraceID   bool
	}{
		{
			name:              "没有预先设置请求ID",
			requestID:         "",
			method:            "GET",
			path:              "/api/v1/data",
			expectedRequestID: true,
			expectedTraceID:   true,
		},
		{
			name:              "预先设置请求ID",
			requestID:         "test-request-id",
			method:            "POST",
			path:              "/api/v1/entities",
			expectedRequestID: true,
			expectedTraceID:   true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建测试上下文
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)
			c.Request = httptest.NewRequest(tt.method, tt.path, nil)

			if tt.requestID != "" {
				c.Request.Header.Set(middleware.RequestIDHeader, tt.requestID)
			}

			// 创建中间件
			middleware := middleware.RequestTracker(logger)

			// 执行中间件
			startTime := time.Now()
			middleware(c)
			
			// 等待一段时间模拟处理过程
			time.Sleep(10 * time.Millisecond)
			
			// 调用Next()后的处理
			c.Writer.WriteHeader(http.StatusOK)

			// 验证结果
			// 检查请求ID是否正确设置
			if tt.requestID != "" {
				assert.Equal(t, tt.requestID, c.Writer.Header().Get(middleware.RequestIDHeader))
			} else {
				assert.NotEmpty(t, c.Writer.Header().Get(middleware.RequestIDHeader))
			}

			// 检查上下文中是否正确存储请求ID
			requestID, exists := c.Get(middleware.RequestIDKey)
			assert.True(t, exists)
			assert.NotEmpty(t, requestID)

			// 检查跟踪ID
			assert.NotEmpty(t, c.Writer.Header().Get(middleware.TraceIDHeader))

			// 检查响应时间
			assert.NotEmpty(t, c.Writer.Header().Get("X-Response-Time"))
			
			// 验证请求持续时间
			duration := middleware.GetRequestDuration(c)
			assert.True(t, duration >= 10*time.Millisecond)
			
			// 检查开始时间
			startTimeFromContext := middleware.GetStartTime(c)
			assert.WithinDuration(t, startTime, startTimeFromContext, 50*time.Millisecond)
		})
	}
}

func TestGetRequestID(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	
	// 创建测试上下文
	c, _ := gin.CreateTestContext(httptest.NewRecorder())
	
	// 测试没有请求ID时
	requestID := middleware.GetRequestID(c)
	assert.Equal(t, "unknown", requestID)
	
	// 测试有请求ID时
	c.Set(middleware.RequestIDKey, "test-request-id")
	requestID = middleware.GetRequestID(c)
	assert.Equal(t, "test-request-id", requestID)
}

func TestGetTraceID(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	
	// 创建测试上下文
	c, _ := gin.CreateTestContext(httptest.NewRecorder())
	
	// 测试没有跟踪ID时
	traceID := middleware.GetTraceID(c)
	assert.Equal(t, "unknown", traceID)
	
	// 测试有跟踪ID时
	c.Set("TraceID", "test-trace-id")
	traceID = middleware.GetTraceID(c)
	assert.Equal(t, "test-trace-id", traceID)
}

// 性能基准测试
func BenchmarkRequestTracker(b *testing.B) {
	// 设置测试环境
	gin.SetMode(gin.ReleaseMode)
	logger, _ := zap.NewDevelopment()
	
	// 创建请求跟踪中间件
	middleware := middleware.RequestTracker(logger)
	
	// 重置计时器
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		c.Request = httptest.NewRequest("GET", "/benchmark", nil)
		
		middleware(c)
		c.Writer.WriteHeader(http.StatusOK)
	}
} 