package errors

import (
	"fmt"
	"net/http"
)

// AppError 自定义应用错误
type AppError struct {
	Code    int    // HTTP状态码
	Message string // 用户友好消息
	Err     error  // 原始错误
}

func (e *AppError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

// 常用错误类型
func NotFound(resource string, err error) *AppError {
	return &AppError{
		Code:    http.StatusNotFound,
		Message: fmt.Sprintf("%s不存在", resource),
		Err:     err,
	}
}

func BadRequest(message string, err error) *AppError {
	return &AppError{
		Code:    http.StatusBadRequest,
		Message: message,
		Err:     err,
	}
}

func InternalServerError(message string, err error) *AppError {
	return &AppError{
		Code:    http.StatusInternalServerError,
		Message: message,
		Err:     err,
	}
}

func Unauthorized(message string, err error) *AppError {
	return &AppError{
		Code:    http.StatusUnauthorized,
		Message: message,
		Err:     err,
	}
}

func Forbidden(message string, err error) *AppError {
	return &AppError{
		Code:    http.StatusForbidden,
		Message: message,
		Err:     err,
	}
}

func Conflict(message string, err error) *AppError {
	return &AppError{
		Code:    http.StatusConflict,
		Message: message,
		Err:     err,
	}
}
