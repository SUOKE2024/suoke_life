package metrics

import (
	"fmt"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	// 请求计数器
	requestCounter = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "knowledge_base_http_requests_total",
			Help: "总HTTP请求数",
		},
		[]string{"method", "endpoint", "status"},
	)

	// 请求持续时间
	requestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "knowledge_base_http_request_duration_seconds",
			Help:    "HTTP请求持续时间（秒）",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)

	// 数据库操作计数器
	dbOperationsCounter = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "knowledge_base_db_operations_total",
			Help: "数据库操作总数",
		},
		[]string{"operation", "status"},
	)

	// 向量搜索计数器
	vectorSearchCounter = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "knowledge_base_vector_searches_total",
			Help: "向量搜索总数",
		},
		[]string{"status"},
	)

	// 嵌入计数器
	embeddingCounter = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "knowledge_base_embeddings_total",
			Help: "嵌入总数",
		},
	)

	// 活跃连接数
	activeConnections = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "knowledge_base_active_connections",
			Help: "当前活跃连接数",
		},
	)
)

// 初始化函数
func init() {
	// 注册指标
	prometheus.MustRegister(requestCounter)
	prometheus.MustRegister(requestDuration)
	prometheus.MustRegister(dbOperationsCounter)
	prometheus.MustRegister(vectorSearchCounter)
	prometheus.MustRegister(embeddingCounter)
	prometheus.MustRegister(activeConnections)
}

// StartMetricsServer 启动指标服务器
func StartMetricsServer(port int) {
	http.Handle("/metrics", promhttp.Handler())
	go func() {
		fmt.Printf("指标服务器在:%d/metrics启动\n", port)
		if err := http.ListenAndServe(fmt.Sprintf(":%d", port), nil); err != nil {
			fmt.Printf("指标服务器错误: %v\n", err)
		}
	}()
}

// ResponseRecorder 包装http.ResponseWriter以捕获状态码
type ResponseRecorder struct {
	http.ResponseWriter
	StatusCode int
}

// WriteHeader 捕获状态码
func (r *ResponseRecorder) WriteHeader(statusCode int) {
	r.StatusCode = statusCode
	r.ResponseWriter.WriteHeader(statusCode)
}

// RequestMetricsMiddleware HTTP请求指标中间件
func RequestMetricsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		activeConnections.Inc()
		defer activeConnections.Dec()

		start := time.Now()

		// 创建响应记录器以捕获状态码
		recorder := &ResponseRecorder{
			ResponseWriter: w,
			StatusCode:     http.StatusOK,
		}

		// 调用下一个处理器
		next.ServeHTTP(recorder, r)

		// 记录请求持续时间
		duration := time.Since(start).Seconds()
		requestDuration.WithLabelValues(r.Method, r.URL.Path).Observe(duration)

		// 增加请求计数
		requestCounter.WithLabelValues(
			r.Method,
			r.URL.Path,
			fmt.Sprintf("%d", recorder.StatusCode),
		).Inc()
	})
}

// IncrementDBCounter 增加数据库操作计数
func IncrementDBCounter(operation string, success bool) {
	status := "success"
	if !success {
		status = "error"
	}
	dbOperationsCounter.WithLabelValues(operation, status).Inc()
}

// IncrementVectorSearchCounter 增加向量搜索计数
func IncrementVectorSearchCounter(success bool) {
	status := "success"
	if !success {
		status = "error"
	}
	vectorSearchCounter.WithLabelValues(status).Inc()
}

// IncrementEmbeddingCounter 增加嵌入计数
func IncrementEmbeddingCounter() {
	embeddingCounter.Inc()
}
