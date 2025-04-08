#!/bin/bash
set -e

echo "========== 运行单元测试 ==========="
go test -v ./...

echo "========== 运行基准测试 ==========="
go test -bench=. -benchmem ./...

echo "========== 生成覆盖率报告 ==========="
go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
go tool cover -html=coverage.out -o coverage.html

echo "========== 测试完成 ==========="
