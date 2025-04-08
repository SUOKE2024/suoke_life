package main

import (
	"flag"
	"fmt"
)

func main() {
	// 解析命令行参数
	var (
		query = flag.String("query", "", "搜索查询")
		mode  = flag.String("mode", "text", "模式: text, image, audio")
	)
	flag.Parse()

	// 打印测试信息
	fmt.Println("索克生活RAG服务简单测试工具")
	fmt.Println("============================")
	fmt.Printf("查询: %s\n", *query)
	fmt.Printf("模式: %s\n", *mode)
	fmt.Println("测试完成。实际接口尚未实现，这是一个示例程序。")
} 