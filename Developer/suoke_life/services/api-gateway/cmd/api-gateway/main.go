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

	"github.com/suoke-life/api-gateway/internal/configs"
	"github.com/suoke-life/api-gateway/internal/router"
)

func main() {
	// 解析命令行参数
	configPath := flag.String("config", "", "配置文件路径")
	flag.Parse()

	// 加载配置
	config, err := configs.GetConfig(*configPath)
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}

	// 如果环境变量中设置了端口，优先使用环境变量
	portStr := os.Getenv("API_GATEWAY_PORT")
	port := config.Server.Port
	if portStr != "" {
		// 不需要错误处理，如果转换失败使用配置文件中的端口
		fmt.Sscanf(portStr, "%d", &port)
	}

	// 设置路由
	r := router.SetupRouter(config)

	// 创建HTTP服务器
	server := &http.Server{
		Addr:         fmt.Sprintf("%s:%d", config.Server.Host, port),
		Handler:      r,
		ReadTimeout:  time.Duration(config.Server.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(config.Server.WriteTimeout) * time.Second,
	}

	// 在goroutine中启动服务器
	go func() {
		log.Printf("API网关服务启动在 %s:%d\n", config.Server.Host, port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("监听失败: %s\n", err)
		}
	}()

	// 等待中断信号以优雅地关闭服务器
	quit := make(chan os.Signal, 1)
	// kill (无参数) 默认发送 syscall.SIGTERM
	// kill -2 是 syscall.SIGINT
	// kill -9 是 syscall.SIGKILL，但不能被捕获，所以不需要添加
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("正在关闭服务器...")

	// 设置超时上下文进行关闭
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(config.Server.ShutdownTimeout)*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Fatal("服务器被强制关闭:", err)
	}

	log.Println("服务器优雅退出")
}