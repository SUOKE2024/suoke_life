# integration-service Makefile

.PHONY: help install dev test build run clean

help:  ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装依赖
	uv sync

dev:  ## 启动开发服务器
	uv run python -m integration_service.main

test:  ## 运行测试
	uv run pytest tests/ -v

test-cov:  ## 运行测试并生成覆盖率报告
	uv run pytest tests/ --cov=integration_service --cov-report=html

build:  ## 构建Docker镜像
	docker build -t integration-service:latest .

run:  ## 使用Docker Compose启动服务
	docker-compose up -d

stop:  ## 停止Docker Compose服务
	docker-compose down

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

lint:  ## 代码检查
	uv run ruff check .
	uv run mypy integration_service/

format:  ## 代码格式化
	uv run ruff format .

health:  ## 健康检查
	curl -f http://localhost:8000/health/ || exit 1
