package middleware

import (
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// 请求总数
	httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "HTTP请求总数",
		},
		[]string{"method", "path", "status"},
	)

	// 请求持续时间
	httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP请求持续时间（秒）",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)

	// 请求大小
	httpRequestSize = promauto.NewSummaryVec(
		prometheus.SummaryOpts{
			Name:       "http_request_size_bytes",
			Help:       "HTTP请求大小（字节）",
			Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.99: 0.001},
		},
		[]string{"method", "path"},
	)

	// 响应大小
	httpResponseSize = promauto.NewSummaryVec(
		prometheus.SummaryOpts{
			Name:       "http_response_size_bytes",
			Help:       "HTTP响应大小（字节）",
			Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.99: 0.001},
		},
		[]string{"method", "path"},
	)

	// 活跃会话计数
	activeSessions = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "agent_active_sessions",
			Help: "活跃会话数量",
		},
	)

	// 会话操作计数
	sessionOperationsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "session_operations_total",
			Help: "会话操作总数",
		},
		[]string{"operation"},
	)

	// 代理调用计数
	agentCallsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "agent_calls_total",
			Help: "代理调用总数",
		},
		[]string{"agent_type", "function"},
	)

	// 知识图谱查询计数
	knowledgeQueriesTotal = promauto.NewCounter(
		prometheus.CounterOpts{
			Name: "knowledge_queries_total",
			Help: "知识图谱查询总数",
		},
	)

	// 错误计数
	errorsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "errors_total",
			Help: "错误总数",
		},
		[]string{"type"},
	)
)

// MetricsMiddleware 创建指标中间件
func MetricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := normalizePath(c.Request.URL.Path)
		method := c.Request.Method

		// 记录请求大小
		requestSize := 0
		if c.Request.ContentLength > 0 {
			requestSize = int(c.Request.ContentLength)
		}
		httpRequestSize.WithLabelValues(method, path).Observe(float64(requestSize))

		// 处理请求
		c.Next()

		// 获取状态码
		status := strconv.Itoa(c.Writer.Status())

		// 计算请求持续时间
		duration := time.Since(start).Seconds()
		httpRequestDuration.WithLabelValues(method, path).Observe(duration)

		// 递增请求计数
		httpRequestsTotal.WithLabelValues(method, path, status).Inc()

		// 记录响应大小
		responseSize := c.Writer.Size()
		if responseSize < 0 {
			responseSize = 0
		}
		httpResponseSize.WithLabelValues(method, path).Observe(float64(responseSize))

		// 如果有错误，增加错误计数
		if len(c.Errors) > 0 {
			errorsTotal.WithLabelValues("http").Inc()
		}
	}
}

// 标准化路径（避免路径中的ID导致基数爆炸）
func normalizePath(path string) string {
	// 在实际实现中，这里应该使用正则表达式替换路径中的ID为占位符
	// 例如，将 /api/users/123 替换为 /api/users/:id
	// 简化起见，这里仅返回原始路径
	return path
}

// 以下是用于业务逻辑中的指标收集辅助函数

// IncrementSessionOperation 增加会话操作计数
func IncrementSessionOperation(operation string) {
	sessionOperationsTotal.WithLabelValues(operation).Inc()
}

// SetActiveSessions 设置活跃会话数量
func SetActiveSessions(count int) {
	activeSessions.Set(float64(count))
}

// IncrementAgentCall 增加代理调用计数
func IncrementAgentCall(agentType, function string) {
	agentCallsTotal.WithLabelValues(agentType, function).Inc()
}

// IncrementKnowledgeQuery 增加知识图谱查询计数
func IncrementKnowledgeQuery() {
	knowledgeQueriesTotal.Inc()
}

// IncrementError 增加错误计数
func IncrementError(errorType string) {
	errorsTotal.WithLabelValues(errorType).Inc()
}

// 返回所有注册的指标收集器，以便注册到Prometheus
func RegisterMetrics() []prometheus.Collector {
	return []prometheus.Collector{
		httpRequestsTotal,
		httpRequestDuration,
		httpRequestSize,
		httpResponseSize,
		activeSessions,
		sessionOperationsTotal,
		agentCallsTotal,
		knowledgeQueriesTotal,
		errorsTotal,
	}
} 