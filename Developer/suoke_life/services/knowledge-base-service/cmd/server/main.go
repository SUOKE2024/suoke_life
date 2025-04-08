package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	chiMiddleware "github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"

	"knowledge-base-service/config"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/infrastructure/database"
	"knowledge-base-service/internal/infrastructure/nlp"
	"knowledge-base-service/internal/infrastructure/repository"
	"knowledge-base-service/internal/infrastructure/vectorstore"
	"knowledge-base-service/internal/interfaces/health"
	"knowledge-base-service/internal/interfaces/metrics"
	appMiddleware "knowledge-base-service/internal/interfaces/middleware"
	"knowledge-base-service/internal/interfaces/rest"
	"knowledge-base-service/internal/mocks"
	"knowledge-base-service/pkg/logger"
)

func main() {
	// 初始化结构化日志
	l := logger.NewStructuredLogger()
	defer l.Sync()

	// 创建root context，用于传递给所有组件和请求（用于后续使用）
	_, cancel := context.WithCancel(context.Background())
	defer cancel()

	// 加载配置
	cfg, err := config.Load()
	if err != nil {
		l.Error("Failed to load configuration", "error", err)
		os.Exit(1)
	}

	// 初始化数据库连接
	db, err := database.NewPostgresDB(cfg.Database.ConnString)
	if err != nil {
		l.Error("Failed to connect to database", "error", err)
		os.Exit(1)
	}

	// 初始化数据库架构
	if err = db.InitSchema(); err != nil {
		l.Error("Failed to initialize database schema", "error", err)
		os.Exit(1)
	}

	// 初始化向量存储
	vectorStore, err := vectorstore.NewMilvusClient(cfg.VectorStore.Host, cfg.VectorStore.Port)
	if err != nil {
		l.Error("Failed to connect to vector store", "error", err)
		os.Exit(1)
	}

	// 设置集合名称
	if cfg.VectorStore.Collection != "" {
		vectorStore.SetCollectionName(cfg.VectorStore.Collection)
	}

	// 创建文本分割器
	textSplitter := nlp.NewChineseTextSplitter(
		cfg.TextSplitter.ChunkSize,
		cfg.TextSplitter.ChunkOverlap,
		true, // 使用智能边界
	)

	// 创建HTTP客户端（用于嵌入服务）
	httpClient := &mocks.MockHttpClient{}

	// 创建嵌入服务
	embeddingService := nlp.NewChineseEmbeddingService(
		nlp.EmbeddingOptions{
			ModelURL:    cfg.Embedding.ModelURL,
			APIToken:    cfg.Embedding.APIToken,
			ContextSize: cfg.Embedding.ContextSize,
			Dimension:   cfg.Embedding.Dimensions,
			BatchSize:   cfg.Embedding.BatchSize,
		},
		httpClient,
	)

	// 创建区块链客户端
	blockchainClient := &mocks.MockBlockchainClient{}

	// 创建文档存储库
	documentRepo := repository.NewPostgresDocumentRepository(db, vectorStore, blockchainClient)

	// 创建分类存储库
	categoryRepo := &mocks.MockCategoryRepository{}

	// 创建文档服务
	documentService := service.NewDocumentService(
		documentRepo,
		categoryRepo,
		textSplitter,
		embeddingService,
	)

	// 创建HTTP处理器
	documentHandler := rest.NewDocumentHandler(documentService)

	// 设置路由
	r := chi.NewRouter()

	// 中间件
	r.Use(chiMiddleware.RequestID)
	r.Use(chiMiddleware.RealIP)
	r.Use(chiMiddleware.Logger)
	r.Use(chiMiddleware.Recoverer)
	r.Use(chiMiddleware.Timeout(60 * time.Second))
	r.Use(appMiddleware.ContextMiddleware)
	r.Use(appMiddleware.ErrorHandler)
	r.Use(metrics.RequestMetricsMiddleware)

	// CORS配置
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   cfg.Security.AllowedOrigins,
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID", "X-Trace-ID"},
		ExposedHeaders:   []string{"Link", "X-Request-ID", "X-Trace-ID"},
		AllowCredentials: true,
		MaxAge:           300,
	}))

	// API路由
	r.Route("/api/v1", func(r chi.Router) {
		// 注册文档处理器路由
		documentHandler.RegisterRoutes(r)
	})

	// 健康检查处理器
	healthHandler := health.NewHealthHandler(db, vectorStore, cfg.Version)
	healthHandler.RegisterRoutes(r)

	// 启动指标服务器（如果启用）
	if cfg.Monitoring.EnableMetrics {
		metrics.StartMetricsServer(cfg.Monitoring.MetricsPort)
	}

	// 启动服务器
	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Server.Port),
		Handler:      r,
		ReadTimeout:  time.Duration(cfg.Server.ReadTimeoutSeconds) * time.Second,
		WriteTimeout: time.Duration(cfg.Server.WriteTimeoutSeconds) * time.Second,
		IdleTimeout:  time.Duration(cfg.Server.IdleTimeoutSeconds) * time.Second,
	}

	// 优雅关闭
	go func() {
		quit := make(chan os.Signal, 1)
		signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
		<-quit

		l.Info("Shutting down server...")

		// 创建关闭上下文
		shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer shutdownCancel()

		if err := server.Shutdown(shutdownCtx); err != nil {
			l.Error("Server shutdown failed", "error", err)
			os.Exit(1)
		}

		// 关闭其他连接
		vectorStore.Close()
		db.Close()

		l.Info("Server gracefully stopped")
		cancel() // 取消根上下文
	}()

	// 启动服务
	l.Info("Server starting", "port", cfg.Server.Port)
	if err := server.ListenAndServe(); err != http.ErrServerClosed {
		l.Error("Server failed to start", "error", err)
		os.Exit(1)
	}
}
