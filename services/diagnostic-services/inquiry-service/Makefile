# Makefile for Inquiry Service - Updated for UV and Python 3.13.3
# 问诊服务构建和开发工具

.PHONY: help install dev-install test lint format clean build run health

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# 项目配置
PROJECT_NAME := inquiry-service
PYTHON_VERSION := 3.13.3
UV_VERSION := 0.5.0

help: ## 显示帮助信息
	@echo "$(BLUE)问诊服务 (Inquiry Service) - 开发工具$(RESET)"
	@echo ""
	@echo "$(GREEN)可用命令:$(RESET)"
	@echo "  install      - Install production dependencies with UV"
	@echo "  dev-install  - Install development dependencies with UV"
	@echo "  test         - Run tests with pytest"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting with ruff and mypy"
	@echo "  format       - Format code with ruff"
	@echo "  pre-commit   - Install and run pre-commit hooks"
	@echo "  clean        - Clean cache and build files"
	@echo "  build        - Build the package with UV"
	@echo "  run          - Run the service"
	@echo "  health       - Check service dependencies"

# Python and UV setup
PYTHON := python3.13
UV := uv
MIRROR_URL := https://pypi.tuna.tsinghua.edu.cn/simple/

# Install dependencies
install: ## 安装生产依赖
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(UV) sync --no-dev --index-url $(MIRROR_URL)

dev-install: ## 安装开发依赖
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(UV) sync --dev --index-url $(MIRROR_URL)
	$(UV) run pre-commit install

# Testing
test: ## 运行测试
	@echo "$(BLUE)Running tests...$(RESET)"
	$(PYTHON) -m pytest test/ -v

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest test/ --cov=inquiry_service --cov-report=html --cov-report=term --cov-fail-under=80

test-integration: ## 运行集成测试
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(PYTHON) test/integration_test.py

# Code quality
lint: ## 运行代码检查
	@echo "$(BLUE)Running linting...$(RESET)"
	ruff check .
	mypy .

format: ## 格式化代码
	@echo "$(BLUE)Formatting code...$(RESET)"
	ruff format .
	ruff check . --fix

# Pre-commit hooks
pre-commit-install: ## 安装 pre-commit 钩子
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(UV) run pre-commit install

pre-commit-run: ## 运行 pre-commit 钩子
	$(UV) run pre-commit run --all-files

# Clean up
clean: ## 清理缓存和临时文件
	@echo "$(BLUE)Cleaning up...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ htmlcov/ .coverage.*

# Build
build: ## 构建项目
	@echo "$(BLUE)Building project...$(RESET)"
	$(UV) build

# Run service
run: ## 运行服务
	@echo "$(BLUE)Starting inquiry service...$(RESET)"
	$(PYTHON) start_server.py

# Development server
dev-run: ## 运行开发模式服务
	@echo "$(BLUE)Starting inquiry service in development mode...$(RESET)"
	ENVIRONMENT=development DEBUG=true $(PYTHON) -m uvicorn inquiry_service.cmd.server:app --reload --host 0.0.0.0 --port 50052

# Docker operations
docker-build: ## 构建 Docker 镜像
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(PROJECT_NAME):latest .

docker-run: ## 运行 Docker 容器
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -p 50052:50052 -p 8080:8080 $(PROJECT_NAME):latest

docker-compose-up: ## 启动 Docker Compose 服务
	@echo "$(BLUE)Starting services with Docker Compose...$(RESET)"
	docker-compose up -d

docker-compose-down: ## 停止 Docker Compose 服务
	@echo "$(BLUE)Stopping services with Docker Compose...$(RESET)"
	docker-compose down

# Health and dependency checks
health: ## 检查服务依赖
	@echo "$(BLUE)Checking service dependencies...$(RESET)"
	@echo "=== Inquiry Service Health Check ==="
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "UV version: $$($(UV) --version)"
	@echo "Project dependencies:"
	@source .venv/bin/activate && python -c "import grpc; print('✅ gRPC available')" 2>/dev/null || echo "❌ gRPC not available"
	@source .venv/bin/activate && python -c "import yaml; print('✅ PyYAML available')" 2>/dev/null || echo "❌ PyYAML not available"
	@source .venv/bin/activate && python -c "from dotenv import load_dotenv; print('✅ python-dotenv available')" 2>/dev/null || echo "❌ python-dotenv not available"
	@source .venv/bin/activate && python -c "import fastapi; print('✅ FastAPI available')" 2>/dev/null || echo "❌ FastAPI not available"
	@source .venv/bin/activate && python -c "import pydantic; print('✅ Pydantic available')" 2>/dev/null || echo "❌ Pydantic not available"
	@source .venv/bin/activate && python -c "import pandas; print('✅ Pandas available')" 2>/dev/null || echo "❌ Pandas not available"
	@source .venv/bin/activate && python -c "import numpy; print('✅ NumPy available')" 2>/dev/null || echo "❌ NumPy not available"
	@echo "Virtual environment: .venv ($(shell ls -la .venv/bin/python 2>/dev/null && echo 'exists' || echo 'missing'))"

# Development workflow
dev-setup: dev-install pre-commit-install
	@echo "$(GREEN)✅ Development environment setup complete$(RESET)"

# CI/CD targets
ci-test: lint test-cov
	@echo "$(GREEN)✅ CI tests passed$(RESET)"

# Production deployment preparation
prod-build: clean install build
	@echo "$(GREEN)✅ Production build complete$(RESET)"

# 数据库
db-upgrade: ## 升级数据库
	@echo "$(BLUE)Upgrading database...$(RESET)"
	$(UV) run alembic upgrade head

db-downgrade: ## 降级数据库
	@echo "$(BLUE)Downgrading database...$(RESET)"
	$(UV) run alembic downgrade -1

db-migration: ## 创建数据库迁移
	@echo "$(BLUE)Creating database migration...$(RESET)"
	@read -p "Migration name: " name; \
	$(UV) run alembic revision --autogenerate -m "$$name"

# 文档
docs: ## 生成文档
	@echo "$(BLUE)Generating documentation...$(RESET)"
	$(UV) run mkdocs build

docs-serve: ## 启动文档服务器
	@echo "$(BLUE)Starting documentation server...$(RESET)"
	$(UV) run mkdocs serve

# 性能测试
benchmark: ## 运行性能测试
	@echo "$(BLUE)Running benchmarks...$(RESET)"
	$(UV) run pytest --benchmark-only

# 完整检查
check-all: lint test-cov
	@echo "$(GREEN)All checks completed!$(RESET)"

# 发布准备
release-check: check-all docs
	@echo "$(GREEN)Release checks completed!$(RESET)"

# 环境信息
info: ## 显示环境信息
	@echo "$(BLUE)Environment Information:$(RESET)"
	@echo "Python version: $(shell python --version)"
	@echo "UV version: $(shell uv --version)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Working directory: $(shell pwd)" 