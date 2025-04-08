package simple

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// 测试简单的中间件功能
func TestMiddleware(t *testing.T) {
	// 设置gin为测试模式
	gin.SetMode(gin.TestMode)

	// 创建一个简单的中间件
	simpleMiddleware := func(c *gin.Context) {
		c.Set("test_key", "test_value")
		c.Next()
	}

	// 创建测试路由
	r := gin.New()
	r.Use(simpleMiddleware)
	r.GET("/test", func(c *gin.Context) {
		val, exists := c.Get("test_key")
		if exists {
			c.String(http.StatusOK, val.(string))
		} else {
			c.String(http.StatusInternalServerError, "Key not found")
		}
	})

	// 创建测试请求
	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	// 验证结果
	assert.Equal(t, http.StatusOK, w.Code)
	assert.Equal(t, "test_value", w.Body.String())
}

// 性能测试简单中间件
func BenchmarkMiddleware(b *testing.B) {
	// 设置gin为测试模式
	gin.SetMode(gin.TestMode)

	// 创建一个简单的中间件
	simpleMiddleware := func(c *gin.Context) {
		c.Set("test_key", "test_value")
		c.Next()
	}

	// 创建测试路由
	r := gin.New()
	r.Use(simpleMiddleware)
	r.GET("/test", func(c *gin.Context) {
		val, _ := c.Get("test_key")
		c.String(http.StatusOK, val.(string))
	})

	// 重置计时器
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		// 创建测试请求
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
	}
} 