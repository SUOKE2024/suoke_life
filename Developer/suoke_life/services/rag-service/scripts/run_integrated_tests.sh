#!/bin/bash

# RAG服务集成测试运行脚本
set -e

echo "开始运行RAG服务集成测试..."

# 创建测试结果目录
mkdir -p ../tests/test_results

# 运行基本功能测试
echo "运行基本功能测试..."
go test -v ../internal/handlers/search_test.go

# 运行性能测试
echo "运行性能测试..."
go test -v ../internal/rag/performance_test.go -bench=.

# 运行多模态功能测试
echo "运行多模态功能测试..."
go run ../tests/test_multimodal.go -image ../tests/samples/tongue.jpg -query "舌红苔白" -verbose

echo "集成测试完成！"
