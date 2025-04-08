package ctxutil

import (
	"context"
	"github.com/google/uuid"
)

type contextKey string

const (
	requestIDKey contextKey = "request_id"
	userIDKey    contextKey = "user_id"
	traceIDKey   contextKey = "trace_id"
)

// WithRequestID 添加请求ID到上下文
func WithRequestID(ctx context.Context, requestID string) context.Context {
	return context.WithValue(ctx, requestIDKey, requestID)
}

// RequestIDFromContext 从上下文获取请求ID
func RequestIDFromContext(ctx context.Context) string {
	if id, ok := ctx.Value(requestIDKey).(string); ok {
		return id
	}
	return ""
}

// WithUserID 添加用户ID到上下文
func WithUserID(ctx context.Context, userID uuid.UUID) context.Context {
	return context.WithValue(ctx, userIDKey, userID)
}

// UserIDFromContext 从上下文获取用户ID
func UserIDFromContext(ctx context.Context) (uuid.UUID, bool) {
	if id, ok := ctx.Value(userIDKey).(uuid.UUID); ok {
		return id, true
	}
	return uuid.Nil, false
}

// WithTraceID 添加追踪ID到上下文
func WithTraceID(ctx context.Context, traceID string) context.Context {
	return context.WithValue(ctx, traceIDKey, traceID)
}

// TraceIDFromContext 从上下文获取追踪ID
func TraceIDFromContext(ctx context.Context) string {
	if id, ok := ctx.Value(traceIDKey).(string); ok {
		return id
	}
	return ""
}
