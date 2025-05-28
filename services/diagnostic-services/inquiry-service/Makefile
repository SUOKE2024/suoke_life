# Makefile for Inquiry Service
# 问诊服务构建和开发工具

.PHONY: help install install-dev clean test lint format type-check security-check build run docker-build docker-run docs

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
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 环境管理
install: ## 安装生产依赖
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	uv sync --no-dev

install-dev: ## 安装开发依赖
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	uv sync --dev
	uv run pre-commit install

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

# 代码质量
lint: ## 运行代码检查
	@echo "$(BLUE)Running linting...$(RESET)"
	uv run ruff check .
	uv run ruff format --check .

format: ## 格式化代码
	@echo "$(BLUE)Formatting code...$(RESET)"
	uv run ruff format .
	uv run ruff check --fix .

type-check: ## 运行类型检查
	@echo "$(BLUE)Running type checking...$(RESET)"
	uv run mypy inquiry_service/

security-check: ## 运行安全检查
	@echo "$(BLUE)Running security checks...$(RESET)"
	uv run bandit -r inquiry_service/ -f json -o bandit-report.json || true
	uv run bandit -r inquiry_service/

# 测试
test: ## 运行测试
	@echo "$(BLUE)Running tests...$(RESET)"
	uv run pytest

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	uv run pytest --cov=inquiry_service --cov-report=html --cov-report=term

test-unit: ## 运行单元测试
	@echo "$(BLUE)Running unit tests...$(RESET)"
	uv run pytest -m "unit"

test-integration: ## 运行集成测试
	@echo "$(BLUE)Running integration tests...$(RESET)"
	uv run pytest -m "integration"

test-e2e: ## 运行端到端测试
	@echo "$(BLUE)Running e2e tests...$(RESET)"
	uv run pytest -m "e2e"

# 构建和运行
build: ## 构建项目
	@echo "$(BLUE)Building project...$(RESET)"
	uv build

run: ## 运行服务
	@echo "$(BLUE)Starting inquiry service...$(RESET)"
	uv run python -m inquiry_service.cmd.server

run-dev: ## 运行开发模式服务
	@echo "$(BLUE)Starting inquiry service in development mode...$(RESET)"
	ENVIRONMENT=development DEBUG=true uv run python -m inquiry_service.cmd.server

# Docker
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

# 文档
docs: ## 生成文档
	@echo "$(BLUE)Generating documentation...$(RESET)"
	uv run mkdocs build

docs-serve: ## 启动文档服务器
	@echo "$(BLUE)Starting documentation server...$(RESET)"
	uv run mkdocs serve

# 数据库
db-upgrade: ## 升级数据库
	@echo "$(BLUE)Upgrading database...$(RESET)"
	uv run alembic upgrade head

db-downgrade: ## 降级数据库
	@echo "$(BLUE)Downgrading database...$(RESET)"
	uv run alembic downgrade -1

db-migration: ## 创建数据库迁移
	@echo "$(BLUE)Creating database migration...$(RESET)"
	@read -p "Migration name: " name; \
	uv run alembic revision --autogenerate -m "$$name"

# 开发工具
pre-commit: ## 运行 pre-commit 检查
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	uv run pre-commit run --all-files

update-deps: ## 更新依赖
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	uv lock --upgrade

check-deps: ## 检查依赖安全性
	@echo "$(BLUE)Checking dependencies for security issues...$(RESET)"
	uv run safety check

# 性能测试
benchmark: ## 运行性能测试
	@echo "$(BLUE)Running benchmarks...$(RESET)"
	uv run pytest --benchmark-only

# 完整检查
check-all: lint type-check security-check test ## 运行所有检查
	@echo "$(GREEN)All checks completed!$(RESET)"

# 发布准备
release-check: check-all docs ## 发布前检查
	@echo "$(GREEN)Release checks completed!$(RESET)"

# 环境信息
info: ## 显示环境信息
	@echo "$(BLUE)Environment Information:$(RESET)"
	@echo "Python version: $(shell python --version)"
	@echo "UV version: $(shell uv --version)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Working directory: $(shell pwd)" 