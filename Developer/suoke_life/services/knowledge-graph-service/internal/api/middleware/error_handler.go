package middleware

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// ErrorResponse 统一错误响应结构
type ErrorResponse struct {
	Success bool   `json:"success"`
	Code    string `json:"code"`
	Message string `json:"message"`
	Details string `json:"details,omitempty"`
}

// CreateErrorResponse 创建错误响应
func CreateErrorResponse(code string, message string, details string) ErrorResponse {
	return ErrorResponse{
		Success: false,
		Code:    code,
		Message: message,
		Details: details,
	}
}

// ToJSON 将错误响应转换为JSON字符串
func (e ErrorResponse) ToJSON() string {
	bytes, _ := json.Marshal(e)
	return string(bytes)
}

// CustomErrorHandler 自定义错误处理器
// 根据错误类型返回相应的HTTP状态码和错误信息
func CustomErrorHandler(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 处理请求
		c.Next()
		
		// 如果没有错误，直接返回
		if len(c.Errors) == 0 {
			return
		}
		
		// 获取最后一个错误
		err := c.Errors.Last()
		
		// 记录错误
		logger.Error("请求处理错误",
			zap.String("error", err.Error()),
			zap.String("path", c.Request.URL.Path),
			zap.String("method", c.Request.Method),
			zap.String("request_id", GetRequestID(c)),
		)
		
		// 默认状态码和错误信息
		statusCode := http.StatusInternalServerError
		errorCode := "internal_error"
		errorMessage := "服务器内部错误"
		errorDetails := err.Error()
		
		// 尝试从错误元数据中获取状态码
		if err.Meta != nil {
			if code, ok := err.Meta.(int); ok {
				statusCode = code
			}
		}
		
		// 根据状态码设置相应的错误代码和消息
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
		case http.StatusConflict:
			errorCode = "conflict"
			errorMessage = "资源冲突"
		case http.StatusTooManyRequests:
			errorCode = "too_many_requests"
			errorMessage = "请求频率过高"
		}
		
		// 检查是否为验证错误
		if strings.Contains(err.Error(), "validation") {
			errorCode = "validation_error"
			errorMessage = "数据验证失败"
		}
		
		// 限制错误详情长度
		if len(errorDetails) > 200 {
			errorDetails = fmt.Sprintf("%s...", errorDetails[:200])
		}
		
		// 屏蔽敏感信息
		errorDetails = sanitizeErrorDetails(errorDetails)
		
		// 返回错误响应
		response := CreateErrorResponse(errorCode, errorMessage, errorDetails)
		c.AbortWithStatusJSON(statusCode, response)
	}
}
