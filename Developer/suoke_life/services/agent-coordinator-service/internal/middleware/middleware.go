package middleware

import (
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/suoke-life/agent-coordinator-service/internal/config"
	"strconv"
	"time"
)

// RegisterMiddleware 注册所有中间件
func RegisterMiddleware(r *gin.Engine, cfg *config.Config) {
	// CORS中间件
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token", "Authorization", "Accept", "Cache-Control", "X-Requested-With"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// 日志中间件
	if cfg.LoggingEnabled {
		r.Use(LoggerMiddleware())
	}

	// 认证中间件
	if cfg.AuthEnabled {
		r.Use(APIKeyAuthMiddleware(cfg.ApiKey))
	}

	// 请求频率限制中间件
	if cfg.RateLimitEnabled {
		r.Use(RateLimitMiddleware(cfg.MaxRequestsPerMinute))
	}
}

// LoggerMiddleware 日志中间件
func LoggerMiddleware() gin.HandlerFunc {
	return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
		return time.Now().Format("2006/01/02 - 15:04:05") +
			" | " + strconv.Itoa(param.StatusCode) +
			" | " + param.Latency.String() +
			" | " + param.ClientIP +
			" | " + param.Method +
			" | " + param.Path + "\n"
	})
}

// APIKeyAuthMiddleware API密钥认证中间件
func APIKeyAuthMiddleware(apiKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 健康检查端点跳过认证
		if c.Request.URL.Path == "/health" {
			c.Next()
			return
		}

		// 校验API密钥
		key := c.GetHeader("Authorization")
		if key == "" {
			key = c.Query("api_key")
		}

		if key != apiKey {
			c.JSON(401, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "UNAUTHORIZED",
					"message": "未授权访问",
				},
			})
			c.Abort()
			return
		}

		c.Next()
	}
}

// RateLimitMiddleware 请求频率限制中间件
func RateLimitMiddleware(maxRequestsPerMinute int) gin.HandlerFunc {
	// 实际实现可能需要使用Redis或内存限速器
	return func(c *gin.Context) {
		// 简单示例，实际应用中应使用正确的限速器
		c.Next()
	}
} 