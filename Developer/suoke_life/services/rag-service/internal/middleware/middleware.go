package middleware

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// LoggerMiddleware 日志中间件
func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 开始时间
		startTime := time.Now()

		// 处理请求
		c.Next()

		// 结束时间
		endTime := time.Now()

		// 请求耗时
		latency := endTime.Sub(startTime)

		// 请求方法
		method := c.Request.Method

		// 请求路由
		path := c.Request.URL.Path

		// 状态码
		statusCode := c.Writer.Status()

		// 客户端IP
		clientIP := c.ClientIP()

		// 打印日志
		if statusCode >= 500 {
			logger.Errorf("| %3d | %12v | %s | %s | %s |",
				statusCode, latency, clientIP, method, path)
		} else if statusCode >= 400 {
			logger.Warnf("| %3d | %12v | %s | %s | %s |",
				statusCode, latency, clientIP, method, path)
		} else {
			logger.Infof("| %3d | %12v | %s | %s | %s |",
				statusCode, latency, clientIP, method, path)
		}
	}
}

// CORSMiddleware CORS中间件
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Expose-Headers", "Content-Length")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}

// RequestIDMiddleware 请求ID中间件
func RequestIDMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从请求头获取请求ID
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			// 如果没有，生成一个新的请求ID
			requestID = generateRequestID()
		}

		// 设置请求ID
		c.Set("requestID", requestID)
		c.Writer.Header().Set("X-Request-ID", requestID)

		c.Next()
	}
}

// 生成请求ID
func generateRequestID() string {
	return time.Now().Format("20060102150405") + "-" + randomString(8)
}

// 生成随机字符串
func randomString(n int) string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, n)
	for i := range b {
		b[i] = letters[time.Now().UnixNano()%int64(len(letters))]
	}
	return string(b)
}

// MetricsMiddleware 指标中间件
func MetricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 记录开始时间
		startTime := time.Now()

		// 添加开始时间到上下文
		c.Set("startTime", startTime.UnixNano()/int64(time.Millisecond))

		// 处理请求
		c.Next()

		// 记录结束时间
		endTime := time.Now()
		c.Set("endTime", endTime.UnixNano()/int64(time.Millisecond))

		// 计算请求耗时
		latency := endTime.Sub(startTime).Seconds()

		// 获取请求方法和路径
		method := c.Request.Method
		path := c.Request.URL.Path

		// 获取状态码
		statusCode := c.Writer.Status()

		// 记录请求指标
		if metricsHandler, exists := c.Get("metricsHandler"); exists {
			handler := metricsHandler.(interface{})
			if recorder, ok := handler.(interface {
				RecordRequest(method, endpoint, status string)
				RecordRequestDuration(method, endpoint string, durationSeconds float64)
			}); ok {
				recorder.RecordRequest(method, path, http.StatusText(statusCode))
				recorder.RecordRequestDuration(method, path, latency)
			}
		}
	}
}

// RateLimitMiddleware 速率限制中间件
func RateLimitMiddleware(maxRequests int, per time.Duration) gin.HandlerFunc {
	// 创建令牌桶
	type client struct {
		tokens  int
		lastSeen time.Time
	}
	clients := make(map[string]*client)

	// 清理过期客户端
	go func() {
		for {
			time.Sleep(per)
			// 清理超过2*per时间没有请求的客户端
			for ip, cli := range clients {
				if time.Since(cli.lastSeen) > 2*per {
					delete(clients, ip)
				}
			}
		}
	}()

	return func(c *gin.Context) {
		ip := c.ClientIP()
		
		// 检查客户端是否存在
		if _, exists := clients[ip]; !exists {
			clients[ip] = &client{tokens: maxRequests, lastSeen: time.Now()}
		}

		cli := clients[ip]
		cli.lastSeen = time.Now()

		// 检查令牌是否足够
		if cli.tokens <= 0 {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"error":   "请求过于频繁",
				"message": "请稍后再试",
			})
			return
		}

		// 消耗一个令牌
		cli.tokens--

		// 处理请求
		c.Next()

		// 记录令牌使用
		go func() {
			// 每过一个时间周期，恢复一个令牌，最多到最大值
			time.Sleep(per / time.Duration(maxRequests))
			if cli.tokens < maxRequests {
				cli.tokens++
			}
		}()
	}
}

// TimeoutMiddleware 超时中间件
func TimeoutMiddleware(timeout time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 创建一个带有超时的上下文
		ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
		defer cancel()

		// 创建完成通道
		done := make(chan struct{})

		// 处理请求
		go func() {
			c.Request = c.Request.WithContext(ctx)
			c.Next()
			close(done)
		}()

		// 等待请求完成或超时
		select {
		case <-done:
			return
		case <-ctx.Done():
			// 超时处理
			c.AbortWithStatusJSON(http.StatusRequestTimeout, gin.H{
				"error":   "请求超时",
				"message": "请求处理时间超过限制",
			})
			return
		}
	}
} 