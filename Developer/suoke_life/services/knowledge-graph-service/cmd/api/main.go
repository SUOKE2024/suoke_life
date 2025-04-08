package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/mux"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"

	"knowledge-graph-service/internal/api"
	"knowledge-graph-service/internal/api/handlers"
	"knowledge-graph-service/internal/config"
	"knowledge-graph-service/internal/infrastructure/database"
	"knowledge-graph-service/internal/infrastructure/repositories"
	"knowledge-graph-service/internal/usecases"
	"knowledge-graph-service/internal/middleware"
	"knowledge-graph-service/internal/logger"
)

func main() {
	// 加载配置
	cfg, err := config.LoadConfig(".")
	if err != nil {
		log.Fatalf("无法加载配置: %v", err)
	}

	// 初始化日志
	logger := logger.NewLogger(cfg.LogLevel)

	// 初始化数据库连接
	db, err := database.NewNeo4jDriver(cfg.DB.URI, cfg.DB.Username, cfg.DB.Password)
	if err != nil {
		logger.Fatal(fmt.Sprintf("Neo4j连接失败: %v", err))
	}
	defer db.Close()

	// 设置存储库
	nodeRepo := repositories.NewNeo4jNodeRepository(db, logger)
	relationshipRepo := repositories.NewNeo4jRelationshipRepository(db, logger)

	// 设置用例
	nodeUseCase := usecases.NewNodeUseCase(nodeRepo, relationshipRepo, logger)
	relationshipUseCase := usecases.NewRelationshipUseCase(relationshipRepo, nodeRepo, logger)
	graphUseCase := usecases.NewGraphUseCase(nodeRepo, relationshipRepo, logger)
	constitutionUseCase := usecases.NewConstitutionUseCase(nodeRepo, relationshipRepo, logger)

	// 设置处理程序
	nodeHandler := handlers.NewNodeHandler(nodeUseCase, logger)
	relationshipHandler := handlers.NewRelationshipHandler(relationshipUseCase, logger)
	graphHandler := handlers.NewGraphHandler(graphUseCase, logger)
	constitutionHandler := handlers.NewConstitutionHandler(constitutionUseCase, logger)

	// 设置Gin路由器
	gin.SetMode(cfg.GinMode)
	router := gin.Default()
	
	// 使用中间件
	router.Use(middleware.CORS())
	router.Use(middleware.RequestLogger(logger))
	
	// 设置路由
	api.SetupRoutes(router, nodeHandler, relationshipHandler, graphHandler, constitutionHandler)

	// 启动服务器
	port := cfg.Port
	if port == "" {
		port = "8080"
	}
	
	logger.Info(fmt.Sprintf("服务器启动在 http://localhost:%s", port))
	
	err = router.Run(":" + port)
	if err != nil {
		logger.Fatal(fmt.Sprintf("服务器启动失败: %v", err))
	}
}

// 初始化日志
func initLogger(level string) *zap.Logger {
	// 解析日志级别
	var zapLevel zapcore.Level
	switch level {
	case "debug":
		zapLevel = zapcore.DebugLevel
	case "info":
		zapLevel = zapcore.InfoLevel
	case "warn":
		zapLevel = zapcore.WarnLevel
	case "error":
		zapLevel = zapcore.ErrorLevel
	default:
		zapLevel = zapcore.InfoLevel
	}

	// 创建日志配置
	config := zap.Config{
		Level:       zap.NewAtomicLevelAt(zapLevel),
		Development: false,
		Sampling: &zap.SamplingConfig{
			Initial:    100,
			Thereafter: 100,
		},
		Encoding: "json",
		EncoderConfig: zapcore.EncoderConfig{
			TimeKey:        "ts",
			LevelKey:       "level",
			NameKey:        "logger",
			CallerKey:      "caller",
			MessageKey:     "msg",
			StacktraceKey:  "stacktrace",
			LineEnding:     zapcore.DefaultLineEnding,
			EncodeLevel:    zapcore.LowercaseLevelEncoder,
			EncodeTime:     zapcore.ISO8601TimeEncoder,
			EncodeDuration: zapcore.SecondsDurationEncoder,
			EncodeCaller:   zapcore.ShortCallerEncoder,
		},
		OutputPaths:      []string{"stdout"},
		ErrorOutputPaths: []string{"stderr"},
	}

	// 创建日志
	logger, err := config.Build()
	if err != nil {
		log.Fatalf("无法初始化日志: %v", err)
	}

	return logger
}

// 日志中间件
func loggingMiddleware(logger *zap.Logger) mux.MiddlewareFunc {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			next.ServeHTTP(w, r)
			logger.Info("HTTP请求",
				zap.String("method", r.Method),
				zap.String("path", r.URL.Path),
				zap.String("remote_addr", r.RemoteAddr),
				zap.String("user_agent", r.UserAgent()),
				zap.Duration("latency", time.Since(start)),
			)
		})
	}
}

// 初始化数据库架构
func initDatabaseSchema(neo4jManager *database.Neo4jManager, logger *zap.Logger) error {
	// 从文件读取架构定义
	schemaBytes, err := os.ReadFile("internal/infrastructure/database/schema.cypher")
	if err != nil {
		return fmt.Errorf("读取架构文件失败: %w", err)
	}

	// 执行架构脚本
	_, err = neo4jManager.ExecuteWrite(string(schemaBytes), nil)
	if err != nil {
		return fmt.Errorf("执行架构脚本失败: %w", err)
	}

	return nil
}