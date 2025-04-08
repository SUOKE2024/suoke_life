package middleware

import (
	"encoding/json"
	"knowledge-base-service/pkg/errors"
	"knowledge-base-service/pkg/logger"
	"net/http"
)

// responseWriter 是一个包装 http.ResponseWriter 的自定义响应写入器
type responseWriter struct {
	http.ResponseWriter
	status  int
	written bool
	err     error
}

// WriteHeader 重写以捕获状态码
func (rw *responseWriter) WriteHeader(status int) {
	rw.status = status
	rw.written = true
	rw.ResponseWriter.WriteHeader(status)
}

// Write 重写以捕获写入状态
func (rw *responseWriter) Write(b []byte) (int, error) {
	if !rw.written {
		rw.WriteHeader(http.StatusOK)
	}
	return rw.ResponseWriter.Write(b)
}

// SetError 设置错误
func (rw *responseWriter) SetError(err error) {
	rw.err = err
}

// ErrorResponse 错误响应
type ErrorResponse struct {
	Error string `json:"error"`
}

// ErrorHandler 错误处理中间件
func ErrorHandler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 创建自定义响应写入器
		rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}

		// 执行下一个处理器
		next.ServeHTTP(rw, r)

		// 如果有错误且未处理
		if rw.err != nil && !rw.written {
			handleError(rw, r, rw.err)
		}
	})
}

// handleError 处理错误
func handleError(w http.ResponseWriter, r *http.Request, err error) {
	log := logger.FromContext(r.Context())

	switch e := err.(type) {
	case *errors.AppError:
		log.Errorw("应用错误",
			"code", e.Code,
			"message", e.Message,
			"error", e.Err,
			"path", r.URL.Path,
			"method", r.Method,
		)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(e.Code)

		response := ErrorResponse{Error: e.Message}
		json.NewEncoder(w).Encode(response)
	default:
		log.Errorw("未知错误",
			"error", err,
			"path", r.URL.Path,
			"method", r.Method,
		)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)

		response := ErrorResponse{Error: "服务器内部错误"}
		json.NewEncoder(w).Encode(response)
	}
}
