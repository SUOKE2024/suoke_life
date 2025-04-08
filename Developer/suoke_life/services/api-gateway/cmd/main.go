package main

import (
	"context"
	"flag"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/suoke-life/api-gateway/internal/config"
	"github.com/suoke-life/api-gateway/internal/server"
	"github.com/suoke-life/api-gateway/internal/logger"
)

func main() {
	// 解析命令行参数
	var configPath string
	flag.StringVar(&configPath, "config", "config/config.yaml", "配置文件路径")
	flag.Parse()

	// 初始化日志记录器
	logConfig := logger.DefaultConfig()
	log := logger.NewLogger(logConfig)
	log.Info("启动API网关服务...")

	// 加载配置
	cfg, err := config.LoadConfig(configPath)
	if err != nil {
		log.Error("加载配置失败", "error", err)
		// 使用默认配置
		log.Info("使用默认配置")
		cfg = server.DefaultConfig()
	}

	// 创建服务器实例
	srv := server.NewServer(cfg, log)

	// 在后台启动服务器
	go func() {
		log.Info("服务器启动中...", "port", cfg.Server.Port)
		if err := srv.Start(); err != nil {
			log.Error("服务器启动失败", "error", err)
			os.Exit(1)
		}
	}()

	// 等待中断信号优雅关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	log.Info("正在关闭服务器...")
	
	// 创建超时上下文
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(cfg.Server.ShutdownTimeout)*time.Second)
	defer cancel()
	
	// 关闭服务器
	if err := srv.Shutdown(ctx); err != nil {
		log.Error("服务器关闭出错", "error", err)
	}
	
	log.Info("服务器已成功关闭")
} 