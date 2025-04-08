package server

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/suoke-life/api-gateway/internal/config"
	"github.com/suoke-life/api-gateway/internal/middleware"
	"github.com/suoke-life/api-gateway/internal/proxy"
	"github.com/suoke-life/api-gateway/internal/logger"
)

// Server 表示API网关服务器
type Server struct {
	router      *gin.Engine
	logger      logger.Logger
	config      *config.Config
	server      *http.Server
	proxyManager *proxy.ProxyManager
}

// NewServer 创建新的API网关服务器
func NewServer(cfg *config.Config, log logger.Logger) *Server {
	gin.SetMode(getGinMode())
	router := gin.New()

	// 注册中间件
	router.Use(gin.Recovery())
	router.Use(middleware.Logger(log))
	router.Use(middleware.CORS())
	router.Use(middleware.Metrics())

	// 创建代理管理器
	proxyManager := proxy.NewProxyManager(cfg, log)

	// 创建服务器
	server := &Server{
		router:      router,
		logger:      log,
		config:      cfg,
		proxyManager: proxyManager,
		server: &http.Server{
			Addr:         fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port),
			Handler:      router,
			ReadTimeout:  time.Duration(cfg.Server.ReadTimeout) * time.Second,
			WriteTimeout: time.Duration(cfg.Server.WriteTimeout) * time.Second,
		},
	}

	// 设置路由
	server.setupRoutes()
	return server
}

// Start 启动API网关服务器
func (s *Server) Start() error {
	s.logger.Info("API网关启动", "address", s.server.Addr)
	return s.server.ListenAndServe()
}

// Shutdown 优雅关闭服务器
func (s *Server) Shutdown(ctx context.Context) error {
	s.logger.Info("API网关关闭中...")
	return s.server.Shutdown(ctx)
}

// DefaultConfig 返回默认配置
func DefaultConfig() *config.Config {
	return &config.Config{
		Server: config.ServerConfig{
			Port:            8080,
			Host:            "0.0.0.0",
			ReadTimeout:     15,
			WriteTimeout:    15,
			ShutdownTimeout: 10,
		},
	}
}

// setupRoutes 设置API路由
func (s *Server) setupRoutes() {
	// 健康检查端点
	s.router.GET("/health", s.healthCheck)
	
	// Prometheus指标端点
	if s.config.Metrics.Enabled {
		s.router.GET(s.config.Metrics.Path, gin.WrapH(promhttp.Handler()))
	}
	
	// API路由组
	api := s.router.Group("/api/v1")
	
	// 公开的认证相关端点（不需要JWT验证）
	auth := api.Group("/auth")
	auth.POST("/login", s.proxyToService("auth_service", "/auth/login"))
	auth.POST("/register", s.proxyToService("auth_service", "/auth/register"))
	auth.POST("/refresh", s.proxyToService("auth_service", "/auth/refresh"))
	
	// 需要JWT验证的路由
	protected := api.Group("")
	protected.Use(middleware.JWT())
	
	// 用户服务
	userAPI := protected.Group("/users")
	userAPI.GET("/profile", s.proxyToService("user_service", "/users/profile"))
	userAPI.PUT("/profile", s.proxyToService("user_service", "/users/profile"))
	userAPI.GET("/:id", s.proxyToService("user_service", "/users/:id"))
	
	// RAG服务
	ragAPI := protected.Group("/rag")
	ragAPI.POST("/query", s.proxyToService("rag_service", "/rag/query"))
	ragAPI.GET("/history", s.proxyToService("rag_service", "/rag/history"))
	
	// 知识图谱服务
	kgAPI := protected.Group("/knowledge-graph")
	kgAPI.GET("/query", s.proxyToService("knowledge_graph_service", "/query"))
	kgAPI.POST("/update", s.proxyToService("knowledge_graph_service", "/update"))
	
	// 四诊合参相关服务
	diagnosisAPI := protected.Group("/diagnosis")
	
	// 望诊服务
	diagnosisAPI.POST("/looking", s.proxyToService("looking_diagnosis_service", "/diagnose"))
	
	// 闻诊服务
	diagnosisAPI.POST("/smell", s.proxyToService("smell_diagnosis_service", "/diagnose"))
	
	// 问诊服务
	diagnosisAPI.POST("/inquiry", s.proxyToService("inquiry_diagnosis_service", "/diagnose"))
	
	// 切诊服务
	diagnosisAPI.POST("/touch", s.proxyToService("touch_diagnosis_service", "/diagnose"))
	
	// 四诊合参汇总
	diagnosisAPI.POST("/integrated", s.proxyToService("four_diagnosis_coordinator", "/integrated"))
}

// healthCheck 处理健康检查请求
func (s *Server) healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "ok",
		"time":   time.Now().Format(time.RFC3339),
	})
}

// proxyToService 创建代理到指定服务的处理函数
func (s *Server) proxyToService(serviceName, pathPrefix string) gin.HandlerFunc {
	return s.proxyManager.ProxyToService(serviceName, pathPrefix)
}

// getGinMode 根据环境返回Gin模式
func getGinMode() string {
	env := gin.ReleaseMode // 默认生产模式
	if mode := gin.DebugMode; mode == "debug" {
		env = gin.DebugMode
	}
	return env
} 