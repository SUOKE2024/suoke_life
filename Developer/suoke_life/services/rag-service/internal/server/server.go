package server

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	
	"github.com/suoke/suoke_life/services/rag-service/factory"
	"github.com/suoke/suoke_life/services/rag-service/internal/config"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// Server RAG服务器
type Server struct {
	// 配置
	config *config.Config
	
	// 组件工厂
	factory *factory.ComponentFactory
	
	// 路由器
	router *mux.Router
	
	// HTTP服务器
	httpServer *http.Server
	
	// 日志器
	logger utils.Logger
}

// NewServer 创建服务器
func NewServer(config *config.Config, factory *factory.ComponentFactory, logger utils.Logger) *Server {
	router := mux.NewRouter()
	
	return &Server{
		config:     config,
		factory:    factory,
		router:     router,
		httpServer: &http.Server{
			Addr:    fmt.Sprintf(":%d", config.Server.Port),
			Handler: router,
		},
		logger:     logger,
	}
}

// Start 启动服务器
func (s *Server) Start() error {
	// 注册路由
	s.registerRoutes()
	
	// 启动HTTP服务器
	go func() {
		s.logger.Info("启动HTTP服务器", "port", s.config.Server.Port)
		if err := s.httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			s.logger.Error("HTTP服务器错误", "error", err)
		}
	}()
	
	return nil
}

// Stop 停止服务器
func (s *Server) Stop(ctx context.Context) error {
	s.logger.Info("关闭HTTP服务器")
	return s.httpServer.Shutdown(ctx)
}

// 注册路由
func (s *Server) registerRoutes() {
	// API版本前缀
	apiPrefix := "/api/v1"
	
	// 健康检查
	s.router.HandleFunc("/health", s.handleHealthCheck).Methods("GET")
	
	// API路由组
	api := s.router.PathPrefix(apiPrefix).Subrouter()
	
	// 注册搜索相关路由
	searchRouter := api.PathPrefix("/search").Subrouter()
	searchRouter.HandleFunc("/vector", s.handleVectorSearch).Methods("POST")
	searchRouter.HandleFunc("/keyword", s.handleKeywordSearch).Methods("POST")
	searchRouter.HandleFunc("/hybrid", s.handleHybridSearch).Methods("POST")
	
	// 注册重排序相关路由
	rerankRouter := api.PathPrefix("/rerank").Subrouter()
	rerankRouter.HandleFunc("", s.handleRerank).Methods("POST")
	
	// 注册多模态相关路由
	multimodalRouter := api.PathPrefix("/multimodal").Subrouter()
	multimodalRouter.HandleFunc("/embed", s.handleMultimodalEmbed).Methods("POST")
	
	// 注册中医特色相关路由
	tcmRouter := api.PathPrefix("/tcm").Subrouter()
	tcmRouter.HandleFunc("/terms", s.handleTCMTerms).Methods("GET")
	tcmRouter.HandleFunc("/analyze", s.handleTCMAnalyze).Methods("POST")
	
	// 设置中间件
	s.router.Use(s.loggingMiddleware)
	s.router.Use(s.corsMiddleware)
	
	s.logger.Info("注册API路由", "prefix", apiPrefix)
}

// 健康检查处理器
func (s *Server) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	// 返回服务状态
	utils.WriteJSONResponse(w, http.StatusOK, map[string]interface{}{
		"status":  "ok",
		"version": "1.0.0",
		"time":    time.Now().Format(time.RFC3339),
	})
}

// 向量搜索处理器
func (s *Server) handleVectorSearch(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// 关键词搜索处理器
func (s *Server) handleKeywordSearch(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// 混合搜索处理器
func (s *Server) handleHybridSearch(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// 重排序处理器
func (s *Server) handleRerank(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// 多模态嵌入处理器
func (s *Server) handleMultimodalEmbed(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// TCM术语处理器
func (s *Server) handleTCMTerms(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// TCM分析处理器
func (s *Server) handleTCMAnalyze(w http.ResponseWriter, r *http.Request) {
	// 暂时返回未实现
	utils.WriteJSONResponse(w, http.StatusNotImplemented, map[string]interface{}{
		"error": "接口尚未实现",
	})
}

// 日志中间件
func (s *Server) loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		
		// 包装响应写入器以捕获状态码
		wrapper := utils.NewResponseWriterWrapper(w)
		
		// 调用下一个处理器
		next.ServeHTTP(wrapper, r)
		
		// 记录请求
		s.logger.Info("HTTP请求",
			"method", r.Method,
			"path", r.URL.Path,
			"status", wrapper.StatusCode,
			"duration_ms", time.Since(start).Milliseconds(),
			"user_agent", r.UserAgent(),
		)
	})
}

// CORS中间件
func (s *Server) corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 设置CORS头
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		
		// 预检请求
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		
		// 调用下一个处理器
		next.ServeHTTP(w, r)
	})
}