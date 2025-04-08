package middleware

import (
	"fmt"
	"net"
	"net/http"
	"net/http/httputil"
	"os"
	"runtime/debug"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// 添加本地错误响应函数，替换对response包的依赖
func sendErrorResponse(c *gin.Context, status int, errCode, message string) {
	c.JSON(status, gin.H{
		"success": false,
		"code":    errCode,
		"message": message,
	})
}

// RecoveryWithLogger 使用日志记录器的恢复中间件
func RecoveryWithLogger(logger *zap.Logger) gin.HandlerFunc {
	return CustomRecovery(logger, DefaultRecoveryHandler(logger))
}

// CustomRecovery 自定义恢复中间件
func CustomRecovery(logger *zap.Logger, handler gin.RecoveryFunc) gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				stack := string(debug.Stack())
				logger.Error("请求处理中发生恐慌",
					zap.Any("error", err),
					zap.String("stack", stack),
					zap.String("request_id", GetRequestID(c)),
					zap.String("method", c.Request.Method),
					zap.String("path", c.Request.URL.Path),
				)

				// 调用恢复处理函数
				handler(c, err)
			}
		}()
		c.Next()
	}
}

// DefaultRecoveryHandler 默认恢复处理函数
func DefaultRecoveryHandler(logger *zap.Logger) gin.RecoveryFunc {
	return func(c *gin.Context, err interface{}) {
		// 记录错误信息
		logger.Error("恢复处理",
			zap.Any("error", err),
			zap.String("request_id", GetRequestID(c)),
		)
		
		// 发送错误响应
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"code":    "internal_error",
			"message": "服务器内部错误",
			"details": sanitizeErrorDetails(fmt.Sprint(err)),
		})
	}
}

// RecoveryMiddleware 错误恢复中间件
func RecoveryMiddleware(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				// 记录错误堆栈
				stack := debug.Stack()
				
				logger.Error("错误恢复",
					zap.Any("error", err),
					zap.ByteString("stack", stack),
					zap.String("request_id", GetRequestID(c)),
					zap.String("url", c.Request.URL.String()),
					zap.String("method", c.Request.Method),
				)
				
				// 发送错误响应
				c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
					"success": false,
					"code":    "internal_error",
					"message": "服务器内部错误",
					"details": sanitizeErrorDetails(fmt.Sprint(err)),
				})
			}
		}()
		c.Next()
	}
}

// ErrorHandler 全局错误处理中间件
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()
		
		// 处理请求过程中的错误
		if len(c.Errors) > 0 {
			// 获取最后一个错误
			err := c.Errors.Last()
			
			// 根据错误类型返回相应的状态码和消息
			statusCode := http.StatusInternalServerError
			errorCode := "internal_error"
			errorMessage := "服务器内部错误"
			
			// 检查是否包含状态码元数据
			if err.Meta != nil {
				if status, ok := err.Meta.(int); ok {
					statusCode = status
				}
			}
			
			// 根据状态码设置错误代码和消息
			switch statusCode {
			case http.StatusBadRequest:
				errorCode = "bad_request"
				errorMessage = "请求参数无效"
			case http.StatusUnauthorized:
				errorCode = "unauthorized"
				errorMessage = "未经授权的请求"
			case http.StatusForbidden:
				errorCode = "forbidden"
				errorMessage = "禁止访问"
			case http.StatusNotFound:
				errorCode = "not_found"
				errorMessage = "资源不存在"
			case http.StatusMethodNotAllowed:
				errorCode = "method_not_allowed"
				errorMessage = "请求方法不允许"
			case http.StatusConflict:
				errorCode = "conflict"
				errorMessage = "资源冲突"
			case http.StatusTooManyRequests:
				errorCode = "too_many_requests"
				errorMessage = "请求频率过高"
			}
			
			// 发送错误响应
			c.AbortWithStatusJSON(statusCode, gin.H{
				"success": false,
				"code":    errorCode,
				"message": errorMessage,
				"details": sanitizeErrorDetails(err.Error()),
			})
		}
	}
}

// sanitizeErrorDetails 清理错误详情
func sanitizeErrorDetails(errMsg string) string {
	// 在生产环境中可能需要移除敏感信息
	// 这里简单处理，移除可能的SQL错误、文件路径等
	
	// 过滤掉文件路径
	errMsg = filterFilePaths(errMsg)
	
	// 限制错误消息长度
	if len(errMsg) > 200 {
		errMsg = errMsg[:200] + "..."
	}
	
	return errMsg
}

// filterFilePaths 过滤文件路径
func filterFilePaths(msg string) string {
	// 简单实现，过滤掉常见的文件路径格式
	pathPatterns := []string{
		"/var/",
		"/etc/",
		"/home/",
		"/usr/",
		"/tmp/",
		"/go/",
		"/app/",
	}
	
	for _, pattern := range pathPatterns {
		if strings.Contains(msg, pattern) {
			// 替换为安全的表示
			msg = strings.ReplaceAll(msg, pattern, "[PATH]/")
		}
	}
	
	return msg
}

// FullRecoveryHandler 提供更详细的请求信息记录
func FullRecoveryHandler(logger *zap.Logger) gin.RecoveryFunc {
	return func(c *gin.Context, err interface{}) {
		// 获取当前时间
		now := time.Now()
		
		// 尝试获取请求信息
		var requestData []byte
		var clientIP string
		
		if req := c.Request; req != nil {
			if httpRequest, err := httputil.DumpRequest(req, false); err == nil {
				requestData = httpRequest
			}
			
			clientIP = c.ClientIP()
			if host, _, netErr := net.SplitHostPort(req.RemoteAddr); netErr == nil {
				clientIP = host
			}
		}
		
		// 记录到日志文件
		logFilePath := "logs/panic-" + now.Format("2006-01-02") + ".log"
		if logFile, err := os.OpenFile(logFilePath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644); err == nil {
			defer logFile.Close()
			
			fmt.Fprintf(logFile, "[Panic Recovery] %v\n", now.Format(time.RFC3339))
			fmt.Fprintf(logFile, "Error: %v\n", err)
			fmt.Fprintf(logFile, "Request: %s\n", string(requestData))
			fmt.Fprintf(logFile, "Client IP: %s\n", clientIP)
			fmt.Fprintf(logFile, "Stack Trace:\n%s\n\n", string(debug.Stack()))
		}
		
		// 记录错误信息
		logger.Error("恢复处理",
			zap.Any("error", err),
			zap.String("request_id", GetRequestID(c)),
			zap.String("client_ip", clientIP),
			zap.String("timestamp", now.Format(time.RFC3339)),
		)
		
		// 发送错误响应
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"code":    "internal_error",
			"message": "服务器内部错误",
			"details": sanitizeErrorDetails(fmt.Sprint(err)),
		})
	}
} 