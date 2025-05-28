# A2A 智能体网络微服务 Makefile
# 使用 UV 包管理器和 Python 3.13.3

.PHONY: help install install-dev test test-cov lint format type-check security clean build run docker-build docker-run deploy

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# 项目配置
PROJECT_NAME := a2a-agent-network
PYTHON_VERSION := 3.13.3
DOCKER_IMAGE := suoke-life/$(PROJECT_NAME)
DOCKER_TAG := latest

help: ## 显示帮助信息
	@echo "$(BLUE)A2A 智能体网络微服务 - 开发工具$(RESET)"
	@echo ""
	@echo "$(GREEN)可用命令:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 环境检查
check-uv:
	@which uv > /dev/null || (echo "$(RED)错误: 请先安装 UV 包管理器$(RESET)" && exit 1)

check-python:
	@python --version | grep -q "$(PYTHON_VERSION)" || (echo "$(YELLOW)警告: 建议使用 Python $(PYTHON_VERSION)$(RESET)")

# 依赖安装
install: check-uv ## 安装生产依赖
	@echo "$(BLUE)安装生产依赖...$(RESET)"
	uv pip install -e .

install-dev: check-uv ## 安装开发依赖
	@echo "$(BLUE)安装开发依赖...$(RESET)"
	uv pip install -e ".[dev,monitoring]"
	uv pip install pre-commit
	pre-commit install

install-prod: check-uv ## 安装生产环境依赖
	@echo "$(BLUE)安装生产环境依赖...$(RESET)"
	uv pip install -e ".[production,monitoring]"

# 代码质量
format: ## 格式化代码
	@echo "$(BLUE)格式化代码...$(RESET)"
	black .
	isort .
	ruff --fix .

lint: ## 代码检查
	@echo "$(BLUE)执行代码检查...$(RESET)"
	ruff check .
	black --check .
	isort --check-only .

type-check: ## 类型检查
	@echo "$(BLUE)执行类型检查...$(RESET)"
	mypy internal cmd pkg

security: ## 安全检查
	@echo "$(BLUE)执行安全检查...$(RESET)"
	bandit -r internal cmd pkg
	safety check

pre-commit: ## 运行 pre-commit 检查
	@echo "$(BLUE)运行 pre-commit 检查...$(RESET)"
	pre-commit run --all-files

# 测试
test: ## 运行测试
	@echo "$(BLUE)运行测试...$(RESET)"
	pytest test/ -v

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(BLUE)运行测试并生成覆盖率报告...$(RESET)"
	pytest test/ -v --cov=internal --cov=api --cov=cmd --cov-report=html --cov-report=term

test-unit: ## 运行单元测试
	@echo "$(BLUE)运行单元测试...$(RESET)"
	pytest test/unit/ -v -m "not slow"

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(RESET)"
	pytest test/integration/ -v

# 开发服务器
run: ## 启动开发服务器
	@echo "$(BLUE)启动开发服务器...$(RESET)"
	python cmd/server/main.py

run-dev: ## 启动开发模式服务器
	@echo "$(BLUE)启动开发模式服务器...$(RESET)"
	FLASK_ENV=development python cmd/server/main.py

run-prod: ## 启动生产模式服务器
	@echo "$(BLUE)启动生产模式服务器...$(RESET)"
	gunicorn --config config/gunicorn.conf.py cmd.server.main:app

# Docker 操作
docker-build: ## 构建 Docker 镜像
	@echo "$(BLUE)构建 Docker 镜像...$(RESET)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest

docker-run: ## 运行 Docker 容器
	@echo "$(BLUE)运行 Docker 容器...$(RESET)"
	docker run -d \
		--name $(PROJECT_NAME) \
		-p 5000:5000 \
		-p 5001:5001 \
		-v $(PWD)/config:/app/config \
		-v $(PWD)/logs:/app/logs \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-stop: ## 停止 Docker 容器
	@echo "$(BLUE)停止 Docker 容器...$(RESET)"
	docker stop $(PROJECT_NAME) || true
	docker rm $(PROJECT_NAME) || true

docker-logs: ## 查看 Docker 容器日志
	@echo "$(BLUE)查看 Docker 容器日志...$(RESET)"
	docker logs -f $(PROJECT_NAME)

# 部署
deploy-dev: ## 部署到开发环境
	@echo "$(BLUE)部署到开发环境...$(RESET)"
	kubectl apply -f deploy/kubernetes/namespace.yaml
	kubectl apply -f deploy/kubernetes/configmap.yaml
	kubectl apply -f deploy/kubernetes/deployment.yaml

deploy-prod: ## 部署到生产环境
	@echo "$(BLUE)部署到生产环境...$(RESET)"
	kubectl apply -f deploy/kubernetes/ --namespace=suoke-life-prod

# 数据库操作
db-migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(RESET)"
	python scripts/migrate.py

db-seed: ## 填充测试数据
	@echo "$(BLUE)填充测试数据...$(RESET)"
	python scripts/seed.py

# 监控和日志
logs: ## 查看应用日志
	@echo "$(BLUE)查看应用日志...$(RESET)"
	tail -f logs/app.log

metrics: ## 查看指标
	@echo "$(BLUE)查看指标...$(RESET)"
	curl http://localhost:9090/metrics

health: ## 健康检查
	@echo "$(BLUE)执行健康检查...$(RESET)"
	curl -f http://localhost:5000/health

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
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

clean-docker: ## 清理 Docker 资源
	@echo "$(BLUE)清理 Docker 资源...$(RESET)"
	docker system prune -f
	docker image prune -f

# 构建和发布
build: clean ## 构建项目
	@echo "$(BLUE)构建项目...$(RESET)"
	uv build

publish: build ## 发布到 PyPI
	@echo "$(BLUE)发布到 PyPI...$(RESET)"
	uv publish

# 开发工具
demo: ## 运行演示脚本
	@echo "$(BLUE)运行演示脚本...$(RESET)"
	python scripts/demo.py

benchmark: ## 运行性能测试
	@echo "$(BLUE)运行性能测试...$(RESET)"
	python scripts/benchmark.py

# 文档
docs: ## 生成文档
	@echo "$(BLUE)生成文档...$(RESET)"
	sphinx-build -b html docs/ docs/_build/html

docs-serve: ## 启动文档服务器
	@echo "$(BLUE)启动文档服务器...$(RESET)"
	python -m http.server 8000 --directory docs/_build/html

# 环境管理
venv: ## 创建虚拟环境
	@echo "$(BLUE)创建虚拟环境...$(RESET)"
	uv venv .venv --python $(PYTHON_VERSION)

venv-activate: ## 激活虚拟环境提示
	@echo "$(YELLOW)运行以下命令激活虚拟环境:$(RESET)"
	@echo "source .venv/bin/activate"

# 全面检查
check-all: lint type-check security test ## 运行所有检查

# 开发环境设置
setup-dev: venv install-dev ## 设置开发环境
	@echo "$(GREEN)开发环境设置完成!$(RESET)"
	@echo "$(YELLOW)请运行: source .venv/bin/activate$(RESET)"

# CI/CD
ci: check-all ## CI 流水线
	@echo "$(GREEN)CI 检查通过!$(RESET)"

# 版本管理
version: ## 显示版本信息
	@echo "$(BLUE)项目版本信息:$(RESET)"
	@python -c "from internal import __version__; print(f'版本: {__version__}')"
	@python --version
	@uv --version 