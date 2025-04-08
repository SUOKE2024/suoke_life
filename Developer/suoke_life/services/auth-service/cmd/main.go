package main

import (
	"context"
	"flag"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/suoke-life/auth-service/internal/config"
	"github.com/suoke-life/auth-service/internal/controllers"
	"github.com/suoke-life/auth-service/internal/database"
	"github.com/suoke-life/auth-service/internal/repository"
	"github.com/suoke-life/auth-service/internal/server"
	"github.com/suoke-life/auth-service/internal/services"
	"github.com/suoke-life/shared/pkg/logger"
)

func main() {
	// 解析命令行参数
	configPath := flag.String("config", "./configs/config.json", "配置文件路径")
	flag.Parse()

	// 初始化日志
	log := logger.NewLogger("auth-service", "info", "json")
	log.Info("认证服务启动中...")

	// 加载配置
	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		log.Warn("加载配置失败，使用默认配置", "error", err)
		cfg = config.DefaultConfig()
		
		// 尝试保存默认配置到指定路径
		if saveErr := config.SaveConfig(cfg, *configPath); saveErr != nil {
			log.Warn("保存默认配置失败", "error", saveErr)
		} else {
			log.Info("默认配置已保存到", "path", *configPath)
		}
	}

	// 初始化数据库连接
	log.Info("初始化数据库连接...")
	dbManager, err := database.NewManager(cfg.Database, log)
	if err != nil {
		log.Error("初始化数据库失败", "error", err)
		os.Exit(1)
	}
	defer dbManager.Close()

	// 运行数据库迁移
	if err := dbManager.RunMigrations(); err != nil {
		log.Error("运行数据库迁移失败", "error", err)
		os.Exit(1)
	}

	// 初始化存储库
	userRepo := repository.NewSQLUserRepository(dbManager.GetDB(), log)

	// 初始化服务
	jwtService := services.NewJWTService(cfg.Server.JWT)
	authService := services.NewAuthService(userRepo, log)

	// 初始化控制器
	authController := controllers.NewAuthController(log, jwtService, authService)

	// 创建服务器
	srv := server.NewServer(cfg.Server, log, authController)

	// 后台启动服务器
	go func() {
		if err := srv.Start(); err != nil {
			log.Error("服务器启动失败", "error", err)
			os.Exit(1)
		}
	}()

	log.Info("服务器已启动", "port", cfg.Server.Port)

	// 等待中断信号优雅关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info("接收到关闭信号，开始优雅关闭...")
	
	// 创建超时上下文
	ctx, cancel := context.WithTimeout(
		context.Background(), 
		time.Duration(cfg.Server.ShutdownTimeout)*time.Second,
	)
	defer cancel()

	// 关闭服务器
	if err := srv.Shutdown(ctx); err != nil {
		log.Error("服务器关闭超时", "error", err)
	}

	log.Info("服务器已关闭")
} 