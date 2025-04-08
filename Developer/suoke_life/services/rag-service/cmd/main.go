package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/suoke/suoke_life/services/rag-service/internal/config"
	"github.com/suoke/suoke_life/services/rag-service/internal/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/internal/handlers"
	ragImpl "github.com/suoke/suoke_life/services/rag-service/internal/rag"
	"github.com/suoke/suoke_life/services/rag-service/vector_store"
)

func main() {
	// 加载配置
	cfg, err := config.LoadConfig(".env")
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}

	// 创建路由器
	r := chi.NewRouter()

	// 应用中间件
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(time.Duration(cfg.ServerConfig.RequestTimeout) * time.Second))
	
	// 配置CORS
	if cfg.ServerConfig.EnableCORS {
		r.Use(cors.Handler(cors.Options{
			AllowedOrigins:   cfg.ServerConfig.AllowOrigins,
			AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
			AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token"},
			ExposedHeaders:   []string{"Link"},
			AllowCredentials: true,
			MaxAge:           300,
		}))
	}

	// 创建嵌入模型
	embeddingOptions := embeddings.EmbeddingOptions{
		Model:         cfg.EmbeddingConfig.ModelName,
		Endpoint:      cfg.EmbeddingConfig.OpenAIEndpoint,
		APIKey:        cfg.EmbeddingConfig.OpenAIKey,
		Dimensions:    cfg.EmbeddingConfig.Dimensions,
		UseLocal:      cfg.EmbeddingConfig.UseLocal,
		LocalModelPath: cfg.EmbeddingConfig.LocalModelPath,
	}
	
	embedder, err := embeddings.CreateEmbedder(embeddingOptions)
	if err != nil {
		log.Fatalf("创建嵌入模型失败: %v", err)
	}
	defer embedder.Close()

	// 创建向量存储
	var store vector_store.VectorStore
	
	switch cfg.VectorConfig.Type {
	case "memory":
		store = vector_store.NewMemoryVectorStore()
	case "milvus":
		// 配置Milvus连接
		store, err = vector_store.NewMilvusVectorStore(
			cfg.VectorConfig.Host,
			cfg.VectorConfig.Port,
			cfg.VectorConfig.Username,
			cfg.VectorConfig.Password,
		)
		if err != nil {
			log.Fatalf("创建Milvus向量存储失败: %v", err)
		}
	default:
		// 默认使用本地向量存储
		store = vector_store.NewLocalVectorStore(cfg.VectorConfig.DataPath)
	}
	
	// 初始化向量存储
	err = store.Initialize(context.Background())
	if err != nil {
		log.Fatalf("初始化向量存储失败: %v", err)
	}
	defer store.Close()

	// 创建指标处理器
	metricsHandler := handlers.NewPrometheusMetricsHandler()
	
	// 创建RAG服务
	ragService := ragImpl.NewDefaultRAGService()
	
	// 设置RAG服务的组件
	ragService.SetComponents(store, embedder, metricsHandler)
	
	// 初始化RAG服务
	err = ragService.Initialize(context.Background())
	if err != nil {
		log.Fatalf("初始化RAG服务失败: %v", err)
	}
	defer ragService.Close()

	// 创建处理器
	ragHandler := handlers.NewRAGHandler(ragService, metricsHandler)
	
	// 注册路由
	ragHandler.Register(r)
	
	// 注册指标路由
	r.Get("/metrics", metricsHandler.GetMetricsHandler())
	
	// 健康检查路由
	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})

	// 获取服务地址和端口
	addr := fmt.Sprintf("%s:%d", cfg.ServerConfig.Host, cfg.ServerConfig.Port)
	
	// 创建服务器
	server := &http.Server{
		Addr:         addr,
		Handler:      r,
		ReadTimeout:  time.Duration(cfg.ServerConfig.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(cfg.ServerConfig.WriteTimeout) * time.Second,
	}

	// 启动服务器
	go func() {
		log.Printf("启动RAG服务，监听地址: %s\n", addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("监听失败: %v", err)
		}
	}()

	// 优雅关闭
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	log.Println("正在关闭服务器...")
	
	// 创建关闭上下文
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("服务器关闭异常: %v", err)
	}
	
	log.Println("服务器已关闭")
}
