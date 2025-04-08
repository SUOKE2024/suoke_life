package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"go.uber.org/zap"
	
	"knowledge-graph-service/internal/api/handlers"
	"knowledge-graph-service/internal/api/middleware"
	"knowledge-graph-service/internal/api"
	"knowledge-graph-service/internal/config"
	"knowledge-graph-service/internal/infrastructure/repositories"
	"knowledge-graph-service/internal/usecases"
	"knowledge-graph-service/pkg/logger"
)

func main() {
	// 加载环境变量
	if err := godotenv.Load(); err != nil {
		log.Printf("警告: 未找到.env文件或无法加载: %v", err)
	}

	// 初始化日志
	zapLogger, err := logger.NewLogger("info", "console")
	if err != nil {
		log.Fatalf("初始化日志失败: %v", err)
	}
	defer zapLogger.Sync()

	// 配置
	cfg := config.LoadConfig()

	// 设置Gin模式
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// 初始化Neo4j
	driver, err := neo4j.NewDriverWithContext(
		cfg.Neo4j.URI,
		neo4j.BasicAuth(cfg.Neo4j.Username, cfg.Neo4j.Password, ""),
	)
	if err != nil {
		zapLogger.Fatal("连接Neo4j失败", zap.Error(err))
	}
	defer driver.Close(context.Background())

	// 初始化存储库
	nodeRepo := repositories.NewNeo4jNodeRepository(driver, zapLogger)
	relationshipRepo := repositories.NewNeo4jRelationshipRepository(driver, zapLogger)

	// 初始化用例
	nodeUseCase := usecases.NewNodeUseCase(nodeRepo, zapLogger)
	relationshipUseCase := usecases.NewRelationshipUseCase(relationshipRepo, zapLogger)
	graphUseCase := usecases.NewGraphUseCase(nodeRepo, relationshipRepo, zapLogger)

	// 初始化路由
	router := gin.Default()
	
	// 添加中间件
	router.Use(middleware.Cors())
	router.Use(middleware.Logger())
	router.Use(middleware.ErrorHandler())
	
	// 健康检查端点
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "up",
			"service": "knowledge-graph-service",
			"version": "0.1.0",
			"time": time.Now().Format(time.RFC3339),
		})
	})

	// 设置API路由
	nodeHandler := handlers.NewNodeHandler(nodeUseCase)
	relationshipHandler := handlers.NewRelationshipHandler(relationshipUseCase)
	graphHandler := handlers.NewGraphHandler(graphUseCase)

	// 注册路由
	api.SetupRoutes(router, nodeHandler, relationshipHandler, graphHandler)

	// 启动服务器
	server := &http.Server{
		Addr:    fmt.Sprintf(":%d", cfg.Server.Port),
		Handler: router,
	}

	// 优雅关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		zapLogger.Info("服务器启动", zap.Int("port", cfg.Server.Port))
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			zapLogger.Fatal("启动服务器失败", zap.Error(err))
		}
	}()

	<-quit
	zapLogger.Info("关闭服务器...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		zapLogger.Fatal("服务器关闭失败", zap.Error(err))
	}

	zapLogger.Info("服务器已优雅关闭")
} 