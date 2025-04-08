package response

import (
	"net/http"
	"sync"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/domain/errors"
)

// 重要！这些常量从middleware包中移过来
const (
	RequestIDKey = "X-Request-ID"
	TraceIDKey   = "X-Trace-ID"
)

var (
	// 响应对象池，减少内存分配
	responsePool = sync.Pool{
		New: func() interface{} {
			return &Response{
				Meta: &Meta{},
			}
		},
	}
	
	// 错误信息池
	errorInfoPool = sync.Pool{
		New: func() interface{} {
			return make([]ErrorInfo, 0, 4)
		},
	}
)

// GetRequestID 获取请求ID的辅助函数
func GetRequestID(c *gin.Context) string {
	id, exists := c.Get(RequestIDKey)
	if !exists {
		return ""
	}
	if id, ok := id.(string); ok {
		return id
	}
	return ""
}

// GetTraceID 获取跟踪ID的辅助函数
func GetTraceID(c *gin.Context) string {
	id, exists := c.Get(TraceIDKey)
	if !exists {
		return ""
	}
	if id, ok := id.(string); ok {
		return id
	}
	return ""
}

// OptimizedSuccess 优化版成功响应函数
// 使用对象池减少内存分配
func OptimizedSuccess(c *gin.Context, data interface{}) {
	resp := responsePool.Get().(*Response)
	defer func() {
		// 清理数据并放回池中
		resp.Success = false
		resp.Code = ""
		resp.Message = ""
		resp.Data = nil
		resp.Errors = nil
		resp.Meta = nil
		responsePool.Put(resp)
	}()
	
	// 设置响应数据
	resp.Success = true
	resp.Data = data
	
	c.JSON(http.StatusOK, resp)
}

// OptimizedSuccessWithMeta 优化版带元数据的成功响应
func OptimizedSuccessWithMeta(c *gin.Context, data interface{}, meta *Meta) {
	resp := responsePool.Get().(*Response)
	defer func() {
		resp.Success = false
		resp.Code = ""
		resp.Message = ""
		resp.Data = nil
		resp.Errors = nil
		resp.Meta = nil
		responsePool.Put(resp)
	}()
	
	resp.Success = true
	resp.Data = data
	resp.Meta = meta
	
	c.JSON(http.StatusOK, resp)
}

// OptimizedError 优化的错误处理函数
// 减少内存分配和类型断言开销
func OptimizedError(c *gin.Context, err error, logger *zap.Logger) {
	// 获取请求ID，只在需要时获取
	requestID := GetRequestID(c)
	
	// 从池中获取响应对象
	resp := responsePool.Get().(*Response)
	defer func() {
		resp.Success = false
		resp.Code = ""
		resp.Message = ""
		resp.Data = nil
		resp.Errors = nil
		resp.Meta = nil
		responsePool.Put(resp)
	}()
	
	// 设置基本错误响应
	resp.Success = false
	
	// 预定义状态码变量，避免在多个地方重复设置
	var statusCode int
	
	// 记录错误日志
	logger.Error("请求处理错误",
		zap.String("request_id", requestID),
		zap.String("trace_id", GetTraceID(c)),
		zap.Error(err),
	)
	
	// 使用类型switch一次性判断错误类型
	switch e := err.(type) {
	case *errors.DomainError:
		resp.Code = e.Code
		resp.Message = e.Message
		
		// 根据错误代码设置状态码
		switch e.Code {
		case errors.CodeNotFound:
			statusCode = http.StatusNotFound
		case errors.CodeBadRequest:
			statusCode = http.StatusBadRequest
		case errors.CodeUnauthorized:
			statusCode = http.StatusUnauthorized
		case errors.CodeForbidden:
			statusCode = http.StatusForbidden
		case errors.CodeConflict:
			statusCode = http.StatusConflict
		case errors.CodeValidation:
			statusCode = http.StatusUnprocessableEntity
		default:
			statusCode = http.StatusInternalServerError
		}
		
	case *errors.AppError:
		resp.Code = string(e.Type)
		resp.Message = e.Message
		
		// 确保有请求ID
		if e.RequestID == "" {
			e.WithRequestID(requestID)
		}
		
		statusCode = e.Code
		
	case *errors.ValidationError:
		resp.Code = errors.CodeValidation
		resp.Message = e.Message
		
		// 从池中获取错误信息切片
		errs := errorInfoPool.Get().([]ErrorInfo)[:0]
		for field, msg := range e.Errors {
			errs = append(errs, ErrorInfo{
				Code:    errors.CodeValidation,
				Message: msg,
				Field:   field,
			})
		}
		resp.Errors = errs
		
		statusCode = http.StatusUnprocessableEntity
		
		// 错误处理完后放回池中
		defer func() {
			resp.Errors = nil
			errorInfoPool.Put(errs)
		}()
		
	default:
		// 使用标准的错误类型判断函数
		switch {
		case errors.IsNotFound(err):
			resp.Code = errors.CodeNotFound
			resp.Message = err.Error()
			statusCode = http.StatusNotFound
		case errors.IsBadRequest(err):
			resp.Code = errors.CodeBadRequest
			resp.Message = err.Error()
			statusCode = http.StatusBadRequest
		case errors.IsUnauthorized(err):
			resp.Code = errors.CodeUnauthorized
			resp.Message = err.Error()
			statusCode = http.StatusUnauthorized
		case errors.IsForbidden(err):
			resp.Code = errors.CodeForbidden
			resp.Message = err.Error()
			statusCode = http.StatusForbidden
		case errors.IsConflict(err):
			resp.Code = errors.CodeConflict
			resp.Message = err.Error()
			statusCode = http.StatusConflict
		case errors.IsValidation(err):
			resp.Code = errors.CodeValidation
			resp.Message = err.Error()
			statusCode = http.StatusUnprocessableEntity
		case errors.IsDatabase(err):
			resp.Code = errors.CodeDatabase
			resp.Message = "数据库错误"
			statusCode = http.StatusInternalServerError
		default:
			resp.Code = errors.CodeInternal
			resp.Message = "服务器内部错误"
			statusCode = http.StatusInternalServerError
		}
	}
	
	c.JSON(statusCode, resp)
} 