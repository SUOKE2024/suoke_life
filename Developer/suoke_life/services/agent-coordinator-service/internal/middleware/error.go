package middleware

import (
	"fmt"
	"log"
	"net/http"
	"runtime/debug"

	"github.com/gin-gonic/gin"
)

// ErrorResponse 标准错误响应结构
type ErrorResponse struct {
	Code      string      `json:"code"`               // 错误代码
	Message   string      `json:"message"`            // 错误消息
	Details   interface{} `json:"details,omitempty"`  // 详细错误信息
	RequestID string      `json:"requestId,omitempty"` // 请求ID，用于跟踪
}

// 预定义错误代码
const (
	ErrCodeInvalidRequest   = "INVALID_REQUEST"
	ErrCodeUnauthorized     = "UNAUTHORIZED"
	ErrCodeForbidden        = "FORBIDDEN"
	ErrCodeNotFound         = "NOT_FOUND"
	ErrCodeInternalError    = "INTERNAL_ERROR"
	ErrCodeServiceUnavailable = "SERVICE_UNAVAILABLE"
	ErrCodeValidationFailed = "VALIDATION_FAILED"
)

// ErrorHandler 统一错误处理中间件
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 生成请求ID
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = fmt.Sprintf("%d", c.Request.Context().Value("RequestID"))
		}
		
		// 设置请求ID
		c.Set("RequestID", requestID)
		c.Header("X-Request-ID", requestID)
		
		// 错误恢复
		defer func() {
			if err := recover(); err != nil {
				// 记录堆栈信息
				stack := debug.Stack()
				log.Printf("[严重错误] 发生崩溃: %v\n%s", err, stack)
				
				// 返回500错误
				c.AbortWithStatusJSON(http.StatusInternalServerError, ErrorResponse{
					Code:      ErrCodeInternalError,
					Message:   "服务器内部错误",
					Details:   fmt.Sprintf("%v", err),
					RequestID: requestID,
				})
			}
		}()
		
		c.Next()
		
		// 检查是否有错误
		if len(c.Errors) > 0 {
			// 记录所有错误
			for _, e := range c.Errors {
				log.Printf("[错误] %s: %s", requestID, e.Error())
			}
			
			// 如果还没有响应，返回一个默认的错误响应
			if !c.Writer.Written() {
				statusCode := c.Writer.Status()
				if statusCode == http.StatusOK {
					statusCode = http.StatusInternalServerError
				}
				
				var code string
				switch statusCode {
				case http.StatusBadRequest:
					code = ErrCodeInvalidRequest
				case http.StatusUnauthorized:
					code = ErrCodeUnauthorized
				case http.StatusForbidden:
					code = ErrCodeForbidden
				case http.StatusNotFound:
					code = ErrCodeNotFound
				case http.StatusServiceUnavailable:
					code = ErrCodeServiceUnavailable
				default:
					code = ErrCodeInternalError
				}
				
				c.JSON(statusCode, ErrorResponse{
					Code:      code,
					Message:   c.Errors.Last().Error(),
					RequestID: requestID,
				})
			}
		}
	}
}

// HandleError 便捷错误处理函数，用于处理程序内部
func HandleError(c *gin.Context, statusCode int, code string, message string, details interface{}) {
	requestID, _ := c.Get("RequestID")
	
	log.Printf("[错误] %v: %s - %s", requestID, code, message)
	
	c.JSON(statusCode, ErrorResponse{
		Code:      code,
		Message:   message,
		Details:   details,
		RequestID: fmt.Sprintf("%v", requestID),
	})
}