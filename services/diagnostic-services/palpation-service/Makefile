# 索克生活触诊服务 Makefile
# 遵循 Python 项目最佳实践

.PHONY: help install install-dev install-prod clean lint test test-unit test-integration test-e2e test-all coverage docs docs-serve build run dev check-deps security-check update-deps docker-build docker-run

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# 项目配置
PROJECT_NAME := palpation-service
PYTHON_VERSION := 3.13.3
UV_VERSION := 0.6.16

# 帮助信息
help: ## 显示帮助信息
	@echo "$(BLUE)索克生活触诊服务 - 开发工具$(RESET)"
	@echo ""
	@echo "$(GREEN)可用命令:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 环境检查
check-python: ## 检查 Python 版本
	@echo "$(BLUE)检查 Python 版本...$(RESET)"
	@python --version | grep -q "$(PYTHON_VERSION)" || (echo "$(RED)需要 Python $(PYTHON_VERSION)$(RESET)" && exit 1)
	@echo "$(GREEN)✓ Python 版本正确$(RESET)"

check-uv: ## 检查 UV 版本
	@echo "$(BLUE)检查 UV 版本...$(RESET)"
	@uv --version || (echo "$(RED)请安装 UV$(RESET)" && exit 1)
	@echo "$(GREEN)✓ UV 已安装$(RESET)"

check-deps: check-python check-uv ## 检查所有依赖

# 安装和环境管理
install: check-deps ## 安装基础依赖
	@echo "$(BLUE)安装基础依赖...$(RESET)"
	uv sync --frozen
	@echo "$(GREEN)✓ 基础依赖安装完成$(RESET)"

install-dev: check-deps ## 安装开发依赖
	@echo "$(BLUE)安装开发依赖...$(RESET)"
	uv sync --frozen --extra dev --extra test --extra docs
	@echo "$(GREEN)✓ 开发依赖安装完成$(RESET)"

install-prod: check-deps ## 安装生产依赖
	@echo "$(BLUE)安装生产依赖...$(RESET)"
	uv sync --frozen --extra production --no-dev
	@echo "$(GREEN)✓ 生产依赖安装完成$(RESET)"

update-deps: ## 更新依赖
	@echo "$(BLUE)更新依赖...$(RESET)"
	uv lock --upgrade
	@echo "$(GREEN)✓ 依赖更新完成$(RESET)"

# 清理
clean: ## 清理临时文件
	@echo "$(BLUE)清理临时文件...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	@echo "$(GREEN)✓ 清理完成$(RESET)"

# 代码质量
lint: ## 运行代码检查和格式化
	@echo "$(BLUE)运行代码检查...$(RESET)"
	uv run ruff check --fix .
	uv run ruff format .
	uv run mypy palpation_service
	@echo "$(GREEN)✓ 代码检查完成$(RESET)"

lint-check: ## 仅检查代码质量，不修复
	@echo "$(BLUE)检查代码质量...$(RESET)"
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy palpation_service
	@echo "$(GREEN)✓ 代码质量检查完成$(RESET)"

security-check: ## 安全检查
	@echo "$(BLUE)运行安全检查...$(RESET)"
	uv run bandit -r palpation_service
	uv run safety check
	@echo "$(GREEN)✓ 安全检查完成$(RESET)"

# 测试
test-unit: ## 运行单元测试
	@echo "$(BLUE)运行单元测试...$(RESET)"
	uv run pytest -m unit -v
	@echo "$(GREEN)✓ 单元测试完成$(RESET)"

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(RESET)"
	uv run pytest -m integration -v
	@echo "$(GREEN)✓ 集成测试完成$(RESET)"

test-e2e: ## 运行端到端测试
	@echo "$(BLUE)运行端到端测试...$(RESET)"
	uv run pytest -m e2e -v
	@echo "$(GREEN)✓ 端到端测试完成$(RESET)"

test: ## 运行所有测试
	@echo "$(BLUE)运行所有测试...$(RESET)"
	uv run pytest -v
	@echo "$(GREEN)✓ 所有测试完成$(RESET)"

test-fast: ## 运行快速测试（排除慢速测试）
	@echo "$(BLUE)运行快速测试...$(RESET)"
	uv run pytest -m "not slow" -v
	@echo "$(GREEN)✓ 快速测试完成$(RESET)"

coverage: ## 生成测试覆盖率报告
	@echo "$(BLUE)生成测试覆盖率报告...$(RESET)"
	uv run pytest --cov=palpation_service --cov-report=html --cov-report=term --cov-report=xml
	@echo "$(GREEN)✓ 覆盖率报告生成完成$(RESET)"
	@echo "$(YELLOW)HTML 报告: htmlcov/index.html$(RESET)"

# 文档
docs: ## 生成文档
	@echo "$(BLUE)生成文档...$(RESET)"
	uv run mkdocs build
	@echo "$(GREEN)✓ 文档生成完成$(RESET)"

docs-serve: ## 启动文档服务器
	@echo "$(BLUE)启动文档服务器...$(RESET)"
	uv run mkdocs serve --dev-addr 0.0.0.0:8001

docs-clean: ## 清理文档
	@echo "$(BLUE)清理文档...$(RESET)"
	rm -rf site/
	@echo "$(GREEN)✓ 文档清理完成$(RESET)"

# 构建和打包
build: clean ## 构建项目
	@echo "$(BLUE)构建项目...$(RESET)"
	uv build
	@echo "$(GREEN)✓ 项目构建完成$(RESET)"

# 运行服务
run: ## 运行服务（生产模式）
	@echo "$(BLUE)启动触诊服务...$(RESET)"
	uv run palpation-service serve

dev: ## 运行服务（开发模式）
	@echo "$(BLUE)启动触诊服务（开发模式）...$(RESET)"
	uv run palpation-service serve --reload --log-level debug

# 健康检查
health: ## 检查服务健康状态
	@echo "$(BLUE)检查服务健康状态...$(RESET)"
	uv run palpation-service health

config-check: ## 检查配置文件
	@echo "$(BLUE)检查配置文件...$(RESET)"
	uv run palpation-service check-config

# Docker 相关
docker-build: ## 构建 Docker 镜像
	@echo "$(BLUE)构建 Docker 镜像...$(RESET)"
	docker build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✓ Docker 镜像构建完成$(RESET)"

docker-run: ## 运行 Docker 容器
	@echo "$(BLUE)运行 Docker 容器...$(RESET)"
	docker run -p 8000:8000 $(PROJECT_NAME):latest

docker-compose-up: ## 启动 Docker Compose
	@echo "$(BLUE)启动 Docker Compose...$(RESET)"
	docker-compose up -d

docker-compose-down: ## 停止 Docker Compose
	@echo "$(BLUE)停止 Docker Compose...$(RESET)"
	docker-compose down

# 数据库迁移
migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(RESET)"
	uv run alembic upgrade head
	@echo "$(GREEN)✓ 数据库迁移完成$(RESET)"

migrate-create: ## 创建新的迁移文件
	@echo "$(BLUE)创建新的迁移文件...$(RESET)"
	@read -p "迁移描述: " desc; \
	uv run alembic revision --autogenerate -m "$$desc"

# 性能测试
benchmark: ## 运行性能测试
	@echo "$(BLUE)运行性能测试...$(RESET)"
	uv run pytest -m benchmark --benchmark-only
	@echo "$(GREEN)✓ 性能测试完成$(RESET)"

# 完整的 CI/CD 流程
ci: clean install-dev lint-check security-check test coverage ## 完整的 CI 流程
	@echo "$(GREEN)✓ CI 流程完成$(RESET)"

cd: build ## 完整的 CD 流程
	@echo "$(GREEN)✓ CD 流程完成$(RESET)"

# 开发环境设置
setup-dev: install-dev ## 设置开发环境
	@echo "$(BLUE)设置开发环境...$(RESET)"
	uv run pre-commit install
	@echo "$(GREEN)✓ 开发环境设置完成$(RESET)"

# 版本管理
version: ## 显示版本信息
	@echo "$(BLUE)版本信息:$(RESET)"
	@echo "项目: $(PROJECT_NAME)"
	@echo "Python: $(shell python --version)"
	@echo "UV: $(shell uv --version)"
	@uv run python -c "from palpation_service import __version__; print(f'服务版本: {__version__}')"

# 全面检查
check-all: check-deps lint-check security-check test coverage ## 运行所有检查
	@echo "$(GREEN)✓ 所有检查完成$(RESET)" 