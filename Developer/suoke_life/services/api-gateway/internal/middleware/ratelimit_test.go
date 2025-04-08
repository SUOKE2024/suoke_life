package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/suoke-life/api-gateway/internal/configs"
)

func TestRateLimit_NormalUsage(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置限流中间件 - 每秒允许5个请求
	config := &configs.Config{
		RateLimit: configs.RateLimitConfig{
			Enabled:           true,
			RequestsPerMinute: 5,
			BurstSize:         2,
			TimeWindow:        1, // 1秒窗口
		},
	}
	r.Use(RateLimit(config))

	// 添加测试路由
	r.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "请求成功")
	})

	// 测试正常使用 - 5个请求应该都成功
	for i := 0; i < 5; i++ {
		req, _ := http.NewRequest("GET", "/test", nil)
		req.RemoteAddr = "192.168.1.1:1234" // 模拟相同的IP地址
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	}
}

func TestRateLimit_ExceedLimit(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置限流中间件 - 每秒允许3个请求
	config := &configs.Config{
		RateLimit: configs.RateLimitConfig{
			Enabled:           true,
			RequestsPerMinute: 3,
			BurstSize:         0, // 不允许突发请求
			TimeWindow:        1, // 1秒窗口
		},
	}
	r.Use(RateLimit(config))

	// 添加测试路由
	r.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "请求成功")
	})

	// 先发送3个请求 - 这些应该成功
	for i := 0; i < 3; i++ {
		req, _ := http.NewRequest("GET", "/test", nil)
		req.RemoteAddr = "192.168.1.2:1234" // 模拟相同的IP地址
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	}
	
	// 再发送一个请求 - 这个应该被限流
	req, _ := http.NewRequest("GET", "/test", nil)
	req.RemoteAddr = "192.168.1.2:1234" // 模拟相同的IP地址
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusTooManyRequests, w.Code)
}

func TestRateLimit_DifferentIPs(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置限流中间件 - 每秒允许2个请求
	config := &configs.Config{
		RateLimit: configs.RateLimitConfig{
			Enabled:           true,
			RequestsPerMinute: 2,
			BurstSize:         0, // 不允许突发请求
			TimeWindow:        1, // 1秒窗口
		},
	}
	r.Use(RateLimit(config))

	// 添加测试路由
	r.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "请求成功")
	})

	// 使用IP1发送请求
	for i := 0; i < 2; i++ {
		req, _ := http.NewRequest("GET", "/test", nil)
		req.RemoteAddr = "192.168.1.3:1234" // IP1
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	}
	
	// IP1超过限制，应该被拒绝
	req1, _ := http.NewRequest("GET", "/test", nil)
	req1.RemoteAddr = "192.168.1.3:1234" // IP1
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	
	assert.Equal(t, http.StatusTooManyRequests, w1.Code)
	
	// 使用IP2发送请求，应该成功
	req2, _ := http.NewRequest("GET", "/test", nil)
	req2.RemoteAddr = "192.168.1.4:1234" // IP2
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	
	assert.Equal(t, http.StatusOK, w2.Code)
}

func TestRateLimit_WindowReset(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置限流中间件 - 每秒允许1个请求
	config := &configs.Config{
		RateLimit: configs.RateLimitConfig{
			Enabled:           true,
			RequestsPerMinute: 1,
			BurstSize:         0, // 不允许突发请求
			TimeWindow:        1, // 1秒窗口
		},
	}
	r.Use(RateLimit(config))

	// 添加测试路由
	r.GET("/test", func(c *gin.Context) {
		c.String(http.StatusOK, "请求成功")
	})

	// 发送第一个请求 - 应该成功
	req1, _ := http.NewRequest("GET", "/test", nil)
	req1.RemoteAddr = "192.168.1.5:1234"
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	
	assert.Equal(t, http.StatusOK, w1.Code)
	
	// 发送第二个请求 - 应该失败
	req2, _ := http.NewRequest("GET", "/test", nil)
	req2.RemoteAddr = "192.168.1.5:1234"
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	
	assert.Equal(t, http.StatusTooManyRequests, w2.Code)
	
	// 等待时间窗口重置
	time.Sleep(1100 * time.Millisecond)
	
	// 发送第三个请求 - 窗口已重置，应该成功
	req3, _ := http.NewRequest("GET", "/test", nil)
	req3.RemoteAddr = "192.168.1.5:1234"
	w3 := httptest.NewRecorder()
	r.ServeHTTP(w3, req3)
	
	assert.Equal(t, http.StatusOK, w3.Code)
} 