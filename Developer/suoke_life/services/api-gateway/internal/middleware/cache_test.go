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

func TestCache_Hit(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置缓存中间件 - 缓存时间1秒
	config := &configs.Config{
		Cache: configs.CacheConfig{
			Enabled:    true,
			DefaultTTL: 1, // 1秒
			ExcludePaths: []string{},
		},
	}
	
	// 定义计数器，用于验证缓存命中
	requestCount := 0
	
	// 使用缓存中间件
	r.GET("/cached", Cache(config), func(c *gin.Context) {
		requestCount++
		c.JSON(http.StatusOK, gin.H{
			"message": "数据",
			"time":    time.Now().Unix(),
		})
	})

	// 发送第一个请求 - 应该从服务器获取
	req1, _ := http.NewRequest("GET", "/cached", nil)
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	
	assert.Equal(t, http.StatusOK, w1.Code)
	assert.Equal(t, 1, requestCount) // 计数器应该是1
	
	// 发送第二个请求 - 应该从缓存获取
	req2, _ := http.NewRequest("GET", "/cached", nil)
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	
	assert.Equal(t, http.StatusOK, w2.Code)
	assert.Equal(t, 1, requestCount) // 计数器应该仍然是1，表示没有访问处理函数
	
	// 发送第三个请求 - 带不同的查询参数，应该从服务器获取
	req3, _ := http.NewRequest("GET", "/cached?param=value", nil)
	w3 := httptest.NewRecorder()
	r.ServeHTTP(w3, req3)
	
	assert.Equal(t, http.StatusOK, w3.Code)
	assert.Equal(t, 2, requestCount) // 计数器应该是2
}

func TestCache_Expiration(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置缓存中间件 - 非常短的缓存时间，便于测试
	config := &configs.Config{
		Cache: configs.CacheConfig{
			Enabled:    true,
			DefaultTTL: 1, // 1秒，但在测试中使用Sleep等待
			ExcludePaths: []string{},
		},
	}
	
	// 定义计数器，用于验证缓存命中
	requestCount := 0
	
	// 使用缓存中间件
	r.GET("/short-lived", Cache(config), func(c *gin.Context) {
		requestCount++
		c.JSON(http.StatusOK, gin.H{
			"message": "数据",
			"time":    time.Now().Unix(),
		})
	})

	// 发送第一个请求
	req1, _ := http.NewRequest("GET", "/short-lived", nil)
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	
	assert.Equal(t, http.StatusOK, w1.Code)
	assert.Equal(t, 1, requestCount)
	
	// 发送第二个请求 - 应该从缓存获取
	req2, _ := http.NewRequest("GET", "/short-lived", nil)
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	
	assert.Equal(t, http.StatusOK, w2.Code)
	assert.Equal(t, 1, requestCount) // 没有增加
	
	// 等待缓存过期
	time.Sleep(1200 * time.Millisecond)
	
	// 发送第三个请求 - 缓存应该已过期，应从服务器获取
	req3, _ := http.NewRequest("GET", "/short-lived", nil)
	w3 := httptest.NewRecorder()
	r.ServeHTTP(w3, req3)
	
	assert.Equal(t, http.StatusOK, w3.Code)
	assert.Equal(t, 2, requestCount) // 计数器应该是2
}

func TestCache_MethodExclusion(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置缓存中间件
	config := &configs.Config{
		Cache: configs.CacheConfig{
			Enabled:    true,
			DefaultTTL: 1, // 1秒
			ExcludePaths: []string{},
		},
	}
	
	// 定义计数器，用于验证缓存命中
	requestCount := 0
	
	// 使用缓存中间件
	r.Any("/method-test", Cache(config), func(c *gin.Context) {
		requestCount++
		c.JSON(http.StatusOK, gin.H{
			"method": c.Request.Method,
			"time":   time.Now().Unix(),
		})
	})

	// GET请求应该被缓存
	req1, _ := http.NewRequest("GET", "/method-test", nil)
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	
	assert.Equal(t, http.StatusOK, w1.Code)
	assert.Equal(t, 1, requestCount)
	
	// 再次GET请求应该从缓存获取
	req2, _ := http.NewRequest("GET", "/method-test", nil)
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	
	assert.Equal(t, http.StatusOK, w2.Code)
	assert.Equal(t, 1, requestCount) // 没有增加
	
	// POST请求不应被缓存
	req3, _ := http.NewRequest("POST", "/method-test", nil)
	w3 := httptest.NewRecorder()
	r.ServeHTTP(w3, req3)
	
	assert.Equal(t, http.StatusOK, w3.Code)
	assert.Equal(t, 2, requestCount) // 计数器应该是2
	
	// PUT请求不应被缓存
	req4, _ := http.NewRequest("PUT", "/method-test", nil)
	w4 := httptest.NewRecorder()
	r.ServeHTTP(w4, req4)
	
	assert.Equal(t, http.StatusOK, w4.Code)
	assert.Equal(t, 3, requestCount) // 计数器应该是3
}

func TestCache_PathExclusion(t *testing.T) {
	// 设置测试模式
	gin.SetMode(gin.TestMode)

	// 创建Gin路由
	r := gin.New()
	
	// 配置缓存中间件 - 排除某些路径
	config := &configs.Config{
		Cache: configs.CacheConfig{
			Enabled:    true,
			DefaultTTL: 1, // 1秒
			ExcludePaths: []string{
				"/api/v1/dynamic",
				"/api/v1/admin",
			},
		},
	}
	
	// 启用缓存
	r.Use(Cache(config))
	
	// 定义计数器，用于验证缓存命中
	requestCount := 0
	
	// 可缓存的路由
	r.GET("/api/v1/public", func(c *gin.Context) {
		requestCount++
		c.JSON(http.StatusOK, gin.H{"cacheable": true})
	})
	
	// 不可缓存的路由
	r.GET("/api/v1/dynamic", func(c *gin.Context) {
		requestCount++
		c.JSON(http.StatusOK, gin.H{"cacheable": false})
	})

	// 访问可缓存路由
	req1, _ := http.NewRequest("GET", "/api/v1/public", nil)
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	
	assert.Equal(t, http.StatusOK, w1.Code)
	assert.Equal(t, 1, requestCount)
	
	// 再次访问可缓存路由 - 应该从缓存获取
	req2, _ := http.NewRequest("GET", "/api/v1/public", nil)
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	
	assert.Equal(t, http.StatusOK, w2.Code)
	assert.Equal(t, 1, requestCount) // 没有增加
	
	// 访问不可缓存路由
	req3, _ := http.NewRequest("GET", "/api/v1/dynamic", nil)
	w3 := httptest.NewRecorder()
	r.ServeHTTP(w3, req3)
	
	assert.Equal(t, http.StatusOK, w3.Code)
	assert.Equal(t, 2, requestCount) // 计数器应该是2
	
	// 再次访问不可缓存路由 - 不应该从缓存获取
	req4, _ := http.NewRequest("GET", "/api/v1/dynamic", nil)
	w4 := httptest.NewRecorder()
	r.ServeHTTP(w4, req4)
	
	assert.Equal(t, http.StatusOK, w4.Code)
	assert.Equal(t, 3, requestCount) // 计数器应该是3
} 