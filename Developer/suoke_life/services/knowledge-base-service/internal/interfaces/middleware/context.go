package middleware

import (
	"github.com/go-chi/chi/v5/middleware"
	"github.com/google/uuid"
	"knowledge-base-service/pkg/ctxutil"
	"knowledge-base-service/pkg/logger"
	"net/http"
)

// ContextMiddleware 添加请求上下文信息
func ContextMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 从请求头获取requestID或生成新的
		requestID := r.Header.Get("X-Request-ID")
		if requestID == "" {
			requestID = middleware.GetReqID(r.Context())
			if requestID == "" {
				requestID = uuid.New().String()
			}
		}

		// 从请求头获取traceID
		traceID := r.Header.Get("X-Trace-ID")
		if traceID == "" {
			traceID = requestID
		}

		// 创建带有requestID和traceID的上下文
		ctx := ctxutil.WithRequestID(r.Context(), requestID)
		ctx = ctxutil.WithTraceID(ctx, traceID)

		// 从请求中获取认证信息（若有）
		if userIDStr := r.Header.Get("X-User-ID"); userIDStr != "" {
			if userID, err := uuid.Parse(userIDStr); err == nil {
				ctx = ctxutil.WithUserID(ctx, userID)
			}
		}

		// 创建与请求关联的日志记录器
		log := logger.With("request_id", requestID, "trace_id", traceID)
		ctx = logger.WithContext(ctx, log)

		// 设置响应头
		w.Header().Set("X-Request-ID", requestID)
		w.Header().Set("X-Trace-ID", traceID)

		// 使用增强的上下文继续处理请求
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
