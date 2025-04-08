package response

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/api/middleware"
	"knowledge-graph-service/internal/domain/errors"
)

// Response 统一的API响应结构
type Response struct {
	Success bool        `json:"success"`           // 是否成功
	Code    string      `json:"code,omitempty"`    // 业务代码
	Message string      `json:"message,omitempty"` // 消息
	Data    interface{} `json:"data,omitempty"`    // 数据
	Errors  []ErrorInfo `json:"errors,omitempty"`  // 错误详情
	Meta    *Meta       `json:"meta,omitempty"`    // 元数据
}

// ErrorInfo 错误信息
type ErrorInfo struct {
	Code    string `json:"code,omitempty"`    // 错误代码
	Message string `json:"message,omitempty"` // 错误消息
	Field   string `json:"field,omitempty"`   // 相关字段（用于字段验证错误）
}

// Meta 元数据信息，用于分页等
type Meta struct {
	Total       int64     `json:"total,omitempty"`        // 总数
	PerPage     int       `json:"per_page,omitempty"`     // 每页数量
	CurrentPage int       `json:"current_page,omitempty"` // 当前页
	LastPage    int       `json:"last_page,omitempty"`    // 最后一页
	From        int       `json:"from,omitempty"`         // 起始记录
	To          int       `json:"to,omitempty"`           // 结束记录
	Timestamp   time.Time `json:"timestamp"`              // 时间戳
}

// NewMeta 创建新的元数据
func NewMeta(total int64, perPage, currentPage int) *Meta {
	lastPage := int(total) / perPage
	if int(total)%perPage > 0 {
		lastPage++
	}
	
	from := (currentPage-1)*perPage + 1
	to := from + perPage - 1
	if to > int(total) {
		to = int(total)
	}
	if total == 0 {
		from = 0
		to = 0
	}
	
	return &Meta{
		Total:       total,
		PerPage:     perPage,
		CurrentPage: currentPage,
		LastPage:    lastPage,
		From:        from,
		To:          to,
		Timestamp:   time.Now(),
	}
}

// Success 返回成功响应
func Success(c *gin.Context, data interface{}) {
	resp := Response{
		Success: true,
		Data:    data,
	}
	c.JSON(http.StatusOK, resp)
}

// SuccessWithMeta 返回带元数据的成功响应
func SuccessWithMeta(c *gin.Context, data interface{}, meta *Meta) {
	resp := Response{
		Success: true,
		Data:    data,
		Meta:    meta,
	}
	c.JSON(http.StatusOK, resp)
}

// Created 返回创建成功响应
func Created(c *gin.Context, data interface{}) {
	resp := Response{
		Success: true,
		Message: "创建成功",
		Data:    data,
	}
	c.JSON(http.StatusCreated, resp)
}

// NoContent 返回无内容响应
func NoContent(c *gin.Context) {
	c.Status(http.StatusNoContent)
}

// BadRequest 返回错误请求响应
func BadRequest(c *gin.Context, message string) {
	resp := Response{
		Success: false,
		Code:    errors.CodeBadRequest,
		Message: message,
	}
	c.JSON(http.StatusBadRequest, resp)
}

// Unauthorized 返回未授权响应
func Unauthorized(c *gin.Context, message string) {
	resp := Response{
		Success: false,
		Code:    errors.CodeUnauthorized,
		Message: message,
	}
	c.JSON(http.StatusUnauthorized, resp)
}

// Forbidden 返回禁止访问响应
func Forbidden(c *gin.Context, message string) {
	resp := Response{
		Success: false,
		Code:    errors.CodeForbidden,
		Message: message,
	}
	c.JSON(http.StatusForbidden, resp)
}

// NotFound 返回资源未找到响应
func NotFound(c *gin.Context, message string) {
	resp := Response{
		Success: false,
		Code:    errors.CodeNotFound,
		Message: message,
	}
	c.JSON(http.StatusNotFound, resp)
}

// Conflict 返回资源冲突响应
func Conflict(c *gin.Context, message string) {
	resp := Response{
		Success: false,
		Code:    errors.CodeConflict,
		Message: message,
	}
	c.JSON(http.StatusConflict, resp)
}

// UnprocessableEntity 返回无法处理的实体响应
func UnprocessableEntity(c *gin.Context, message string, validationErrors map[string]string) {
	errs := make([]ErrorInfo, 0, len(validationErrors))
	for field, msg := range validationErrors {
		errs = append(errs, ErrorInfo{
			Code:    errors.CodeValidation,
			Message: msg,
			Field:   field,
		})
	}
	
	resp := Response{
		Success: false,
		Code:    errors.CodeValidation,
		Message: message,
		Errors:  errs,
	}
	c.JSON(http.StatusUnprocessableEntity, resp)
}

// InternalError 返回内部服务器错误响应
func InternalError(c *gin.Context, message string, logger *zap.Logger) {
	requestID := middleware.GetRequestID(c)
	traceID := middleware.GetTraceID(c)
	
	// 记录错误日志
	logger.Error("内部服务器错误",
		zap.String("request_id", requestID),
		zap.String("trace_id", traceID),
		zap.String("error", message),
	)
	
	resp := Response{
		Success: false,
		Code:    errors.CodeInternal,
		Message: message,
	}
	c.JSON(http.StatusInternalServerError, resp)
}

// Error 处理错误并返回相应的响应
func Error(c *gin.Context, err error, logger *zap.Logger) {
	requestID := middleware.GetRequestID(c)
	traceID := middleware.GetTraceID(c)
	
	// 记录错误日志
	logger.Error("请求处理错误",
		zap.String("request_id", requestID),
		zap.String("trace_id", traceID),
		zap.Error(err),
	)
	
	// 处理领域错误
	var domainError *errors.DomainError
	var appError *errors.AppError
	var validationError *errors.ValidationError
	
	switch {
	case errors.As(err, &domainError):
		resp := Response{
			Success: false,
			Code:    domainError.Code,
			Message: domainError.Message,
		}
		
		switch domainError.Code {
		case errors.CodeNotFound:
			c.JSON(http.StatusNotFound, resp)
		case errors.CodeBadRequest:
			c.JSON(http.StatusBadRequest, resp)
		case errors.CodeUnauthorized:
			c.JSON(http.StatusUnauthorized, resp)
		case errors.CodeForbidden:
			c.JSON(http.StatusForbidden, resp)
		case errors.CodeConflict:
			c.JSON(http.StatusConflict, resp)
		case errors.CodeValidation:
			c.JSON(http.StatusUnprocessableEntity, resp)
		default:
			c.JSON(http.StatusInternalServerError, resp)
		}
		
	case errors.As(err, &appError):
		resp := Response{
			Success: false,
			Code:    string(appError.Type),
			Message: appError.Message,
		}
		
		if appError.RequestID == "" && requestID != "unknown" {
			appError.WithRequestID(requestID)
		}
		
		c.JSON(appError.Code, resp)
		
	case errors.As(err, &validationError):
		errs := make([]ErrorInfo, 0, len(validationError.Errors))
		for field, msg := range validationError.Errors {
			errs = append(errs, ErrorInfo{
				Code:    errors.CodeValidation,
				Message: msg,
				Field:   field,
			})
		}
		
		resp := Response{
			Success: false,
			Code:    errors.CodeValidation,
			Message: validationError.Message,
			Errors:  errs,
		}
		c.JSON(http.StatusUnprocessableEntity, resp)
		
	case errors.IsNotFound(err):
		NotFound(c, err.Error())
	case errors.IsBadRequest(err):
		BadRequest(c, err.Error())
	case errors.IsUnauthorized(err):
		Unauthorized(c, err.Error())
	case errors.IsForbidden(err):
		Forbidden(c, err.Error())
	case errors.IsConflict(err):
		Conflict(c, err.Error())
	case errors.IsValidation(err):
		UnprocessableEntity(c, err.Error(), nil)
	default:
		InternalError(c, "服务器内部错误", logger)
	}
} 