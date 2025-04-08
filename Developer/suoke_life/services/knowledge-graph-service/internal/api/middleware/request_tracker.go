package middleware

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.uber.org/zap"
)

// RequestTrackerConfig 请求跟踪器配置
type RequestTrackerConfig struct {
	SkipPaths []string // 跳过的路径
}

// NewRequestTrackerConfig 创建默认配置
func NewRequestTrackerConfig() RequestTrackerConfig {
	return RequestTrackerConfig{
		SkipPaths: []string{"/health", "/metrics", "/swagger"},
	}
}

// RequestTracker 请求跟踪中间件
// 为每个请求生成唯一的请求ID和跟踪ID，用于日志跟踪和请求跟踪
func RequestTracker(logger *zap.Logger) gin.HandlerFunc {
	config := NewRequestTrackerConfig()
	return func(c *gin.Context) {
		// 检查是否跳过此路径
		if shouldSkipPath(c.Request.URL.Path, config.SkipPaths) {
			c.Next()
			return
		}

		// 获取请求开始时间
		startTime := time.Now()

		// 获取或生成请求ID
		requestID := c.GetHeader(string(RequestIDHeader))
		if requestID == "" {
			requestID = uuid.New().String()
		}

		// 获取或生成跟踪ID
		traceID := c.GetHeader(string(TraceIDHeader))
		if traceID == "" {
			traceID = uuid.New().String()
		}

		// 存储请求ID和跟踪ID到上下文
		c.Set(string(RequestIDKey), requestID)
		c.Set(string(TraceIDKey), traceID)
		c.Set(string(StartTimeKey), startTime)

		// 在响应头中添加请求ID和跟踪ID
		c.Header(string(RequestIDHeader), requestID)
		c.Header(string(TraceIDHeader), traceID)

		// 记录请求开始
		logger.Info("请求开始",
			zap.String("method", c.Request.Method),
			zap.String("path", c.Request.URL.Path),
			zap.String("client_ip", c.ClientIP()),
			zap.String("user_agent", c.Request.UserAgent()),
			zap.String("request_id", requestID),
			zap.String("trace_id", traceID),
		)

		// 处理请求
		c.Next()

		// 计算处理时间
		duration := time.Since(startTime)

		// 根据状态码确定日志级别
		statusCode := c.Writer.Status()
		var logFunc func(msg string, fields ...zap.Field)

		switch {
		case statusCode >= 500:
			logFunc = logger.Error
		case statusCode >= 400:
			logFunc = logger.Warn
		default:
			logFunc = logger.Info
		}

		// 记录请求完成
		logFunc("请求完成",
			zap.String("method", c.Request.Method),
			zap.String("path", c.Request.URL.Path),
			zap.Int("status", statusCode),
			zap.Duration("duration", duration),
			zap.String("request_id", requestID),
			zap.String("trace_id", traceID),
		)
	}
}

// shouldSkipPath 检查是否应该跳过路径
func shouldSkipPath(path string, skipPaths []string) bool {
	for _, skipPath := range skipPaths {
		if path == skipPath || path == skipPath+"/" {
			return true
		}
	}
	return false
}

// WithRequestContext 添加请求信息到上下文
func WithRequestContext(ctx context.Context, requestID, traceID string) context.Context {
	if requestID != "" {
		ctx = context.WithValue(ctx, RequestIDKey, requestID)
	}
	if traceID != "" {
		ctx = context.WithValue(ctx, TraceIDKey, traceID)
	}
	return ctx
}

// GetRequestIDFromContext 从上下文获取请求ID
func GetRequestIDFromContext(ctx context.Context) string {
	if requestID, ok := ctx.Value(RequestIDKey).(string); ok {
		return requestID
	}
	return ""
}

// GetTraceIDFromContext 从上下文获取跟踪ID
func GetTraceIDFromContext(ctx context.Context) string {
	if traceID, ok := ctx.Value(TraceIDKey).(string); ok {
		return traceID
	}
	return ""
}

// GetStartTime 从上下文获取请求开始时间
func GetStartTime(c *gin.Context) time.Time {
	if startTime, exists := c.Get(string(StartTimeKey)); exists {
		if t, ok := startTime.(time.Time); ok {
			return t
		}
	}
	return time.Now() // 返回当前时间作为回退
}

// GetRequestDuration 计算请求持续时间
func GetRequestDuration(c *gin.Context) time.Duration {
	startTime := GetStartTime(c)
	return time.Since(startTime)
}

// FormatRequestLog 格式化包含HTTP状态的请求日志
func FormatRequestLog(c *gin.Context) string {
	return fmt.Sprintf("请求 [%s %s] 已处理，状态码: %d (%s)，处理时间: %v",
		c.Request.Method,
		c.Request.URL.Path,
		c.Writer.Status(),
		http.StatusText(c.Writer.Status()),
		GetRequestDuration(c),
	)
} 