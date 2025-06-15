# xiaoke-service Makefile
# 标准化的开发工具 Makefile

.PHONY: help install dev test lint format clean build docker-build docker-run

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# 项目信息
PROJECT_NAME := xiaoke-service
PYTHON_VERSION := 3.13
SRC_DIR := xiaoke_service

# UV命令
UV := uv
PYTHON := $(UV) run python

help: ## 显示帮助信息
	@echo "$(BLUE)$(PROJECT_NAME) 可用命令:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# ============================================================================
# 环境管理
# ============================================================================

install: ## 安装核心依赖
	@echo "$(BLUE)安装核心依赖...$(RESET)"
	$(UV) venv --python $(PYTHON_VERSION)
	$(UV) sync
	@echo "$(GREEN)✓ 核心依赖安装完成$(RESET)"

install-dev: ## 安装开发依赖
	@echo "$(BLUE)安装开发依赖...$(RESET)"
	$(UV) sync --extra dev
	@echo "$(GREEN)✓ 开发依赖安装完成$(RESET)"

clean: ## 清理临时文件和缓存
	@echo "$(BLUE)清理临时文件...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/
	@echo "$(GREEN)✓ 清理完成$(RESET)"

# ============================================================================
# 测试
# ============================================================================

test: ## 运行所有测试
	@echo "$(BLUE)运行所有测试...$(RESET)"
	$(PYTHON) -m pytest tests/ -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ 测试完成$(RESET)"

test-unit: ## 运行单元测试
	@echo "$(BLUE)运行单元测试...$(RESET)"
	$(PYTHON) -m pytest tests/unit/ -v
	@echo "$(GREEN)✓ 单元测试完成$(RESET)"

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(RESET)"
	$(PYTHON) -m pytest tests/integration/ -v
	@echo "$(GREEN)✓ 集成测试完成$(RESET)"

# ============================================================================
# 代码质量
# ============================================================================

lint: ## 运行代码检查
	@echo "$(BLUE)运行代码检查...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIR)/ tests/
	@echo "$(GREEN)✓ 代码检查完成$(RESET)"

format: ## 格式化代码
	@echo "$(BLUE)格式化代码...$(RESET)"
	$(PYTHON) -m ruff format $(SRC_DIR)/ tests/
	$(PYTHON) -m ruff check --fix $(SRC_DIR)/ tests/
	@echo "$(GREEN)✓ 代码格式化完成$(RESET)"

typecheck: ## 运行类型检查
	@echo "$(BLUE)运行类型检查...$(RESET)"
	$(PYTHON) -m mypy $(SRC_DIR)/
	@echo "$(GREEN)✓ 类型检查完成$(RESET)"

# ============================================================================
# 开发服务器
# ============================================================================

dev: ## 启动开发服务器
	@echo "$(BLUE)启动开发服务器...$(RESET)"
	$(PYTHON) -m uvicorn $(SRC_DIR).main:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# 构建和部署
# ============================================================================

build: ## 构建Python包
	@echo "$(BLUE)构建Python包...$(RESET)"
	$(UV) build
	@echo "$(GREEN)✓ 构建完成$(RESET)"

docker-build: ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(RESET)"
	docker build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✓ Docker镜像构建完成$(RESET)"

docker-run: ## 运行Docker容器
	@echo "$(BLUE)运行Docker容器...$(RESET)"
	docker run -d --name $(PROJECT_NAME) -p 8000:8000 $(PROJECT_NAME):latest
	@echo "$(GREEN)✓ Docker容器启动完成$(RESET)"

# ============================================================================
# 快捷命令组合
# ============================================================================

setup: install-dev ## 完整环境搭建
	@echo "$(GREEN)✓ 环境搭建完成$(RESET)"

ci: lint typecheck test ## 持续集成检查
	@echo "$(GREEN)✓ CI检查完成$(RESET)"

pre-commit: format lint typecheck ## 预提交检查
	@echo "$(GREEN)✓ 预提交检查完成$(RESET)"
