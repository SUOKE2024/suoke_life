package benchmark

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"
	"go.uber.org/zap/zaptest"

	"knowledge-graph-service/internal/api/middleware"
	"knowledge-graph-service/internal/api/response"
)

// 初始化测试环境
func setupTestRouter(t *testing.T) (*gin.Engine, *zap.Logger) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	logger := zaptest.NewLogger(t)
	return router, logger
}

// 测试正常情况的响应处理
func BenchmarkResponseHandling(b *testing.B) {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	
	// 创建成功响应的路由
	router.GET("/normal", func(c *gin.Context) {
		response.Success(c, gin.H{"message": "success"})
	})
	
	// 创建优化版成功响应的路由
	router.GET("/optimized", func(c *gin.Context) {
		response.OptimizedSuccess(c, gin.H{"message": "success"})
	})
	
	// 创建大量数据的成功响应路由
	router.GET("/normal-large", func(c *gin.Context) {
		data := make([]map[string]interface{}, 100)
		for i := 0; i < 100; i++ {
			data[i] = map[string]interface{}{
				"id":        i,
				"name":      "测试数据",
				"timestamp": time.Now().Unix(),
				"details":   "这是详细信息...",
			}
		}
		response.Success(c, data)
	})
	
	// 创建优化版大量数据的成功响应路由
	router.GET("/optimized-large", func(c *gin.Context) {
		data := make([]map[string]interface{}, 100)
		for i := 0; i < 100; i++ {
			data[i] = map[string]interface{}{
				"id":        i,
				"name":      "测试数据",
				"timestamp": time.Now().Unix(),
				"details":   "这是详细信息...",
			}
		}
		response.OptimizedSuccess(c, data)
	})
	
	// 准备测试请求
	req := httptest.NewRequest("GET", "/normal", nil)
	reqOptimized := httptest.NewRequest("GET", "/optimized", nil)
	reqLarge := httptest.NewRequest("GET", "/normal-large", nil)
	reqOptimizedLarge := httptest.NewRequest("GET", "/optimized-large", nil)
	
	b.Run("NormalResponse", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
	
	b.Run("OptimizedResponse", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqOptimized)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
	
	b.Run("NormalResponseWithLargeData", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqLarge)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
	
	b.Run("OptimizedResponseWithLargeData", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqOptimizedLarge)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
}

// 测试请求追踪中间件性能
func BenchmarkRequestTracking(b *testing.B) {
	gin.SetMode(gin.ReleaseMode)
	logger := zap.NewNop() // 使用无操作logger避免日志输出干扰基准测试
	
	// 标准版请求追踪
	routerStandard := gin.New()
	routerStandard.Use(middleware.RequestTracker())
	routerStandard.GET("/test", func(c *gin.Context) {
		// 从context获取请求ID和开始时间
		requestID := middleware.GetRequestID(c)
		startTime := middleware.GetStartTime(c)
		assert.NotEmpty(b, requestID)
		assert.NotZero(b, startTime)
		c.Status(http.StatusOK)
	})
	
	// 优化版请求追踪
	routerOptimized := gin.New()
	routerOptimized.Use(middleware.OptimizedRequestTracker(logger))
	routerOptimized.GET("/test", func(c *gin.Context) {
		// 从context获取请求ID和开始时间
		requestID := middleware.GetRequestID(c)
		startTime := middleware.GetStartTime(c)
		assert.NotEmpty(b, requestID)
		assert.NotZero(b, startTime)
		c.Status(http.StatusOK)
	})
	
	// 准备测试请求
	req := httptest.NewRequest("GET", "/test", nil)
	
	b.Run("StandardRequestTracker", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			routerStandard.ServeHTTP(w, req)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
	
	b.Run("OptimizedRequestTracker", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			routerOptimized.ServeHTTP(w, req)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
}

// 测试JWT认证中间件性能
func BenchmarkJWTAuth(b *testing.B) {
	gin.SetMode(gin.ReleaseMode)
	
	// 创建带认证中间件的路由
	router := gin.New()
	router.Use(middleware.JWTAuth())
	router.GET("/protected", func(c *gin.Context) {
		c.Status(http.StatusOK)
	})
	
	// 准备测试请求（包含有效的JWT）
	validToken := "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMzQ1Njc4OTAiLCJyb2xlcyI6WyJhZG1pbiJdLCJleHAiOjk5OTk5OTk5OTl9.Z4wNG_Z0PEHRZkALBqZikeW9iFQ08UiX7iQnH3uyJnY"
	req := httptest.NewRequest("GET", "/protected", nil)
	req.Header.Set("Authorization", validToken)
	
	// 无令牌请求
	reqNoToken := httptest.NewRequest("GET", "/protected", nil)
	
	b.Run("JWTAuth_ValidToken", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)
		}
	})
	
	b.Run("JWTAuth_NoToken", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqNoToken)
		}
	})
}

// 测试恢复中间件性能
func BenchmarkRecovery(b *testing.B) {
	gin.SetMode(gin.ReleaseMode)
	logger := zap.NewNop() // 使用无操作logger避免日志输出干扰基准测试
	
	// 创建带恢复中间件的路由
	router := gin.New()
	router.Use(middleware.RecoveryWithLogger(logger))
	
	// 正常路由
	router.GET("/normal", func(c *gin.Context) {
		c.Status(http.StatusOK)
	})
	
	// 会发生panic的路由
	router.GET("/panic", func(c *gin.Context) {
		panic("测试恢复中间件")
	})
	
	// 准备测试请求
	reqNormal := httptest.NewRequest("GET", "/normal", nil)
	reqPanic := httptest.NewRequest("GET", "/panic", nil)
	
	b.Run("Recovery_NormalRoute", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqNormal)
			assert.Equal(b, http.StatusOK, w.Code)
		}
	})
	
	b.Run("Recovery_PanicRoute", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqPanic)
			assert.Equal(b, http.StatusInternalServerError, w.Code)
		}
	})
}

// 测试CORS中间件性能
func BenchmarkCORS(b *testing.B) {
	gin.SetMode(gin.ReleaseMode)
	
	// 创建带CORS中间件的路由
	router := gin.New()
	router.Use(middleware.DefaultCORS())
	router.GET("/api", func(c *gin.Context) {
		c.Status(http.StatusOK)
	})
	
	// 准备标准请求
	reqStandard := httptest.NewRequest("GET", "/api", nil)
	reqStandard.Header.Set("Origin", "http://example.com")
	
	// 准备预检请求
	reqPreflight := httptest.NewRequest("OPTIONS", "/api", nil)
	reqPreflight.Header.Set("Origin", "http://example.com")
	reqPreflight.Header.Set("Access-Control-Request-Method", "GET")
	reqPreflight.Header.Set("Access-Control-Request-Headers", "Content-Type")
	
	b.Run("CORS_StandardRequest", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqStandard)
			assert.Equal(b, http.StatusOK, w.Code)
			assert.Equal(b, "*", w.Header().Get("Access-Control-Allow-Origin"))
		}
	})
	
	b.Run("CORS_PreflightRequest", func(b *testing.B) {
		b.ReportAllocs() // 报告内存分配情况
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			router.ServeHTTP(w, reqPreflight)
			assert.Equal(b, http.StatusNoContent, w.Code)
			assert.Equal(b, "*", w.Header().Get("Access-Control-Allow-Origin"))
		}
	})
}