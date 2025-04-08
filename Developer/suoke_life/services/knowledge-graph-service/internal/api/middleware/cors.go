package middleware

import (
	"net/http"
	"strings"
	
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

// CORSConfig CORS配置
type CORSConfig struct {
	// AllowOrigins 允许的来源域名，多个用逗号分隔
	AllowOrigins string
	
	// AllowMethods 允许的HTTP方法，多个用逗号分隔
	AllowMethods string
	
	// AllowHeaders 允许的请求头，多个用逗号分隔
	AllowHeaders string
	
	// ExposeHeaders 暴露的响应头，多个用逗号分隔
	ExposeHeaders string
	
	// AllowCredentials 是否允许携带凭证
	AllowCredentials bool
	
	// MaxAge 预检请求的缓存时间（秒）
	MaxAge int
}

// DefaultCORSConfig 默认CORS配置
func DefaultCORSConfig() CORSConfig {
	return CORSConfig{
		AllowOrigins:     "*",
		AllowMethods:     "GET,POST,PUT,PATCH,DELETE,OPTIONS",
		AllowHeaders:     "Origin,Content-Type,Accept,Authorization,X-Requested-With,X-Request-ID",
		ExposeHeaders:    "Content-Length,X-Request-ID",
		AllowCredentials: true,
		MaxAge:           86400, // 24小时
	}
}

// CORS 创建CORS中间件
func CORS(config CORSConfig) gin.HandlerFunc {
	return func(c *gin.Context) {
		origin := c.Request.Header.Get("Origin")
		
		// 验证来源
		if origin != "" && config.AllowOrigins != "" {
			// 默认情况下，允许所有来源
			if config.AllowOrigins == "*" && !config.AllowCredentials {
				c.Header("Access-Control-Allow-Origin", "*")
			} else {
				// 检查是否是允许的来源
				allowOrigins := strings.Split(config.AllowOrigins, ",")
				isAllowed := false
				
				for _, allowOrigin := range allowOrigins {
					if allowOrigin == "*" || allowOrigin == origin {
						isAllowed = true
						break
					}
				}
				
				if isAllowed {
					c.Header("Access-Control-Allow-Origin", origin)
				}
			}
		}
		
		// 设置其他CORS头
		if config.AllowMethods != "" {
			c.Header("Access-Control-Allow-Methods", config.AllowMethods)
		}
		
		if config.AllowHeaders != "" {
			c.Header("Access-Control-Allow-Headers", config.AllowHeaders)
		}
		
		if config.ExposeHeaders != "" {
			c.Header("Access-Control-Expose-Headers", config.ExposeHeaders)
		}
		
		if config.AllowCredentials {
			c.Header("Access-Control-Allow-Credentials", "true")
		}
		
		if config.MaxAge > 0 {
			c.Header("Access-Control-Max-Age", string(config.MaxAge))
		}
		
		// 处理预检请求
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		
		c.Next()
	}
}

// DefaultCORS 使用默认配置的CORS中间件
func DefaultCORS() gin.HandlerFunc {
	// 使用gin-contrib/cors包实现
	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	config.AllowMethods = []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"Origin", "Content-Type", "Accept", "Authorization", "X-Requested-With", "X-Request-ID"}
	config.ExposeHeaders = []string{"Content-Length", "X-Request-ID"}
	config.AllowCredentials = true
	config.MaxAge = 86400
	
	return cors.New(config)
}

// Cors 使用默认配置返回CORS中间件（为了兼容性）
func Cors() gin.HandlerFunc {
	return DefaultCORS()
} 