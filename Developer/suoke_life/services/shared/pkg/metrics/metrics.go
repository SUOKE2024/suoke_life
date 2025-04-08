package metrics

import (
	"time"
	
	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	// RequestCount 统计请求总数
	RequestCount = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "HTTP请求总数",
		},
		[]string{"service", "method", "path", "status"},
	)
	
	// RequestDuration 请求持续时间
	RequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP请求耗时（秒）",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"service", "method", "path"},
	)
	
	// ResponseSize 响应大小
	ResponseSize = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_response_size_bytes",
			Help:    "HTTP响应大小（字节）",
			Buckets: prometheus.ExponentialBuckets(100, 10, 8),
		},
		[]string{"service", "method", "path"},
	)
	
	// ErrorCount 统计错误总数
	ErrorCount = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "app_errors_total",
			Help: "应用错误总数",
		},
		[]string{"service", "type"},
	)
	
	// ActiveRequests 活跃请求数
	ActiveRequests = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "http_active_requests",
			Help: "当前活跃的HTTP请求数",
		},
		[]string{"service"},
	)
)

// MetricsMiddleware 创建指标中间件
func MetricsMiddleware(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.FullPath()
		if path == "" {
			path = "unknown"
		}
		
		// 增加活跃请求计数
		ActiveRequests.WithLabelValues(serviceName).Inc()
		
		// 请求结束时记录指标
		defer func() {
			// 减少活跃请求计数
			ActiveRequests.WithLabelValues(serviceName).Dec()
			
			// 记录请求数
			status := c.Writer.Status()
			RequestCount.WithLabelValues(
				serviceName,
				c.Request.Method,
				path,
				string(status),
			).Inc()
			
			// 记录请求耗时
			duration := time.Since(start).Seconds()
			RequestDuration.WithLabelValues(
				serviceName,
				c.Request.Method,
				path,
			).Observe(duration)
			
			// 记录响应大小
			ResponseSize.WithLabelValues(
				serviceName,
				c.Request.Method,
				path,
			).Observe(float64(c.Writer.Size()))
		}()
		
		c.Next()
	}
}

// RegisterMetricsEndpoint 注册指标端点
func RegisterMetricsEndpoint(r *gin.Engine) {
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))
}

// RecordError 记录一个错误
func RecordError(serviceName, errorType string) {
	ErrorCount.WithLabelValues(serviceName, errorType).Inc()
}

// RecordDBOperation 记录数据库操作耗时
func RecordDBOperation(serviceName, operation string, duration time.Duration) {
	// 如果需要可以添加数据库操作监控指标
}

// ResetMetrics 重置所有指标（主要用于测试）
func ResetMetrics() {
	RequestCount.Reset()
	RequestDuration.Reset()
	ResponseSize.Reset()
	ErrorCount.Reset()
	ActiveRequests.Reset()
}