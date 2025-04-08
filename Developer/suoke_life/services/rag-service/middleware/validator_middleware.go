package middleware

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// TimeFormat 标准时间格式
const TimeFormat = time.RFC3339

// TimeNow 获取当前时间
func TimeNow() time.Time {
	return time.Now()
}

// 全局验证器实例
var validate = validator.New()

// 最大请求体大小 (5MB)
const maxBodySize = 5 * 1024 * 1024

// 敏感关键词列表
var sensitiveKeywords = []string{
	"script", "<script", "javascript:", "data:", "vbscript:",
	"onload=", "onerror=", "onclick=", "onmouseover=", "alert(",
	"SELECT", "UPDATE", "DELETE", "INSERT", "DROP", "UNION",
	"--", "/*", "*/", ";--", "1=1", "OR 1=1",
}

// RequestLogger 记录请求日志中间件
func RequestLogger() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取请求方法和路径
		method := c.Request.Method
		path := c.Request.URL.Path
		
		// 从上下文获取跟踪ID
		traceID, _ := c.Get("traceID")
		traceIDStr, ok := traceID.(string)
		if !ok {
			traceIDStr = "unknown"
		}
		
		// 开始处理前记录请求
		logger.Infof("[%s] 开始处理 %s %s", traceIDStr, method, path)
		
		// 处理请求
		c.Next()
		
		// 获取响应状态
		status := c.Writer.Status()
		
		// 根据状态码使用不同的日志级别
		if status >= 500 {
			logger.Errorf("[%s] %s %s 完成，状态: %d", traceIDStr, method, path, status)
		} else if status >= 400 {
			logger.Warnf("[%s] %s %s 完成，状态: %d", traceIDStr, method, path, status)
		} else {
			logger.Infof("[%s] %s %s 完成，状态: %d", traceIDStr, method, path, status)
		}
	}
}

// ValidateRequestBody 验证请求体中间件
func ValidateRequestBody() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 跳过GET请求
		if c.Request.Method == http.MethodGet {
			c.Next()
			return
		}
		
		// 获取Content-Type
		contentType := c.GetHeader("Content-Type")
		
		// 只处理JSON请求
		if strings.Contains(contentType, "application/json") {
			// 限制请求体大小
			if c.Request.ContentLength > maxBodySize {
				logger.Warnf("请求体过大: %d bytes", c.Request.ContentLength)
				c.AbortWithStatusJSON(http.StatusRequestEntityTooLarge, ErrorResponse{
					Error: *BadRequestError("请求数据过大", map[string]interface{}{
						"max_size": maxBodySize,
						"size": c.Request.ContentLength,
					}),
					Timestamp: getTimestamp(),
				})
				return
			}
			
			// 读取原始请求体
			bodyBytes, err := io.ReadAll(c.Request.Body)
			if err != nil {
				logger.Errorf("读取请求体失败: %v", err)
				c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
					Error: *BadRequestError("无法读取请求数据", nil),
					Timestamp: getTimestamp(),
				})
				return
			}
			
			// 检查是否为有效的JSON
			if !isValidJSON(bodyBytes) {
				logger.Warnf("无效的JSON数据")
				c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
					Error: *BadRequestError("无效的JSON格式", nil),
					Timestamp: getTimestamp(),
				})
				return
			}
			
			// 检查敏感内容
			rawBody := string(bodyBytes)
			if containsMaliciousContent(rawBody) {
				logger.Warnf("检测到可能的恶意内容")
				c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
					Error: *BadRequestError("请求包含可能的恶意内容", nil),
					Timestamp: getTimestamp(),
				})
				return
			}
			
			// 重新设置请求体以供后续中间件使用
			c.Request.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))
		}
		
		c.Next()
	}
}

// ValidateQueryParams 验证查询参数中间件
func ValidateQueryParams() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取所有查询参数
		queries := c.Request.URL.Query()
		
		// 检查每个参数是否包含恶意内容
		for key, values := range queries {
			for _, value := range values {
				if containsMaliciousContent(value) {
					logger.Warnf("查询参数包含可能的恶意内容: %s=%s", key, value)
					c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
						Error: *BadRequestError("查询参数包含可能的恶意内容", nil),
						Timestamp: getTimestamp(),
					})
					return
				}
			}
		}
		
		c.Next()
	}
}

// RateLimiter 速率限制中间件（简单实现，实际应使用更复杂的限流算法和存储）
var requestCount = make(map[string]int)

func RateLimiter(maxRequests int, timeWindow string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取客户端IP
		clientIP := c.ClientIP()
		
		// 检查请求次数
		if count, ok := requestCount[clientIP]; ok && count >= maxRequests {
			logger.Warnf("客户端 %s 请求过于频繁", clientIP)
			c.AbortWithStatusJSON(http.StatusTooManyRequests, ErrorResponse{
				Error: *NewAppError(ErrTooManyRequests, "请求过于频繁，请稍后再试", http.StatusTooManyRequests, nil),
				Timestamp: getTimestamp(),
			})
			return
		}
		
		// 增加请求计数
		if _, ok := requestCount[clientIP]; !ok {
			requestCount[clientIP] = 0
		}
		requestCount[clientIP]++
		
		c.Next()
	}
}

// ContentSecurityPolicy 内容安全策略中间件
func ContentSecurityPolicy() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 设置CSP头
		c.Header("Content-Security-Policy", "default-src 'self'; script-src 'self'; object-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
		c.Next()
	}
}

// SecurityHeaders 安全头部中间件
func SecurityHeaders() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 设置安全HTTP标头
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("X-Frame-Options", "DENY")
		c.Header("X-XSS-Protection", "1; mode=block")
		c.Header("Referrer-Policy", "strict-origin-when-cross-origin")
		c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		c.Next()
	}
}

// CORS 跨域资源共享中间件
func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*") // 应限制为特定域名
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Api-Key")
		c.Header("Access-Control-Allow-Credentials", "true")
		c.Header("Access-Control-Max-Age", "86400") // 24小时
		
		// 处理OPTIONS请求
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		
		c.Next()
	}
}

// 辅助函数 - 检查是否为有效的JSON
func isValidJSON(data []byte) bool {
	var js json.RawMessage
	return json.Unmarshal(data, &js) == nil
}

// 辅助函数 - 检查是否包含恶意内容
func containsMaliciousContent(content string) bool {
	// 转换为小写以进行不区分大小写的检查
	lowerContent := strings.ToLower(content)
	
	// 检查SQL注入和XSS尝试
	for _, keyword := range sensitiveKeywords {
		if strings.Contains(lowerContent, strings.ToLower(keyword)) {
			return true
		}
	}
	
	return false
}

// 辅助函数 - 获取当前时间戳
func getTimestamp() string {
	return TimeNow().Format(TimeFormat)
} 