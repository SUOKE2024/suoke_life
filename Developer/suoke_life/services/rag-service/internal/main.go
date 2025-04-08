package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/suoke-life/services/rag-service/internal/config"
	"github.com/suoke-life/services/rag-service/internal/embeddings"
	"github.com/suoke-life/services/rag-service/internal/handlers"
	"github.com/suoke-life/services/rag-service/internal/llm"
	"github.com/suoke-life/services/rag-service/internal/metrics"
	"github.com/suoke-life/services/rag-service/internal/rag"
	"github.com/suoke-life/services/rag-service/internal/vector_store"
)

var (
	configFile string
	port       int
)

func init() {
	flag.StringVar(&configFile, "config", "config.yaml", "配置文件路径")
	flag.IntVar(&port, "port", 8080, "服务端口")
	flag.Parse()
}

func main() {
	// 创建上下文
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// 加载配置
	cfg, err := config.LoadConfig(configFile)
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}

	// 创建指标收集器
	metricsCollector := metrics.NewDefaultMetricsCollector()

	// 创建嵌入模型
	embeddingModel, err := createEmbeddingModel(cfg)
	if err != nil {
		log.Fatalf("创建嵌入模型失败: %v", err)
	}
	defer embeddingModel.Close()

	// 创建向量存储
	vectorStore, err := createVectorStore(cfg)
	if err != nil {
		log.Fatalf("创建向量存储失败: %v", err)
	}
	defer vectorStore.Close()

	// 创建LLM服务
	llmService, err := createLLMService(cfg)
	if err != nil {
		log.Printf("创建LLM服务失败: %v", err)
		log.Println("将使用默认样例回答代替LLM生成")
		// 即使LLM服务创建失败也继续运行，RAG服务会提供默认样例回答
	} else {
		defer llmService.Close()
	}

	// 创建RAG服务
	ragService := rag.NewRAGService(embeddingModel, vectorStore, llmService, metricsCollector)
	if err := ragService.Initialize(ctx); err != nil {
		log.Fatalf("初始化RAG服务失败: %v", err)
	}
	defer ragService.Close()

	// 创建处理器
	ragHandler := handlers.NewRAGHandler(ragService)
	embeddingHandler := handlers.NewEmbeddingHandler(embeddingModel)

	// 创建路由
	r := chi.NewRouter()

	// 中间件
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(60 * time.Second))
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: true,
		MaxAge:           300, // Maximum value not ignored by any of major browsers
	}))

	// API 路由
	r.Route("/api/v1", func(r chi.Router) {
		// RAG API
		r.Route("/rag", func(r chi.Router) {
			r.Post("/query", ragHandler.HandleQuery)
			r.Post("/stream", ragHandler.HandleStreamQuery)
			r.Post("/documents", ragHandler.HandleUploadDocument)
			r.Delete("/documents/{collection}/{id}", ragHandler.HandleDeleteDocument)
			r.Get("/documents/{collection}/{id}", ragHandler.HandleGetDocument)
			
			r.Post("/collections", ragHandler.HandleCreateCollection)
			r.Get("/collections", ragHandler.HandleListCollections)
			r.Get("/collections/{name}", ragHandler.HandleGetCollection)
			r.Delete("/collections/{name}", ragHandler.HandleDeleteCollection)
			
			r.Post("/search/{collection}", ragHandler.HandleSearch)
		})

		// 嵌入 API
		r.Route("/embeddings", func(r chi.Router) {
			r.Post("/", embeddingHandler.HandleCreateEmbedding)
			r.Get("/health", embeddingHandler.HandleHealthCheck)
		})
		
		// 健康检查
		r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		})
	})

	// 静态文件
	workDir, _ := os.Getwd()
	filesDir := filepath.Join(workDir, "static")
	FileServer(r, "/", http.Dir(filesDir))

	// 创建HTTP服务器
	server := &http.Server{
		Addr:    fmt.Sprintf(":%d", port),
		Handler: r,
	}

	// 启动服务器
	go func() {
		log.Printf("RAG服务正在启动，端口: %d", port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("服务器启动失败: %v", err)
		}
	}()

	// 等待退出信号
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig

	// 优雅关闭
	log.Println("正在关闭服务器...")
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("服务器关闭失败: %v", err)
	}
	log.Println("服务器已关闭")
}

// FileServer 创建静态文件服务
func FileServer(r chi.Router, path string, root http.FileSystem) {
	if path != "/" && path[len(path)-1] != '/' {
		r.Get(path, http.RedirectHandler(path+"/", 301).ServeHTTP)
		path += "/"
	}
	path += "*"

	r.Get(path, func(w http.ResponseWriter, r *http.Request) {
		rctx := chi.RouteContext(r.Context())
		pathPrefix := strings.TrimSuffix(rctx.RoutePattern(), "/*")
		fs := http.StripPrefix(pathPrefix, http.FileServer(root))
		fs.ServeHTTP(w, r)
	})
}

// createEmbeddingModel 创建嵌入模型
func createEmbeddingModel(cfg *config.Config) (embeddings.EmbeddingModel, error) {
	// 读取嵌入模型配置
	modelName := cfg.Embedding.Model
	apiKey := cfg.Embedding.APIKey
	endpoint := cfg.Embedding.Endpoint

	// 创建合适的嵌入模型
	if strings.Contains(modelName, "local") {
		// 创建本地嵌入模型
		options := embeddings.LocalEmbeddingOptions{
			ModelPath: cfg.Embedding.ModelPath,
			Dimension: cfg.Embedding.Dimension,
		}
		return embeddings.NewLocalEmbedding(options)
	} else {
		// 创建OpenAI嵌入模型
		options := embeddings.OpenAIEmbeddingOptions{
			ModelName: modelName,
			APIKey:    apiKey,
			Endpoint:  endpoint,
		}
		return embeddings.NewOpenAIEmbedding(options)
	}
}

// createVectorStore 创建向量存储
func createVectorStore(cfg *config.Config) (vector_store.VectorStore, error) {
	// 读取向量存储配置
	storeName := cfg.VectorStore.Type
	connectionString := cfg.VectorStore.ConnectionString
	dimension := cfg.Embedding.Dimension

	// 创建合适的向量存储
	if storeName == "memory" {
		// 创建内存向量存储
		return vector_store.NewMemoryVectorStore(dimension)
	} else {
		// 默认创建PostgreSQL向量存储
		return vector_store.NewPostgresVectorStore(connectionString, dimension)
	}
}

// createLLMService 创建LLM服务
func createLLMService(cfg *config.Config) (llm.LLMService, error) {
	// 读取LLM配置
	modelName := cfg.LLM.Model
	apiKey := cfg.LLM.APIKey
	endpoint := cfg.LLM.Endpoint
	modelPath := cfg.LLM.ModelPath
	
	// 创建LLM选项
	options := llm.LLMOptions{
		ModelName:     modelName,
		APIKey:        apiKey,
		Endpoint:      endpoint,
		ModelPath:     modelPath,
		Temperature:   cfg.LLM.Temperature,
		MaxTokens:     cfg.LLM.MaxTokens,
		TopP:          cfg.LLM.TopP,
	}
	
	// 创建LLM服务
	return llm.CreateLLMService(options)
} 