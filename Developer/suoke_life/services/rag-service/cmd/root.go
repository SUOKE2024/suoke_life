package cmd

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	
	"github.com/suoke/suoke_life/services/rag-service/factory"
	"github.com/suoke/suoke_life/services/rag-service/internal/config"
	"github.com/suoke/suoke_life/services/rag-service/internal/server"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

var (
	// 配置文件路径
	cfgFile string
	
	// 服务端口
	port int
	
	// 日志级别
	logLevel string
	
	// 版本信息
	version = "1.0.0"
	
	// 根命令
	rootCmd = &cobra.Command{
		Use:   "rag-service",
		Short: "索克生活RAG服务",
		Long: `索克生活RAG服务 - 支持重排序、混合搜索和多模态检索的RAG系统，
专为中医健康养生领域设计，提供高质量的检索增强生成服务。`,
		Run: func(cmd *cobra.Command, args []string) {
			runServer()
		},
	}
)

// Execute 执行根命令
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)
	
	// 添加命令行参数
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "配置文件路径 (默认为 ./config.yaml)")
	rootCmd.PersistentFlags().IntVar(&port, "port", 0, "服务端口")
	rootCmd.PersistentFlags().StringVar(&logLevel, "log-level", "", "日志级别 (debug, info, warn, error)")
}

// 初始化配置
func initConfig() {
	if cfgFile != "" {
		// 使用命令行指定的配置文件
		viper.SetConfigFile(cfgFile)
	} else {
		// 在当前目录搜索配置文件
		viper.AddConfigPath(".")
		viper.SetConfigName("config")
		viper.SetConfigType("yaml")
	}
	
	viper.AutomaticEnv() // 从环境变量读取配置
	
	// 如果找到配置文件，读取它
	if err := viper.ReadInConfig(); err == nil {
		fmt.Println("使用配置文件:", viper.ConfigFileUsed())
	}
}

// 运行服务器
func runServer() {
	// 初始化日志器
	logger, err := utils.NewStandardLogger(logLevel)
	if err != nil {
		fmt.Printf("初始化日志器失败: %v\n", err)
		os.Exit(1)
	}
	
	logger.Info("启动索克RAG服务", "version", version)
	
	// 加载配置
	var cfg config.Config
	if err := viper.Unmarshal(&cfg); err != nil {
		logger.Error("解析配置失败", "error", err)
		os.Exit(1)
	}
	
	// 如果命令行指定了端口，则覆盖配置文件
	if port > 0 {
		cfg.Server.Port = port
	}
	
	// 创建上下文
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	// 创建组件工厂
	componentFactory := factory.NewComponentFactory(cfg.Components, logger)
	
	// 初始化默认组件
	if err := componentFactory.CreateDefaultComponents(ctx); err != nil {
		logger.Error("初始化默认组件失败", "error", err)
		os.Exit(1)
	}
	
	// 创建并配置服务器
	srv := server.NewServer(&cfg, componentFactory, logger)
	
	// 启动服务器
	if err := srv.Start(); err != nil {
		logger.Error("服务器启动失败", "error", err)
		os.Exit(1)
	}
	
	// 设置优雅关闭
	setupGracefulShutdown(ctx, srv, logger, cancel)
	
	// 阻塞等待关闭
	select {}
}

// 设置优雅关闭
func setupGracefulShutdown(ctx context.Context, srv *server.Server, logger utils.Logger, cancel context.CancelFunc) {
	// 创建信号接收通道
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	
	// 监听关闭信号
	go func() {
		sig := <-sigChan
		logger.Info("接收到关闭信号", "signal", sig)
		
		// 取消上下文
		cancel()
		
		// 设置关闭超时
		shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer shutdownCancel()
		
		// 关闭服务器
		if err := srv.Stop(shutdownCtx); err != nil {
			logger.Error("服务器关闭失败", "error", err)
		}
		
		logger.Info("服务器已关闭")
		os.Exit(0)
	}()
}