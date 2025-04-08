package middleware

import (
	"fmt"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// OptimizedRequestTracker 优化版请求跟踪中间件
// 相比标准版，减少了内存分配、优化了日志写入
func OptimizedRequestTracker(logger *zap.Logger) gin.HandlerFunc {
	// 预分配日志字段容量，避免每次请求都重新分配内存
	baseFields := make([]zap.Field, 0, 10)
	
	return func(c *gin.Context) {
		// 使用快速路径获取时间
		startTime := time.Now()
		
		// 使用更高效的请求ID处理
		requestID := c.GetHeader(string(RequestIDHeader))
		if requestID == "" {
			requestID = uuid.NewString() // 使用更快的UUID生成
		}
		
		// 跟踪ID同样高效处理
		traceID := c.GetHeader(string(TraceIDHeader))
		if traceID == "" {
			traceID = fmt.Sprintf("trace-%s", uuid.NewString())
		}
		
		// 设置上下文值和响应头
		c.Set(string(RequestIDKey), requestID)
		c.Set(string(StartTimeKey), startTime)
		c.Set(string(TraceIDKey), traceID)
		
		c.Header(string(RequestIDHeader), requestID)
		c.Header(string(TraceIDHeader), traceID)
		
		// 避免字符串拼接及内存分配
		if logger.Core().Enabled(zapcore.InfoLevel) {
			// 重用字段切片，避免每次分配
			fields := append(baseFields[:0],
				zap.String("method", c.Request.Method),
				zap.String("path", c.FullPath()),
				zap.String("client_ip", c.ClientIP()),
				zap.String("request_id", requestID),
				zap.String("trace_id", traceID),
				zap.String("user_agent", c.Request.UserAgent()),
			)
			
			// 添加内容长度，避免条件判断
			cl := c.Request.ContentLength
			if cl > 0 {
				fields = append(fields, zap.Int64("content_length", cl))
			}
			
			logger.Info("请求开始", fields...)
		}
		
		// 处理请求
		c.Next()
		
		// 计算处理时间并设置响应头
		duration := time.Since(startTime)
		c.Header("X-Response-Time", duration.String())
		c.Header("X-Response-Size", strconv.Itoa(c.Writer.Size()))
		
		// 记录完成日志，只在需要时执行
		if logger.Core().Enabled(zapcore.InfoLevel) {
			// 同样重用字段切片
			fields := append(baseFields[:0],
				zap.String("method", c.Request.Method),
				zap.String("path", c.FullPath()),
				zap.Int("status", c.Writer.Status()),
				zap.Duration("duration", duration),
				zap.String("request_id", requestID),
				zap.String("trace_id", traceID),
				zap.Int("response_size", c.Writer.Size()),
			)
			
			// 只在有错误时添加错误数量
			if len(c.Errors) > 0 {
				fields = append(fields, zap.Int("errors", len(c.Errors)))
			}
			
			logger.Info("请求完成", fields...)
			
			// 慢请求告警，只在确实慢的情况下记录
			if duration > time.Second {
				slowFields := []zap.Field{
					zap.String("request_id", requestID),
					zap.String("path", c.FullPath()),
					zap.Duration("duration", duration),
				}
				
				// 添加潜在的性能瓶颈信息
				if c.Writer.Size() > 1024*1024 { // 大于1MB的响应
					slowFields = append(slowFields, zap.String("bottleneck", "large_response"))
				}
				
				if len(c.Errors) > 0 {
					slowFields = append(slowFields, zap.String("bottleneck", "errors"))
				}
				
				logger.Warn("慢请求告警", slowFields...)
			}
		}
	}
}

// GetOptimizedRequestDuration 获取请求持续时间的优化版本
// 避免了不必要的类型断言
func GetOptimizedRequestDuration(c *gin.Context) time.Duration {
	if startTime, exists := c.Get(string(StartTimeKey)); exists {
		if t, ok := startTime.(time.Time); ok {
			return time.Since(t)
		}
	}
	return 0
} 