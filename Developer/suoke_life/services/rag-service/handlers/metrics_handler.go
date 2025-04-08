package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// defaultMetricsHandler 默认指标处理程序实现
type defaultMetricsHandler struct {
	registry      *prometheus.Registry
	requestsTotal *prometheus.CounterVec
	requestDuration *prometheus.HistogramVec
	inProgress *prometheus.GaugeVec
	tokensTotal *prometheus.CounterVec
}

// NewMetricsHandler 创建指标处理程序
func NewMetricsHandler() MetricsHandler {
	registry := prometheus.NewRegistry()
	
	requestsTotal := prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "rag_requests_total",
			Help: "RAG服务请求总数",
		},
		[]string{"method", "endpoint", "status"},
	)
	
	requestDuration := prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "rag_request_duration_seconds",
			Help: "RAG服务请求耗时(秒)",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)
	
	inProgress := prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "rag_requests_in_progress",
			Help: "RAG服务正在处理的请求数",
		},
		[]string{"method", "endpoint"},
	)
	
	tokensTotal := prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "rag_tokens_total",
			Help: "RAG服务处理的token总数",
		},
		[]string{"model", "type"},
	)
	
	registry.MustRegister(requestsTotal, requestDuration, inProgress, tokensTotal)
	
	return &defaultMetricsHandler{
		registry:      registry,
		requestsTotal: requestsTotal,
		requestDuration: requestDuration,
		inProgress: inProgress,
		tokensTotal: tokensTotal,
	}
}

// RegisterRoutes 注册路由
func (h *defaultMetricsHandler) RegisterRoutes(router *gin.Engine) {
	// 创建指标API组
	metricsGroup := router.Group("/metrics")
	{
		// 指标接口
		handler := promhttp.HandlerFor(h.registry, promhttp.HandlerOpts{
			Registry: h.registry,
		})
		metricsGroup.GET("", gin.WrapH(handler))
	}
}

// MetricsHandler 指标处理程序
func (h *defaultMetricsHandler) MetricsHandler(c *gin.Context) {
	handler := promhttp.HandlerFor(h.registry, promhttp.HandlerOpts{})
	handler.ServeHTTP(c.Writer, c.Request)
}

// RecordRequest 记录请求
func (h *defaultMetricsHandler) RecordRequest(method, endpoint, status string) {
	h.requestsTotal.WithLabelValues(method, endpoint, status).Inc()
}

// RecordRequestDuration 记录请求耗时
func (h *defaultMetricsHandler) RecordRequestDuration(method, endpoint string, durationSeconds float64) {
	h.requestDuration.WithLabelValues(method, endpoint).Observe(durationSeconds)
}

// RequestStarted 请求开始
func (h *defaultMetricsHandler) RequestStarted(method, endpoint string) {
	h.inProgress.WithLabelValues(method, endpoint).Inc()
}

// RequestFinished 请求结束
func (h *defaultMetricsHandler) RequestFinished(method, endpoint string) {
	h.inProgress.WithLabelValues(method, endpoint).Dec()
}

// RecordTokens 记录token数量
func (h *defaultMetricsHandler) RecordTokens(model, tokenType string, count int) {
	h.tokensTotal.WithLabelValues(model, tokenType).Add(float64(count))
}

// GetRegistry 获取注册表
func (h *defaultMetricsHandler) GetRegistry() *prometheus.Registry {
	return h.registry
} 