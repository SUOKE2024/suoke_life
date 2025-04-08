package middleware

import (
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
			if appErr.HTTPStatus >= 500 {
				logger.Errorf("请求处理错误: [%s] %s, Trace ID: %s, Details: %+v",
					appErr.Code, appErr.Message, appErr.TraceID, appErr.Details)
			} else {
				logger.Warnf("请求处理错误: [%s] %s, Trace ID: %s, Details: %+v",
					appErr.Code, appErr.Message, appErr.TraceID, appErr.Details)
			}
			
			// 返回标准错误响应
			errorResponse := ErrorResponse{
				Error:     *appErr,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			
			c.AbortWithStatusJSON(appErr.HTTPStatus, errorResponse)
		}
	}
}

// 包含敏感信息检查
func containsSensitiveInfo(str string) bool {
	sensitivePatterns := []string{
		"password", "token", "secret", "key", "credential", "api_key", "auth",
	}
	
	lowered := strings.ToLower(str)
	for _, pattern := range sensitivePatterns {
		if strings.Contains(lowered, pattern) {
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
			lines[i] = "[内容已屏蔽]"
		}
	}
	return strings.Join(lines, "\n")
}

// 净化错误消息
func sanitizeErrorMessage(message string) string {
	if containsSensitiveInfo(message) {
		return "系统错误，请联系管理员"
	}
	return message
}