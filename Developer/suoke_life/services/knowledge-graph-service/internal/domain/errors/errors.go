package errors

import (
	"errors"
	"fmt"
	"net/http"
)

// ErrorType 错误类型
type ErrorType string

const (
	// ErrorTypeNotFound 资源未找到
	ErrorTypeNotFound ErrorType = "NOT_FOUND"
	// ErrorTypeBadRequest 错误的请求
	ErrorTypeBadRequest ErrorType = "BAD_REQUEST"
	// ErrorTypeUnauthorized 未授权
	ErrorTypeUnauthorized ErrorType = "UNAUTHORIZED"
	// ErrorTypeForbidden 禁止访问
	ErrorTypeForbidden ErrorType = "FORBIDDEN"
	// ErrorTypeInternal 内部服务器错误
	ErrorTypeInternal ErrorType = "INTERNAL"
	// ErrorTypeConflict 冲突
	ErrorTypeConflict ErrorType = "CONFLICT"
	// ErrorTypeValidation 验证错误
	ErrorTypeValidation ErrorType = "VALIDATION"
	// ErrorTypeDatabase 数据库错误
	ErrorTypeDatabase ErrorType = "DATABASE"
)

// 错误代码常量
const (
	CodeBadRequest   = "BAD_REQUEST"
	CodeUnauthorized = "UNAUTHORIZED"
	CodeForbidden    = "FORBIDDEN"
	CodeNotFound     = "NOT_FOUND"
	CodeConflict     = "CONFLICT"
	CodeInternal     = "INTERNAL"
	CodeValidation   = "VALIDATION"
	CodeDatabase     = "DATABASE"
)

// 简化错误标准化
var (
	ErrNotFound       = errors.New("资源未找到")
	ErrBadRequest     = errors.New("错误的请求")
	ErrUnauthorized   = errors.New("未授权")
	ErrForbidden      = errors.New("禁止访问")
	ErrInternal       = errors.New("内部服务器错误")
	ErrConflict       = errors.New("资源冲突")
	ErrValidation     = errors.New("验证错误")
	ErrDatabase       = errors.New("数据库错误")
)

// AppError 应用错误
type AppError struct {
	Type      ErrorType `json:"type"`
	Message   string    `json:"message"`
	Code      int       `json:"code"`
	Cause     error     `json:"-"`
	RequestID string    `json:"request_id,omitempty"`
}

// DomainError 领域错误类型，用于替代AppError
type DomainError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Cause   error  `json:"-"`
}

// ValidationError 验证错误
type ValidationError struct {
	Message string            `json:"message"`
	Errors  map[string]string `json:"errors"`
	Cause   error             `json:"-"`
}

// Error 实现error接口
func (e *AppError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("%s: %s (原因: %v)", e.Type, e.Message, e.Cause)
	}
	return fmt.Sprintf("%s: %s", e.Type, e.Message)
}

// Error 实现error接口
func (e *DomainError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("%s: %s (原因: %v)", e.Code, e.Message, e.Cause)
	}
	return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

// Error 实现error接口
func (e *ValidationError) Error() string {
	return e.Message
}

// WithRequestID 添加请求ID
func (e *AppError) WithRequestID(requestID string) *AppError {
	e.RequestID = requestID
	return e
}

// Is 实现error.Is接口
func (e *AppError) Is(target error) bool {
	if target == nil {
		return false
	}
	
	targetAppError, ok := target.(*AppError)
	if !ok {
		// 检查是否为标准错误类型
		switch target {
		case ErrNotFound:
			return e.Type == ErrorTypeNotFound
		case ErrBadRequest:
			return e.Type == ErrorTypeBadRequest
		case ErrUnauthorized:
			return e.Type == ErrorTypeUnauthorized
		case ErrForbidden:
			return e.Type == ErrorTypeForbidden
		case ErrInternal:
			return e.Type == ErrorTypeInternal
		case ErrConflict:
			return e.Type == ErrorTypeConflict
		case ErrValidation:
			return e.Type == ErrorTypeValidation
		case ErrDatabase:
			return e.Type == ErrorTypeDatabase
		default:
			return false
		}
	}
	
	return e.Type == targetAppError.Type
}

// Unwrap 实现error.Unwrap接口
func (e *AppError) Unwrap() error {
	return e.Cause
}

// NewNotFoundError 创建未找到资源错误
func NewNotFoundError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeNotFound,
		Message: message,
		Code:    http.StatusNotFound,
		Cause:   cause,
	}
}

// NewBadRequestError 创建错误请求错误
func NewBadRequestError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeBadRequest,
		Message: message,
		Code:    http.StatusBadRequest,
		Cause:   cause,
	}
}

// NewUnauthorizedError 创建未授权错误
func NewUnauthorizedError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeUnauthorized,
		Message: message,
		Code:    http.StatusUnauthorized,
		Cause:   cause,
	}
}

// NewForbiddenError 创建禁止访问错误
func NewForbiddenError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeForbidden,
		Message: message,
		Code:    http.StatusForbidden,
		Cause:   cause,
	}
}

// NewInternalError 创建内部服务器错误
func NewInternalError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeInternal,
		Message: message,
		Code:    http.StatusInternalServerError,
		Cause:   cause,
	}
}

// NewConflictError 创建冲突错误
func NewConflictError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeConflict,
		Message: message,
		Code:    http.StatusConflict,
		Cause:   cause,
	}
}

// NewValidationError 创建验证错误
func NewValidationError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeValidation,
		Message: message,
		Code:    http.StatusUnprocessableEntity,
		Cause:   cause,
	}
}

// NewDatabaseError 创建数据库错误
func NewDatabaseError(message string, cause error) *AppError {
	return &AppError{
		Type:    ErrorTypeDatabase,
		Message: message,
		Code:    http.StatusInternalServerError,
		Cause:   cause,
	}
}

// IsNotFound 判断是否为未找到错误
func IsNotFound(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeNotFound
	}
	return errors.Is(err, ErrNotFound)
}

// IsBadRequest 判断是否为错误请求
func IsBadRequest(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeBadRequest
	}
	return errors.Is(err, ErrBadRequest)
}

// IsUnauthorized 判断是否为未授权错误
func IsUnauthorized(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeUnauthorized
	}
	return errors.Is(err, ErrUnauthorized)
}

// IsForbidden 判断是否为禁止访问错误
func IsForbidden(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeForbidden
	}
	return errors.Is(err, ErrForbidden)
}

// IsInternal 判断是否为内部服务器错误
func IsInternal(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeInternal
	}
	return errors.Is(err, ErrInternal)
}

// IsConflict 判断是否为冲突错误
func IsConflict(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeConflict
	}
	return errors.Is(err, ErrConflict)
}

// IsValidation 判断是否为验证错误
func IsValidation(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeValidation
	}
	return errors.Is(err, ErrValidation)
}

// IsDatabase 判断是否为数据库错误
func IsDatabase(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == ErrorTypeDatabase
	}
	return errors.Is(err, ErrDatabase)
} 