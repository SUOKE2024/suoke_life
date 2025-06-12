# 小艾智能体服务 Makefile
# 提供常用的开发、测试、部署命令

.PHONY: help install install-dev install-ai install-all clean test test-unit test-integration test-e2e lint format typecheck security docs serve dev build docker-build docker-run docker-compose-up docker-compose-down deploy health benchmark profile

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

# 项目信息
PROJECT_NAME := xiaoai-service
VERSION := $(shell grep '^version = ' pyproject.toml | cut -d '"' -f 2)
PYTHON_VERSION := 3.13

# 路径定义
SRC_DIR := xiaoai
TEST_DIR := tests
DOCS_DIR := docs
CONFIG_DIR := config

# UV命令
UV := uv
PYTHON := $(UV) run python
PIP := $(UV) pip

help: ## 显示帮助信息
	@echo "$(CYAN)$(PROJECT_NAME) v$(VERSION)$(RESET)"
	@echo "$(YELLOW)可用命令:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# ============================================================================
# 环境管理
# ============================================================================

install: ## 安装核心依赖
	@echo "$(BLUE)安装核心依赖...$(RESET)"
	$(UV) venv --python $(PYTHON_VERSION)
	$(PIP) install -e .
	@echo "$(GREEN)✓ 核心依赖安装完成$(RESET)"

install-dev: ## 安装开发依赖
	@echo "$(BLUE)安装开发依赖...$(RESET)"
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ 开发依赖安装完成$(RESET)"

install-ai: ## 安装AI/ML依赖
	@echo "$(BLUE)安装AI/ML依赖...$(RESET)"
	$(PIP) install -e ".[ai]"
	@echo "$(GREEN)✓ AI/ML依赖安装完成$(RESET)"

install-all: ## 安装所有依赖
	@echo "$(BLUE)安装所有依赖...$(RESET)"
	$(PIP) install -e ".[all]"
	@echo "$(GREEN)✓ 所有依赖安装完成$(RESET)"

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
	$(PYTHON) -m pytest $(TEST_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ 测试完成$(RESET)"

test-unit: ## 运行单元测试
	@echo "$(BLUE)运行单元测试...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIR)/unit/ -v --cov=$(SRC_DIR) --cov-report=term-missing
	@echo "$(GREEN)✓ 单元测试完成$(RESET)"

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIR)/integration/ -v
	@echo "$(GREEN)✓ 集成测试完成$(RESET)"

test-e2e: ## 运行端到端测试
	@echo "$(BLUE)运行端到端测试...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIR)/e2e/ -v
	@echo "$(GREEN)✓ 端到端测试完成$(RESET)"

test-watch: ## 监控文件变化并自动运行测试
	@echo "$(BLUE)启动测试监控...$(RESET)"
	$(PYTHON) -m pytest-watch $(TEST_DIR)/ --runner "python -m pytest"

benchmark: ## 运行性能基准测试
	@echo "$(BLUE)运行性能基准测试...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIR)/ --benchmark-only --benchmark-sort=mean
	@echo "$(GREEN)✓ 性能测试完成$(RESET)"

# ============================================================================
# 代码质量
# ============================================================================

lint: ## 运行代码检查
	@echo "$(BLUE)运行代码检查...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIR)/ $(TEST_DIR)/
	$(PYTHON) -m ruff format --check $(SRC_DIR)/ $(TEST_DIR)/
	@echo "$(GREEN)✓ 代码检查完成$(RESET)"

format: ## 格式化代码
	@echo "$(BLUE)格式化代码...$(RESET)"
	$(PYTHON) -m ruff format $(SRC_DIR)/ $(TEST_DIR)/
	$(PYTHON) -m ruff check --fix $(SRC_DIR)/ $(TEST_DIR)/
	@echo "$(GREEN)✓ 代码格式化完成$(RESET)"

typecheck: ## 运行类型检查
	@echo "$(BLUE)运行类型检查...$(RESET)"
	$(PYTHON) -m mypy $(SRC_DIR)/
	@echo "$(GREEN)✓ 类型检查完成$(RESET)"

security: ## 运行安全检查
	@echo "$(BLUE)运行安全检查...$(RESET)"
	$(PYTHON) -m bandit -r $(SRC_DIR)/ -f json -o security-report.json
	$(PYTHON) -m safety check --json --output safety-report.json
	@echo "$(GREEN)✓ 安全检查完成$(RESET)"

pre-commit: ## 运行预提交检查
	@echo "$(BLUE)运行预提交检查...$(RESET)"
	$(PYTHON) -m pre_commit run --all-files
	@echo "$(GREEN)✓ 预提交检查完成$(RESET)"

# ============================================================================
# 开发服务器
# ============================================================================

serve: ## 启动生产服务器
	@echo "$(BLUE)启动生产服务器...$(RESET)"
	$(PYTHON) -m uvicorn $(SRC_DIR).api.app:app --host 0.0.0.0 --port 8000

dev: ## 启动开发服务器
	@echo "$(BLUE)启动开发服务器...$(RESET)"
	$(PYTHON) -m uvicorn $(SRC_DIR).api.app:app --reload --host 0.0.0.0 --port 8000

worker: ## 启动后台工作进程
	@echo "$(BLUE)启动后台工作进程...$(RESET)"
	$(PYTHON) -m $(SRC_DIR).cli worker

health: ## 检查服务健康状态
	@echo "$(BLUE)检查服务健康状态...$(RESET)"
	$(PYTHON) -m $(SRC_DIR).cli health

# ============================================================================
# 数据库管理
# ============================================================================

db-init: ## 初始化数据库
	@echo "$(BLUE)初始化数据库...$(RESET)"
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✓ 数据库初始化完成$(RESET)"

db-migrate: ## 创建数据库迁移
	@echo "$(BLUE)创建数据库迁移...$(RESET)"
	$(PYTHON) -m alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✓ 迁移文件创建完成$(RESET)"

db-upgrade: ## 应用数据库迁移
	@echo "$(BLUE)应用数据库迁移...$(RESET)"
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✓ 数据库迁移完成$(RESET)"

db-downgrade: ## 回滚数据库迁移
	@echo "$(BLUE)回滚数据库迁移...$(RESET)"
	$(PYTHON) -m alembic downgrade -1
	@echo "$(GREEN)✓ 数据库回滚完成$(RESET)"

db-reset: ## 重置数据库
	@echo "$(YELLOW)警告: 这将删除所有数据!$(RESET)"
	@read -p "确认继续? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(PYTHON) -m alembic downgrade base
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✓ 数据库重置完成$(RESET)"

# ============================================================================
# 文档
# ============================================================================

docs: ## 生成文档
	@echo "$(BLUE)生成文档...$(RESET)"
	$(PYTHON) -m mkdocs build
	@echo "$(GREEN)✓ 文档生成完成$(RESET)"

docs-serve: ## 启动文档服务器
	@echo "$(BLUE)启动文档服务器...$(RESET)"
	$(PYTHON) -m mkdocs serve --dev-addr 0.0.0.0:8080

docs-deploy: ## 部署文档到GitHub Pages
	@echo "$(BLUE)部署文档...$(RESET)"
	$(PYTHON) -m mkdocs gh-deploy
	@echo "$(GREEN)✓ 文档部署完成$(RESET)"

# ============================================================================
# 构建和打包
# ============================================================================

build: ## 构建Python包
	@echo "$(BLUE)构建Python包...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ 构建完成$(RESET)"

build-wheel: ## 构建wheel包
	@echo "$(BLUE)构建wheel包...$(RESET)"
	$(PYTHON) -m build --wheel
	@echo "$(GREEN)✓ wheel包构建完成$(RESET)"

build-sdist: ## 构建源码包
	@echo "$(BLUE)构建源码包...$(RESET)"
	$(PYTHON) -m build --sdist
	@echo "$(GREEN)✓ 源码包构建完成$(RESET)"

# ============================================================================
# Docker
# ============================================================================

docker-build: ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(RESET)"
	docker build -t $(PROJECT_NAME):$(VERSION) .
	docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest
	@echo "$(GREEN)✓ Docker镜像构建完成$(RESET)"

docker-run: ## 运行Docker容器
	@echo "$(BLUE)运行Docker容器...$(RESET)"
	docker run -d --name $(PROJECT_NAME) -p 8000:8000 $(PROJECT_NAME):latest
	@echo "$(GREEN)✓ Docker容器启动完成$(RESET)"

docker-stop: ## 停止Docker容器
	@echo "$(BLUE)停止Docker容器...$(RESET)"
	docker stop $(PROJECT_NAME) || true
	docker rm $(PROJECT_NAME) || true
	@echo "$(GREEN)✓ Docker容器停止完成$(RESET)"

docker-compose-up: ## 启动Docker Compose服务
	@echo "$(BLUE)启动Docker Compose服务...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✓ Docker Compose服务启动完成$(RESET)"

docker-compose-down: ## 停止Docker Compose服务
	@echo "$(BLUE)停止Docker Compose服务...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✓ Docker Compose服务停止完成$(RESET)"

docker-compose-logs: ## 查看Docker Compose日志
	@echo "$(BLUE)查看Docker Compose日志...$(RESET)"
	docker-compose logs -f

# ============================================================================
# 部署
# ============================================================================

deploy-staging: ## 部署到测试环境
	@echo "$(BLUE)部署到测试环境...$(RESET)"
	./scripts/deploy.sh staging
	@echo "$(GREEN)✓ 测试环境部署完成$(RESET)"

deploy-production: ## 部署到生产环境
	@echo "$(YELLOW)警告: 即将部署到生产环境!$(RESET)"
	@read -p "确认继续? [y/N] " confirm && [ "$$confirm" = "y" ]
	./scripts/deploy.sh production
	@echo "$(GREEN)✓ 生产环境部署完成$(RESET)"

# ============================================================================
# 监控和分析
# ============================================================================

profile: ## 运行性能分析
	@echo "$(BLUE)运行性能分析...$(RESET)"
	$(PYTHON) -m cProfile -o profile.stats -m $(SRC_DIR).main
	$(PYTHON) -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
	@echo "$(GREEN)✓ 性能分析完成$(RESET)"

memory-profile: ## 运行内存分析
	@echo "$(BLUE)运行内存分析...$(RESET)"
	$(PYTHON) -m memory_profiler $(SRC_DIR)/main.py
	@echo "$(GREEN)✓ 内存分析完成$(RESET)"

line-profile: ## 运行行级性能分析
	@echo "$(BLUE)运行行级性能分析...$(RESET)"
	$(PYTHON) -m line_profiler -rmt "$(SRC_DIR)/*.py"
	@echo "$(GREEN)✓ 行级性能分析完成$(RESET)"

# ============================================================================
# 工具命令
# ============================================================================

check-deps: ## 检查依赖更新
	@echo "$(BLUE)检查依赖更新...$(RESET)"
	$(PIP) list --outdated
	@echo "$(GREEN)✓ 依赖检查完成$(RESET)"

update-deps: ## 更新依赖
	@echo "$(BLUE)更新依赖...$(RESET)"
	$(UV) lock --upgrade
	@echo "$(GREEN)✓ 依赖更新完成$(RESET)"

generate-requirements: ## 生成requirements.txt
	@echo "$(BLUE)生成requirements.txt...$(RESET)"
	$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ requirements.txt生成完成$(RESET)"

check-security-deps: ## 检查依赖安全漏洞
	@echo "$(BLUE)检查依赖安全漏洞...$(RESET)"
	$(PYTHON) -m safety check
	@echo "$(GREEN)✓ 安全检查完成$(RESET)"

# ============================================================================
# 版本管理
# ============================================================================

version: ## 显示当前版本
	@echo "$(CYAN)当前版本: $(VERSION)$(RESET)"

bump-patch: ## 升级补丁版本
	@echo "$(BLUE)升级补丁版本...$(RESET)"
	$(PYTHON) -m bumpversion patch
	@echo "$(GREEN)✓ 版本升级完成$(RESET)"

bump-minor: ## 升级次版本
	@echo "$(BLUE)升级次版本...$(RESET)"
	$(PYTHON) -m bumpversion minor
	@echo "$(GREEN)✓ 版本升级完成$(RESET)"

bump-major: ## 升级主版本
	@echo "$(BLUE)升级主版本...$(RESET)"
	$(PYTHON) -m bumpversion major
	@echo "$(GREEN)✓ 版本升级完成$(RESET)"

# ============================================================================
# 快捷命令组合
# ============================================================================

setup: install install-dev db-init ## 完整环境搭建
	@echo "$(GREEN)✓ 环境搭建完成$(RESET)"

ci: lint typecheck test security ## 持续集成检查
	@echo "$(GREEN)✓ CI检查完成$(RESET)"

release: ci build ## 发布准备
	@echo "$(GREEN)✓ 发布准备完成$(RESET)"

dev-setup: install-all db-init docs ## 开发环境完整搭建
	@echo "$(GREEN)✓ 开发环境搭建完成$(RESET)"

# ============================================================================
# 信息显示
# ============================================================================

info: ## 显示项目信息
	@echo "$(CYAN)项目信息:$(RESET)"
	@echo "  名称: $(PROJECT_NAME)"
	@echo "  版本: $(VERSION)"
	@echo "  Python版本: $(PYTHON_VERSION)"
	@echo "  源码目录: $(SRC_DIR)"
	@echo "  测试目录: $(TEST_DIR)"
	@echo "  文档目录: $(DOCS_DIR)"
	@echo "  配置目录: $(CONFIG_DIR)"

status: ## 显示服务状态
	@echo "$(BLUE)检查服务状态...$(RESET)"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "$(RED)服务未运行$(RESET)"

# ============================================================================
# 清理命令
# ============================================================================

clean-all: clean ## 深度清理
	@echo "$(BLUE)深度清理...$(RESET)"
	rm -rf .venv/
	rm -rf node_modules/
	rm -rf models/
	docker system prune -f
	@echo "$(GREEN)✓ 深度清理完成$(RESET)"

# ============================================================================
# 帮助和文档
# ============================================================================

commands: ## 列出所有可用命令
	@echo "$(CYAN)所有可用命令:$(RESET)"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

# 确保某些目标总是执行
.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | cut -d: -f1)