package errors

import (
	"errors"
	"fmt"
	"net/http"
)

// APIError 表示API错误
type APIError struct {
	StatusCode int    `json:"-"`
	Code       string `json:"code"`
	Message    string `json:"message"`
	Detail     string `json:"detail,omitempty"`
	Err        error  `json:"-"`
}

// Error 实现error接口
func (e *APIError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

// Unwrap 返回底层错误
func (e *APIError) Unwrap() error {
	return e.Err
}

// StatusText 返回HTTP状态文本
func (e *APIError) StatusText() string {
	return http.StatusText(e.StatusCode)
}

// 预定义错误码
const (
	ErrCodeBadRequest          = "bad_request"
	ErrCodeUnauthorized        = "unauthorized"
	ErrCodeForbidden           = "forbidden"
	ErrCodeNotFound            = "not_found"
	ErrCodeConflict            = "conflict"
	ErrCodeInternalServerError = "internal_server_error"
	ErrCodeValidationFailed    = "validation_failed"
)

// 创建不同类型的错误
var (
	// NewBadRequest 创建400错误
	NewBadRequest = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusBadRequest,
			Code:       ErrCodeBadRequest,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}

	// NewUnauthorized 创建401错误
	NewUnauthorized = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusUnauthorized,
			Code:       ErrCodeUnauthorized,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}

	// NewForbidden 创建403错误
	NewForbidden = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusForbidden,
			Code:       ErrCodeForbidden,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}

	// NewNotFound 创建404错误
	NewNotFound = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusNotFound,
			Code:       ErrCodeNotFound,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}

	// NewConflict 创建409错误
	NewConflict = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusConflict,
			Code:       ErrCodeConflict,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}

	// NewInternalServerError 创建500错误
	NewInternalServerError = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusInternalServerError,
			Code:       ErrCodeInternalServerError,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}

	// NewValidationFailed 创建422错误
	NewValidationFailed = func(message string, detail string, err error) *APIError {
		return &APIError{
			StatusCode: http.StatusUnprocessableEntity,
			Code:       ErrCodeValidationFailed,
			Message:    message,
			Detail:     detail,
			Err:        err,
		}
	}
)

// Is 检查错误是否匹配
func Is(err, target error) bool {
	return errors.Is(err, target)
}

// As 类型断言
func As(err error, target interface{}) bool {
	return errors.As(err, target)
}

// Wrap 包装错误
func Wrap(err error, message string) error {
	if err == nil {
		return nil
	}
	return fmt.Errorf("%s: %w", message, err)
}

// GetAPIError 将错误转换为APIError
func GetAPIError(err error) *APIError {
	var apiErr *APIError
	if errors.As(err, &apiErr) {
		return apiErr
	}

	// 默认为内部服务器错误
	return NewInternalServerError("内部服务器错误", "", err)
} 