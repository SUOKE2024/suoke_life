package middleware

import (
	"net/http"
	"strconv"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke-life/api-gateway/internal/configs"
)

// ClientLimit 客户端请求限制信息
type ClientLimit struct {
	Count      int       // 当前已处理的请求计数
	ResetTime  time.Time // 重置计数的时间
	Blocked    bool      // 是否被阻止
	BlockUntil time.Time // 阻止解除的时间
}

// RateLimiter 速率限制器
type RateLimiter struct {
	Limit      int           // 在时间窗口内允许的最大请求数
	BurstSize  int           // 允许的突发请求数
	TimeWindow time.Duration // 时间窗口大小
	Clients    map[string]*ClientLimit
	mu         sync.Mutex
}

// NewRateLimiter 创建一个新的速率限制器
func NewRateLimiter(limit, burstSize, timeWindowSeconds int) *RateLimiter {
	limiter := &RateLimiter{
		Limit:      limit,
		BurstSize:  burstSize,
		TimeWindow: time.Duration(timeWindowSeconds) * time.Second,
		Clients:    make(map[string]*ClientLimit),
	}

	// 启动清理过期客户端的goroutine
	go limiter.cleanupLoop()

	return limiter
}

// cleanupLoop 定期清理过期的客户端记录
func (r *RateLimiter) cleanupLoop() {
	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		r.cleanup()
	}
}

// cleanup 清理过期的客户端记录
func (r *RateLimiter) cleanup() {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()
	for ip, client := range r.Clients {
		// 如果客户端被阻止但阻止时间已过，或者重置时间已过且未被阻止
		if (client.Blocked && now.After(client.BlockUntil)) ||
			(!client.Blocked && now.After(client.ResetTime)) {
			delete(r.Clients, ip)
		}
	}
}

// Allow 检查是否允许客户端请求
func (r *RateLimiter) Allow(clientIP string) (bool, int) {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()

	client, exists := r.Clients[clientIP]
	if !exists {
		// 新客户端
		r.Clients[clientIP] = &ClientLimit{
			Count:     1,
			ResetTime: now.Add(r.TimeWindow),
			Blocked:   false,
		}
		return true, r.Limit - 1
	}

	// 检查客户端是否被阻止
	if client.Blocked {
		if now.After(client.BlockUntil) {
			// 阻止时间已过，重置客户端
			client.Blocked = false
			client.Count = 1
			client.ResetTime = now.Add(r.TimeWindow)
			return true, r.Limit - 1
		}
		return false, 0
	}

	// 检查是否需要重置计数
	if now.After(client.ResetTime) {
		client.Count = 1
		client.ResetTime = now.Add(r.TimeWindow)
		return true, r.Limit - 1
	}

	// 增加计数并检查是否超过限制
	client.Count++
	if client.Count > r.Limit+r.BurstSize {
		// 超过突发限制，阻止客户端
		client.Blocked = true
		client.BlockUntil = now.Add(r.TimeWindow)
		return false, 0
	}

	// 如果超过基本限制但未超过突发限制，仍然允许但返回0表示没有剩余请求
	if client.Count > r.Limit {
		return true, 0
	}

	// 允许请求并返回剩余请求数
	return true, r.Limit - client.Count
}

// RateLimit Gin中间件，用于速率限制
func RateLimit(config *configs.Config) gin.HandlerFunc {
	if !config.RateLimit.Enabled {
		// 如果速率限制未启用，返回一个空的中间件
		return func(c *gin.Context) {
			c.Next()
		}
	}

	limiter := NewRateLimiter(
		config.RateLimit.RequestsPerMinute,
		config.RateLimit.BurstSize,
		config.RateLimit.TimeWindow,
	)

	return func(c *gin.Context) {
		// 获取客户端IP
		clientIP := c.ClientIP()
		
		// 检查是否允许请求
		allowed, remaining := limiter.Allow(clientIP)
		
		// 设置速率限制响应头
		limit := config.RateLimit.RequestsPerMinute
		c.Header("X-RateLimit-Limit", strconv.Itoa(limit))
		c.Header("X-RateLimit-Remaining", strconv.Itoa(remaining))
		
		if !allowed {
			// 如果不允许请求，返回429状态码
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error": "请求频率过高，请稍后再试",
			})
			c.Abort()
			return
		}
		
		c.Next()
	}
}