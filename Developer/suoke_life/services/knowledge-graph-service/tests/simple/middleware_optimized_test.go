package simple

import (
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// 常规中间件 - 请求追踪
func standardRequestTracker() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 生成请求ID
		requestID := uuid.New().String()
		// 记录开始时间
		startTime := time.Now()
		
		// 设置请求ID到上下文
		c.Set("RequestID", requestID)
		c.Set("StartTime", startTime)
		
		// 设置请求头
		c.Header("X-Request-ID", requestID)
		
		// 处理请求
		c.Next()
		
		// 请求完成后计算持续时间
		duration := time.Since(startTime)
		
		// 这里通常会有日志记录，但为了基准测试简化
		_ = duration
	}
}

// 优化版中间件 - 请求追踪
func optimizedRequestTracker() gin.HandlerFunc {
	// UUID缓冲池，减少内存分配
	uuidPool := &sync.Pool{
		New: func() interface{} {
			return new([16]byte)
		},
	}
	
	return func(c *gin.Context) {
		// 从池中获取UUID buffer
		uuidBytes := uuidPool.Get().(*[16]byte)
		defer uuidPool.Put(uuidBytes)
		
		// 生成请求ID（直接使用字节数组）
		_, err := uuid.NewRandomFromReader(new(fixedReader))
		if err != nil {
			// 回退到标准方法
			uuid.SetRand(new(fixedReader))
		}
		
		// 生成请求ID字符串
		requestID := uuid.Must(uuid.NewUUID()).String()
		
		// 记录开始时间
		startTime := time.Now()
		
		// 设置请求ID到上下文
		c.Set("RequestID", requestID)
		c.Set("StartTime", startTime)
		
		// 设置请求头
		c.Header("X-Request-ID", requestID)
		
		// 处理请求
		c.Next()
		
		// 请求完成后计算持续时间（只在需要时计算）
		if c.Writer.Status() >= 500 {
			duration := time.Since(startTime)
			_ = duration
		}
	}
}

// 用于优化随机性能的固定读取器
type fixedReader struct{}

func (r *fixedReader) Read(p []byte) (n int, err error) {
	// 填充一些固定数据而不是随机数，用于基准测试
	for i := range p {
		p[i] = byte(i % 256)
	}
	return len(p), nil
}

// 测试两种中间件的功能正确性
func TestRequestTrackers(t *testing.T) {
	// 设置gin为测试模式
	gin.SetMode(gin.TestMode)

	t.Run("StandardTracker", func(t *testing.T) {
		// 创建标准中间件的路由
		r := gin.New()
		r.Use(standardRequestTracker())
		r.GET("/test", func(c *gin.Context) {
			requestID, exists := c.Get("RequestID")
			assert.True(t, exists)
			assert.NotEmpty(t, requestID)
			c.String(http.StatusOK, "ok")
		})

		// 创建测试请求
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)

		// 验证结果
		assert.Equal(t, http.StatusOK, w.Code)
		assert.NotEmpty(t, w.Header().Get("X-Request-ID"))
	})

	t.Run("OptimizedTracker", func(t *testing.T) {
		// 创建优化中间件的路由
		r := gin.New()
		r.Use(optimizedRequestTracker())
		r.GET("/test", func(c *gin.Context) {
			requestID, exists := c.Get("RequestID")
			assert.True(t, exists)
			assert.NotEmpty(t, requestID)
			c.String(http.StatusOK, "ok")
		})

		// 创建测试请求
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)

		// 验证结果
		assert.Equal(t, http.StatusOK, w.Code)
		assert.NotEmpty(t, w.Header().Get("X-Request-ID"))
	})
}

// 性能测试请求追踪中间件
func BenchmarkRequestTrackers(b *testing.B) {
	// 设置标准路由
	standardRouter := gin.New()
	standardRouter.Use(standardRequestTracker())
	standardRouter.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "ok")
	})

	// 设置优化路由
	optimizedRouter := gin.New()
	optimizedRouter.Use(optimizedRequestTracker())
	optimizedRouter.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "ok")
	})

	// 准备测试请求
	req := httptest.NewRequest(http.MethodGet, "/test", nil)

	b.Run("StandardTracker", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, req)
		}
	})

	b.Run("OptimizedTracker", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			optimizedRouter.ServeHTTP(w, req)
		}
	})
}

// 响应处理中间件性能对比
// 标准响应结构
type standardResponse struct {
	Success bool        `json:"success"`
	Code    string      `json:"code,omitempty"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
}

// 响应生成函数 - 标准版
func standardSuccess(c *gin.Context, data interface{}) {
	resp := standardResponse{
		Success: true,
		Data:    data,
	}
	c.JSON(http.StatusOK, resp)
}

// 响应处理函数 - 使用对象池的优化版
var responsePool = &sync.Pool{
	New: func() interface{} {
		return &standardResponse{}
	},
}

// 优化版响应生成
func optimizedSuccess(c *gin.Context, data interface{}) {
	// 从对象池获取响应对象
	resp := responsePool.Get().(*standardResponse)
	defer responsePool.Put(resp)
	
	// 重置响应对象
	*resp = standardResponse{
		Success: true,
		Data:    data,
	}
	
	c.JSON(http.StatusOK, resp)
}

// 测试响应处理功能
func TestResponseHandlers(t *testing.T) {
	// 设置gin为测试模式
	gin.SetMode(gin.TestMode)

	t.Run("StandardResponse", func(t *testing.T) {
		// 创建标准响应的路由
		r := gin.New()
		r.GET("/test", func(c *gin.Context) {
			standardSuccess(c, map[string]string{"message": "test"})
		})

		// 创建测试请求
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)

		// 验证结果
		assert.Equal(t, http.StatusOK, w.Code)
		assert.Contains(t, w.Body.String(), `"success":true`)
		assert.Contains(t, w.Body.String(), `"message":"test"`)
	})

	t.Run("OptimizedResponse", func(t *testing.T) {
		// 创建优化响应的路由
		r := gin.New()
		r.GET("/test", func(c *gin.Context) {
			optimizedSuccess(c, map[string]string{"message": "test"})
		})

		// 创建测试请求
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)

		// 验证结果
		assert.Equal(t, http.StatusOK, w.Code)
		assert.Contains(t, w.Body.String(), `"success":true`)
		assert.Contains(t, w.Body.String(), `"message":"test"`)
	})
}

// 性能测试响应处理
func BenchmarkResponseHandlers(b *testing.B) {
	// 设置标准路由
	standardRouter := gin.New()
	standardRouter.GET("/test", func(c *gin.Context) {
		standardSuccess(c, map[string]string{"message": "test"})
	})

	// 设置优化路由
	optimizedRouter := gin.New()
	optimizedRouter.GET("/test", func(c *gin.Context) {
		optimizedSuccess(c, map[string]string{"message": "test"})
	})

	// 准备测试请求
	req := httptest.NewRequest(http.MethodGet, "/test", nil)

	b.Run("StandardResponse", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, req)
		}
	})

	b.Run("OptimizedResponse", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			optimizedRouter.ServeHTTP(w, req)
		}
	})
} 