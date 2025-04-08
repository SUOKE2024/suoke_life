package middleware

import (
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
)

var (
	// 请求计数器
	requestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_requests_total",
			Help: "API网关处理的请求总数",
		},
		[]string{"method", "path", "status"},
	)

	// 请求延迟直方图
	requestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "api_gateway_request_duration_seconds",
			Help:    "API网关请求处理时间直方图",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)
)

func init() {
	// 注册指标
	prometheus.MustRegister(requestsTotal)
	prometheus.MustRegister(requestDuration)
}

// Metrics 创建API网关的指标监控中间件
func Metrics() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 开始时间
		start := time.Now()
		
		// 处理请求
		c.Next()
		
		// 计算处理时间
		duration := time.Since(start).Seconds()
		
		// 记录指标
		path := c.FullPath()
		if path == "" {
			path = "unknown"
		}
		
		// 更新请求计数
		statusCode := c.Writer.Status()
		requestsTotal.WithLabelValues(c.Request.Method, path, string(rune(statusCode))).Inc()
		
		// 更新请求处理时间
		requestDuration.WithLabelValues(c.Request.Method, path).Observe(duration)
	}
} 