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
	"github.com/suoke-life/agent-coordinator-service/internal/config"
	"github.com/suoke-life/agent-coordinator-service/internal/handlers"
	"github.com/suoke-life/agent-coordinator-service/internal/middleware"
)

// 可以在构建时设置的变量
var (
	version   = "dev"
	buildTime = ""
	gitCommit = ""
)

func main() {
	// 设置版本信息
	if buildTime == "" {
		buildTime = time.Now().Format(time.RFC3339)
	}

	// 解析命令行参数
	configFile := flag.String("config", "config/config.yaml", "配置文件路径")
	showVersion := flag.Bool("version", false, "显示版本信息")
	flag.Parse()

	// 如果请求显示版本信息
	if *showVersion {
		fmt.Printf("Version:\t%s\n", version)
		fmt.Printf("Build time:\t%s\n", buildTime)
		fmt.Printf("Git commit:\t%s\n", gitCommit)
		os.Exit(0)
	}

	// 设置配置文件路径环境变量，用于loadFromFile
	if *configFile != "" {
		os.Setenv("CONFIG_PATH", *configFile)
	}

	// 加载配置
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}

	// 设置 gin 模式
	if cfg.Environment == "development" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// 创建 gin 引擎
	router := gin.New()

	// 添加中间件
	router.Use(middleware.Logger())         // 日志中间件
	router.Use(middleware.ErrorHandler())   // 错误处理中间件
	router.Use(middleware.VersionMiddleware()) // 版本信息中间件
	router.Use(gin.Recovery())              // 恢复中间件

	// 注册路由
	handlers.RegisterRoutes(router)

	// 添加版本信息路由
	router.GET("/version", middleware.VersionHandler)

	// 创建 HTTP 服务器
	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Port),
		Handler:      router,
		ReadTimeout:  60 * time.Second,
		WriteTimeout: 60 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// 在单独的 goroutine 中启动服务器
	go func() {
		log.Printf("服务器启动于 端口 %d", cfg.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("监听失败: %v", err)
		}
	}()

	// 等待中断信号，优雅关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("正在关闭服务器...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("服务器关闭失败: %v", err)
	}

	log.Println("服务器已安全关闭")
} 