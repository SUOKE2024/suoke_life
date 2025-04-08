package middleware

import (
	"context"
	"fmt"
	"net/http"
	"runtime/debug"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// 标准错误码定义
const (
	// 客户端错误 (4xx)
	ErrBadRequest           = "BAD_REQUEST"           // 400
	ErrUnauthorized         = "UNAUTHORIZED"          // 401
	ErrForbidden            = "FORBIDDEN"             // 403
	ErrNotFound             = "NOT_FOUND"             // 404
	ErrMethodNotAllowed     = "METHOD_NOT_ALLOWED"    // 405
	ErrTimeout              = "TIMEOUT"               // 408
	ErrConflict             = "CONFLICT"              // 409
	ErrPayloadTooLarge      = "PAYLOAD_TOO_LARGE"     // 413
	ErrTooManyRequests      = "TOO_MANY_REQUESTS"     // 429
	
	// 服务端错误 (5xx)
	ErrInternalServer       = "INTERNAL_SERVER_ERROR" // 500
	ErrNotImplemented       = "NOT_IMPLEMENTED"       // 501
	ErrBadGateway           = "BAD_GATEWAY"           // 502
	ErrServiceUnavailable   = "SERVICE_UNAVAILABLE"   // 503
	ErrGatewayTimeout       = "GATEWAY_TIMEOUT"       // 504
	
	// 业务错误 (自定义)
	ErrValidation           = "VALIDATION_ERROR"
	ErrDatabase             = "DATABASE_ERROR"
	ErrExternalService      = "EXTERNAL_SERVICE_ERROR"
	ErrVectorStore          = "VECTOR_STORE_ERROR"
	ErrEmbedding            = "EMBEDDING_ERROR"
	ErrRagQuery             = "RAG_QUERY_ERROR"
)

// AppError 应用错误结构
type AppError struct {
	Code       string      `json:"code"`
	Message    string      `json:"message"`
	Details    interface{} `json:"details,omitempty"`
	TraceID    string      `json:"trace_id"`
	HTTPStatus int         `json:"-"`
}

// Error 实现error接口
func (e AppError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

// ErrorResponse 错误响应结构
type ErrorResponse struct {
	Error     AppError `json:"error"`
	Timestamp string   `json:"timestamp"`
}

// NewAppError 创建应用错误
func NewAppError(code string, message string, httpStatus int, details interface{}) *AppError {
	return &AppError{
		Code:       code,
		Message:    message,
		Details:    details,
		TraceID:    uuid.New().String(),
		HTTPStatus: httpStatus,
	}
}

// BadRequestError 创建400错误
func BadRequestError(message string, details interface{}) *AppError {
	return NewAppError(ErrBadRequest, message, http.StatusBadRequest, details)
}

// UnauthorizedError 创建401错误
func UnauthorizedError(message string) *AppError {
	return NewAppError(ErrUnauthorized, message, http.StatusUnauthorized, nil)
}

// ForbiddenError 创建403错误
func ForbiddenError(message string) *AppError {
	return NewAppError(ErrForbidden, message, http.StatusForbidden, nil)
}

// NotFoundError 创建404错误
func NotFoundError(message string) *AppError {
	return NewAppError(ErrNotFound, message, http.StatusNotFound, nil)
}

// InternalServerError 创建500错误
func InternalServerError(message string, details interface{}) *AppError {
	return NewAppError(ErrInternalServer, message, http.StatusInternalServerError, details)
}

// ValidationError 创建验证错误
func ValidationError(message string, details interface{}) *AppError {
	return NewAppError(ErrValidation, message, http.StatusBadRequest, details)
}

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

// ErrorMiddleware 错误处理中间件
func ErrorMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 为请求添加跟踪ID
		traceID := uuid.New().String()
		c.Set("traceID", traceID)
		c.Header("X-Trace-ID", traceID)

		// 处理异常
		defer func() {
			if err := recover(); err != nil {
				// 获取堆栈信息
				stack := debug.Stack()
				
				// 屏蔽堆栈中的敏感信息
				stackStr := maskSensitiveInfo(string(stack))
				
				// 记录错误
				logger.Errorf("处理请求时发生异常: %v\nTrace ID: %s\n堆栈: %s", 
					err, traceID, stackStr)
				
				// 返回标准错误响应
				appErr := InternalServerError("服务器内部错误", nil)
				appErr.TraceID = traceID
				
				errorResponse := ErrorResponse{
					Error:     *appErr,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				
				c.AbortWithStatusJSON(appErr.HTTPStatus, errorResponse)
			}
		}()

		// 处理请求
		c.Next()

		// 检查错误
		if len(c.Errors) > 0 {
			// 获取最后一个错误
			err := c.Errors.Last().Err
			var appErr *AppError
			var httpStatus int = http.StatusInternalServerError
			var errorCode string = ErrInternalServer
			var errorMessage string = "服务器内部错误"
			var details interface{} = nil
			
			// 尝试将错误转换为AppError
			switch e := err.(type) {
			case *AppError:
				appErr = e
			case error:
				errorMessage = sanitizeErrorMessage(e.Error())
				// 根据错误类型判断错误码
				if strings.Contains(errorMessage, "不存在") || 
				   strings.Contains(errorMessage, "找不到") {
					errorCode = ErrNotFound
					httpStatus = http.StatusNotFound
				} else if strings.Contains(errorMessage, "超时") {
					errorCode = ErrTimeout
					httpStatus = http.StatusRequestTimeout
				} else if strings.Contains(errorMessage, "验证") || 
				          strings.Contains(errorMessage, "无效") {
					errorCode = ErrValidation
					httpStatus = http.StatusBadRequest
				}
				appErr = NewAppError(errorCode, errorMessage, httpStatus, details)
			}
			
			// 确保有TraceID
			if appErr.TraceID == "" {
				appErr.TraceID = traceID
			}
			
			// 记录错误
			logLevel := "ERROR"
			if appErr.HTTPStatus >= 500 {
				logLevel = "ERROR"
			} else {
				logLevel = "WARN"
			}
			
			logger.Log(logLevel, fmt.Sprintf("请求处理错误: [%s] %s, Trace ID: %s, Details: %+v",
				appErr.Code, appErr.Message, appErr.TraceID, appErr.Details))
			
			// 返回标准错误响应
			errorResponse := ErrorResponse{
				Error:     *appErr,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			
			c.AbortWithStatusJSON(appErr.HTTPStatus, errorResponse)
		}
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

// 检查是否包含敏感信息
func containsSensitiveInfo(str string) bool {
	sensitivePatterns := []string{
		"password", "passwd", "secret", "token", "key", "auth",
		"api_key", "apikey", "access_key", "credential",
	}
	
	str = strings.ToLower(str)
	for _, pattern := range sensitivePatterns {
		if strings.Contains(str, pattern) {
			return true
		}
	}
	
	return false
}

// 屏蔽敏感信息
func maskSensitiveInfo(stack string) string {
	lines := strings.Split(stack, "\n")
	for i, line := range lines {
		if containsSensitiveInfo(line) {
			lines[i] = "*** SENSITIVE DATA REDACTED ***"
		}
	}
	return strings.Join(lines, "\n")
}

// 清理错误消息，移除敏感信息
func sanitizeErrorMessage(message string) string {
	if containsSensitiveInfo(message) {
		return "发生错误，包含敏感信息已被屏蔽"
	}
	return message
} 