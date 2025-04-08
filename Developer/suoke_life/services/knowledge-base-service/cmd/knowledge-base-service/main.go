package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

var (
	// 构建变量，通过-ldflags传入
	Version   = "dev"
	Commit    = "none"
	BuildDate = "unknown"
)

func main() {
	log.Printf("索克生活知识库服务 - 版本: %s, 提交: %s, 构建日期: %s", Version, Commit, BuildDate)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "索克生活知识库服务 - 构建测试版本\n")
		fmt.Fprintf(w, "版本: %s\n", Version)
		fmt.Fprintf(w, "提交: %s\n", Commit)
		fmt.Fprintf(w, "构建日期: %s\n", BuildDate)
	})

	log.Printf("服务启动在端口 %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("无法启动服务: %v", err)
	}
}
