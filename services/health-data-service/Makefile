# 索克生活健康数据服务 Makefile

.PHONY: help install dev test lint format run clean

# 默认目标
help:
	@echo "索克生活健康数据服务 - 可用命令:"
	@echo "  install     - 安装项目依赖"
	@echo "  dev         - 安装开发依赖"
	@echo "  run         - 启动开发服务器"
	@echo "  test        - 运行测试"
	@echo "  lint        - 代码检查"
	@echo "  format      - 格式化代码"
	@echo "  clean       - 清理缓存文件"

# 安装依赖
install:
	@echo "安装项目依赖..."
	uv sync

# 安装开发依赖
dev:
	@echo "安装开发依赖..."
	uv sync --group dev

# 运行测试
test:
	@echo "运行测试..."
	uv run pytest tests/ -v

# 代码检查
lint:
	@echo "运行代码检查..."
	uv run ruff check health_data_service/ tests/

# 格式化代码
format:
	@echo "格式化代码..."
	uv run ruff format health_data_service/ tests/

# 启动开发服务器
run:
	@echo "启动开发服务器..."
	uv run python -m health_data_service.api.main

# 清理缓存文件
clean:
	@echo "清理缓存文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete 