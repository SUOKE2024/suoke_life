# 小艾智能体服务 Makefile
# XiaoAI Agent Service Makefile

.PHONY: help install install-dev install-ai install-all clean test test-unit test-integration test-coverage lint format type-check security-check run run-dev run-worker run-tests build docker-build docker-run init status health

# 默认目标
.DEFAULT_GOAL := help

# Python 和 UV 配置
PYTHON := python3.13
UV := uv
PROJECT_NAME := xiaoai-service

# 颜色定义
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## 显示帮助信息
	@echo "$(GREEN)小艾智能体服务 - 可用命令:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ===== 安装和依赖管理 =====

install: ## 安装核心依赖
	@echo "$(GREEN)安装核心依赖...$(NC)"
	$(UV) sync --no-dev

install-dev: ## 安装开发依赖
	@echo "$(GREEN)安装开发依赖...$(NC)"
	$(UV) sync --extra dev

install-ai: ## 安装AI/ML依赖
	@echo "$(GREEN)安装AI/ML依赖...$(NC)"
	$(UV) sync --extra ai

install-monitoring: ## 安装监控依赖
	@echo "$(GREEN)安装监控依赖...$(NC)"
	$(UV) sync --extra monitoring

install-all: ## 安装所有依赖
	@echo "$(GREEN)安装所有依赖...$(NC)"
	$(UV) sync --extra all

# ===== 清理 =====

clean: ## 清理临时文件和缓存
	@echo "$(GREEN)清理临时文件...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/

# ===== 测试 =====

test: ## 运行所有测试
	@echo "$(GREEN)运行所有测试...$(NC)"
	$(UV) run pytest

test-unit: ## 运行单元测试
	@echo "$(GREEN)运行单元测试...$(NC)"
	$(UV) run pytest tests/ -m "unit"

test-integration: ## 运行集成测试
	@echo "$(GREEN)运行集成测试...$(NC)"
	$(UV) run pytest tests/ -m "integration"

test-coverage: ## 运行测试并生成覆盖率报告
	@echo "$(GREEN)运行测试覆盖率检查...$(NC)"
	$(UV) run pytest --cov=xiaoai --cov-report=html --cov-report=term-missing

test-watch: ## 监视文件变化并自动运行测试
	@echo "$(GREEN)启动测试监视模式...$(NC)"
	$(UV) run pytest-watch

# ===== 代码质量 =====

lint: ## 运行代码检查
	@echo "$(GREEN)运行代码检查...$(NC)"
	$(UV) run ruff check xiaoai/ tests/
	$(UV) run ruff format --check xiaoai/ tests/

format: ## 格式化代码
	@echo "$(GREEN)格式化代码...$(NC)"
	$(UV) run black xiaoai/ tests/
	$(UV) run isort xiaoai/ tests/
	$(UV) run ruff format xiaoai/ tests/

format-check: ## 检查代码格式
	@echo "$(GREEN)检查代码格式...$(NC)"
	$(UV) run black --check xiaoai/ tests/
	$(UV) run isort --check-only xiaoai/ tests/

type-check: ## 运行类型检查
	@echo "$(GREEN)运行类型检查...$(NC)"
	$(UV) run mypy xiaoai/

security-check: ## 运行安全检查
	@echo "$(GREEN)运行安全检查...$(NC)"
	$(UV) run bandit -r xiaoai/
	$(UV) run safety check

quality: lint type-check security-check ## 运行所有代码质量检查

# ===== 运行服务 =====

run: ## 运行服务器
	@echo "$(GREEN)启动小艾智能体服务器...$(NC)"
	$(UV) run xiaoai-server

run-dev: ## 运行开发服务器
	@echo "$(GREEN)启动开发服务器...$(NC)"
	$(UV) run xiaoai-server --reload --workers 1

run-worker: ## 运行工作进程
	@echo "$(GREEN)启动工作进程...$(NC)"
	$(UV) run xiaoai-worker

run-tests: ## 运行测试服务器
	@echo "$(GREEN)启动测试服务器...$(NC)"
	$(UV) run xiaoai-server --host 127.0.0.1 --port 8888 --reload

# ===== 初始化和管理 =====

init: ## 初始化项目
	@echo "$(GREEN)初始化小艾智能体...$(NC)"
	$(UV) run xiaoai init

init-config: ## 初始化配置
	@echo "$(GREEN)初始化配置...$(NC)"
	$(UV) run xiaoai init --target config

init-db: ## 初始化数据库
	@echo "$(GREEN)初始化数据库...$(NC)"
	$(UV) run xiaoai init --target database

status: ## 检查服务状态
	@echo "$(GREEN)检查服务状态...$(NC)"
	$(UV) run xiaoai status

health: ## 健康检查
	@echo "$(GREEN)执行健康检查...$(NC)"
	$(UV) run xiaoai health

# ===== 构建和部署 =====

build: ## 构建项目
	@echo "$(GREEN)构建项目...$(NC)"
	$(UV) build

build-wheel: ## 构建 wheel 包
	@echo "$(GREEN)构建 wheel 包...$(NC)"
	$(UV) build --wheel

build-sdist: ## 构建源码包
	@echo "$(GREEN)构建源码包...$(NC)"
	$(UV) build --sdist

# ===== Docker =====

docker-build: ## 构建 Docker 镜像
	@echo "$(GREEN)构建 Docker 镜像...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

docker-run: ## 运行 Docker 容器
	@echo "$(GREEN)运行 Docker 容器...$(NC)"
	docker run -p 8000:8000 $(PROJECT_NAME):latest

docker-dev: ## 运行开发 Docker 容器
	@echo "$(GREEN)运行开发 Docker 容器...$(NC)"
	docker run -p 8000:8000 -v $(PWD):/app $(PROJECT_NAME):latest

# ===== 文档 =====

docs: ## 生成文档
	@echo "$(GREEN)生成文档...$(NC)"
	$(UV) run mkdocs build

docs-serve: ## 启动文档服务器
	@echo "$(GREEN)启动文档服务器...$(NC)"
	$(UV) run mkdocs serve

# ===== 开发工具 =====

shell: ## 启动 Python shell
	@echo "$(GREEN)启动 Python shell...$(NC)"
	$(UV) run python

notebook: ## 启动 Jupyter notebook
	@echo "$(GREEN)启动 Jupyter notebook...$(NC)"
	$(UV) run jupyter notebook

profile: ## 性能分析
	@echo "$(GREEN)运行性能分析...$(NC)"
	$(UV) run py-spy top --pid $$(pgrep -f "xiaoai-server")

# ===== 数据库管理 =====

db-migrate: ## 运行数据库迁移
	@echo "$(GREEN)运行数据库迁移...$(NC)"
	$(UV) run alembic upgrade head

db-revision: ## 创建新的数据库迁移
	@echo "$(GREEN)创建数据库迁移...$(NC)"
	$(UV) run alembic revision --autogenerate -m "$(msg)"

db-downgrade: ## 回滚数据库迁移
	@echo "$(GREEN)回滚数据库迁移...$(NC)"
	$(UV) run alembic downgrade -1

# ===== 完整工作流 =====

ci: clean install-dev quality test ## CI 流水线
	@echo "$(GREEN)CI 流水线完成!$(NC)"

dev-setup: install-all init ## 开发环境设置
	@echo "$(GREEN)开发环境设置完成!$(NC)"

pre-commit: format lint type-check test-unit ## 提交前检查
	@echo "$(GREEN)提交前检查完成!$(NC)"

release: clean quality test build ## 发布准备
	@echo "$(GREEN)发布准备完成!$(NC)" 