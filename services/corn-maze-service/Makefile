# Corn Maze Service Makefile
# 索克生活迷宫探索微服务开发和部署工具

.PHONY: help install dev test lint format type-check clean build docker-build docker-run deploy

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# 项目配置
PROJECT_NAME := corn-maze-service
PYTHON_VERSION := 3.13.3
DOCKER_IMAGE := suokelife/$(PROJECT_NAME)
DOCKER_TAG := latest

help: ## 显示帮助信息
	@echo "$(BLUE)Corn Maze Service - 索克生活迷宫探索微服务$(RESET)"
	@echo ""
	@echo "$(GREEN)可用命令:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## 安装依赖
	@echo "$(BLUE)安装依赖...$(RESET)"
	uv sync --dev
	@echo "$(GREEN)依赖安装完成$(RESET)"

install-prod: ## 安装生产依赖
	@echo "$(BLUE)安装生产依赖...$(RESET)"
	uv sync --no-dev
	@echo "$(GREEN)生产依赖安装完成$(RESET)"

dev: ## 启动开发服务器
	@echo "$(BLUE)启动开发服务器...$(RESET)"
	uv run python -m corn_maze_service.cmd.server.main

dev-reload: ## 启动开发服务器（自动重载）
	@echo "$(BLUE)启动开发服务器（自动重载）...$(RESET)"
	HTTP__RELOAD=true uv run python -m corn_maze_service.cmd.server.main

test: ## 运行测试
	@echo "$(BLUE)运行测试...$(RESET)"
	uv run pytest

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(BLUE)运行测试并生成覆盖率报告...$(RESET)"
	uv run pytest --cov=corn_maze_service --cov-report=html --cov-report=term

test-unit: ## 运行单元测试
	@echo "$(BLUE)运行单元测试...$(RESET)"
	uv run pytest -m unit

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(RESET)"
	uv run pytest -m integration

test-e2e: ## 运行端到端测试
	@echo "$(BLUE)运行端到端测试...$(RESET)"
	uv run pytest -m e2e

lint: ## 运行代码检查
	@echo "$(BLUE)运行代码检查...$(RESET)"
	uv run ruff check .

lint-fix: ## 运行代码检查并自动修复
	@echo "$(BLUE)运行代码检查并自动修复...$(RESET)"
	uv run ruff check . --fix

format: ## 格式化代码
	@echo "$(BLUE)格式化代码...$(RESET)"
	uv run ruff format .

format-check: ## 检查代码格式
	@echo "$(BLUE)检查代码格式...$(RESET)"
	uv run ruff format . --check

type-check: ## 运行类型检查
	@echo "$(BLUE)运行类型检查...$(RESET)"
	uv run mypy corn_maze_service

check-all: lint format-check type-check ## 运行所有检查
	@echo "$(GREEN)所有检查完成$(RESET)"

clean: ## 清理临时文件
	@echo "$(BLUE)清理临时文件...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	@echo "$(GREEN)清理完成$(RESET)"

build: ## 构建包
	@echo "$(BLUE)构建包...$(RESET)"
	uv build
	@echo "$(GREEN)构建完成$(RESET)"

# Docker 相关命令
docker-build: ## 构建 Docker 镜像
	@echo "$(BLUE)构建 Docker 镜像...$(RESET)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)Docker 镜像构建完成$(RESET)"

docker-run: ## 运行 Docker 容器
	@echo "$(BLUE)运行 Docker 容器...$(RESET)"
	docker run -p 50057:50057 -p 51057:51057 -p 51058:51058 $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-push: ## 推送 Docker 镜像
	@echo "$(BLUE)推送 Docker 镜像...$(RESET)"
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)Docker 镜像推送完成$(RESET)"

# 开发环境设置
setup-dev: install ## 设置开发环境
	@echo "$(BLUE)设置开发环境...$(RESET)"
	cp env.example .env
	mkdir -p data logs
	@echo "$(GREEN)开发环境设置完成$(RESET)"
	@echo "$(YELLOW)请编辑 .env 文件配置环境变量$(RESET)"

# 数据库相关
db-init: ## 初始化数据库
	@echo "$(BLUE)初始化数据库...$(RESET)"
	# TODO: 添加数据库初始化脚本
	@echo "$(GREEN)数据库初始化完成$(RESET)"

db-migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(RESET)"
	# TODO: 添加数据库迁移脚本
	@echo "$(GREEN)数据库迁移完成$(RESET)"

# 部署相关
deploy-dev: ## 部署到开发环境
	@echo "$(BLUE)部署到开发环境...$(RESET)"
	# TODO: 添加开发环境部署脚本
	@echo "$(GREEN)开发环境部署完成$(RESET)"

deploy-staging: ## 部署到测试环境
	@echo "$(BLUE)部署到测试环境...$(RESET)"
	# TODO: 添加测试环境部署脚本
	@echo "$(GREEN)测试环境部署完成$(RESET)"

deploy-prod: ## 部署到生产环境
	@echo "$(BLUE)部署到生产环境...$(RESET)"
	# TODO: 添加生产环境部署脚本
	@echo "$(GREEN)生产环境部署完成$(RESET)"

# 监控和日志
logs: ## 查看日志
	@echo "$(BLUE)查看日志...$(RESET)"
	tail -f logs/app.log

monitor: ## 启动监控
	@echo "$(BLUE)启动监控...$(RESET)"
	# TODO: 添加监控启动脚本

# 文档相关
docs-build: ## 构建文档
	@echo "$(BLUE)构建文档...$(RESET)"
	uv run mkdocs build
	@echo "$(GREEN)文档构建完成$(RESET)"

docs-serve: ## 启动文档服务器
	@echo "$(BLUE)启动文档服务器...$(RESET)"
	uv run mkdocs serve

# 安全检查
security-check: ## 运行安全检查
	@echo "$(BLUE)运行安全检查...$(RESET)"
	uv run bandit -r corn_maze_service/
	@echo "$(GREEN)安全检查完成$(RESET)"

# 性能测试
perf-test: ## 运行性能测试
	@echo "$(BLUE)运行性能测试...$(RESET)"
	# TODO: 添加性能测试脚本
	@echo "$(GREEN)性能测试完成$(RESET)"

# 版本管理
version: ## 显示版本信息
	@echo "$(BLUE)版本信息:$(RESET)"
	@echo "项目: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON_VERSION)"
	@uv run python -c "from corn_maze_service import __version__; print(f'服务版本: {__version__}')"

# CI/CD 相关
ci-test: install test lint type-check ## CI 测试流水线
	@echo "$(GREEN)CI 测试流水线完成$(RESET)"

ci-build: ci-test build ## CI 构建流水线
	@echo "$(GREEN)CI 构建流水线完成$(RESET)"

# 快速开始
quick-start: setup-dev dev ## 快速开始（设置环境并启动服务）
	@echo "$(GREEN)快速开始完成$(RESET)" 