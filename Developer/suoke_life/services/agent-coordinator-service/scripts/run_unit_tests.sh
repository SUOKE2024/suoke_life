#!/bin/bash

# 单元测试运行脚本
echo "运行所有单元测试..."
go test -v ./internal/handlers/...
