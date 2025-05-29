.PHONY: all clean test lint format dev build docker-build docker-run docker-push dev-up dev-down grpc k8s-deploy uv-install uv-sync uv-update uv-dev uv-add uv-add-dev uv-remove

# 默认目标
all: lint test

# 环境变量
DOCKER_REPO ?= suoke
IMAGE_NAME ?= rag-service
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
DOCKER_TAG ?= $(VERSION)
DOCKER_IMAGE = $(DOCKER_REPO)/$(IMAGE_NAME):$(DOCKER_TAG)

# 项目目录
PROJECT_ROOT := $(shell pwd)
CONFIG_FILE ?= $(PROJECT_ROOT)/config/default.yaml

# UV 包管理器命令
uv-install:
	uv sync

# UV 同步依赖（生产环境）
uv-sync:
	uv sync --frozen

# UV 更新依赖
uv-update:
	uv sync --upgrade

# UV 安装开发依赖
uv-dev:
	uv sync --dev

# UV 添加新依赖
uv-add:
	@echo "Usage: make uv-add PACKAGE=package_name"
	@if [ -z "$(PACKAGE)" ]; then echo "Please specify PACKAGE=package_name"; exit 1; fi
	uv add $(PACKAGE)

# UV 添加开发依赖
uv-add-dev:
	@echo "Usage: make uv-add-dev PACKAGE=package_name"
	@if [ -z "$(PACKAGE)" ]; then echo "Please specify PACKAGE=package_name"; exit 1; fi
	uv add --dev $(PACKAGE)

# UV 移除依赖
uv-remove:
	@echo "Usage: make uv-remove PACKAGE=package_name"
	@if [ -z "$(PACKAGE)" ]; then echo "Please specify PACKAGE=package_name"; exit 1; fi
	uv remove $(PACKAGE)

# 传统 pip 安装依赖（兼容性保留）
install:
	pip install -e .

# 传统 pip 安装开发依赖（兼容性保留）
dev-install:
	pip install -e ".[dev]"

# 清理缓存和构建文件
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage

# 运行测试
test:
	uv run pytest test/ -v

# 运行单元测试
unit-test:
	uv run pytest test/unit/ -v

# 运行集成测试
integration-test:
	uv run pytest test/integration/ -v

# 代码覆盖率
coverage:
	uv run pytest --cov=internal --cov-report=html

# 代码风格检查（使用 ruff 替代 flake8）
lint:
	uv run ruff check internal/ cmd/ test/
	uv run mypy internal/ cmd/

# 格式化代码（使用 ruff 和 black）
format:
	uv run ruff format internal/ cmd/ test/
	uv run black internal/ cmd/ test/
	uv run isort internal/ cmd/ test/

# 修复代码风格问题
fix:
	uv run ruff check --fix internal/ cmd/ test/
	uv run ruff format internal/ cmd/ test/

# 启动开发服务
dev:
	uv run python -m cmd.server.main --config=$(CONFIG_FILE)

# 构建Docker镜像（使用 UV 优化的 Dockerfile）
docker-build:
	docker build -f Dockerfile.uv -t $(DOCKER_IMAGE) .
	@echo "Built $(DOCKER_IMAGE)"

# 构建传统Docker镜像
docker-build-legacy:
	docker build -t $(DOCKER_IMAGE) .
	@echo "Built $(DOCKER_IMAGE)"

# 运行Docker容器
docker-run:
	docker run -p 8000:8000 -p 50051:50051 \
		-v $(PROJECT_ROOT)/config:/app/config \
		-v $(PROJECT_ROOT)/data:/app/data \
		-v $(PROJECT_ROOT)/logs:/app/logs \
		--env-file .env \
		$(DOCKER_IMAGE)

# 推送Docker镜像到仓库
docker-push: docker-build
	docker push $(DOCKER_IMAGE)
	@echo "Pushed $(DOCKER_IMAGE)"

# 使用docker-compose启动开发环境
dev-up:
	docker-compose -f deploy/docker/docker-compose.dev.yml up -d

# 停止开发环境
dev-down:
	docker-compose -f deploy/docker/docker-compose.dev.yml down

# 生成gRPC代码
grpc:
	uv run python -m grpc_tools.protoc \
		-I./api/grpc \
		--python_out=./api/grpc/generated \
		--grpc_python_out=./api/grpc/generated \
		./api/grpc/rag_service.proto

# 部署到Kubernetes
k8s-deploy:
	kubectl apply -f deploy/kubernetes/rag-service.yaml

# 安全检查
security:
	uv run bandit -r internal/ cmd/
	uv run safety check

# 性能测试
benchmark:
	uv run pytest test/ --benchmark-only

# 打印版本信息
version:
	@echo $(VERSION)

# 检查依赖更新
check-updates:
	uv tree --outdated

# 帮助命令
help:
	@echo "Available commands:"
	@echo ""
	@echo "UV Package Management:"
	@echo "  make uv-install        - Install dependencies with UV"
	@echo "  make uv-sync           - Sync dependencies (production)"
	@echo "  make uv-update         - Update all dependencies"
	@echo "  make uv-dev            - Install with dev dependencies"
	@echo "  make uv-add PACKAGE=x  - Add new dependency"
	@echo "  make uv-add-dev PACKAGE=x - Add new dev dependency"
	@echo "  make uv-remove PACKAGE=x - Remove dependency"
	@echo ""
	@echo "Legacy Commands:"
	@echo "  make install           - Install dependencies with pip"
	@echo "  make dev-install       - Install dev dependencies with pip"
	@echo ""
	@echo "Development:"
	@echo "  make clean             - Clean cache and build files"
	@echo "  make test              - Run all tests"
	@echo "  make unit-test         - Run unit tests"
	@echo "  make integration-test  - Run integration tests"
	@echo "  make coverage          - Generate code coverage report"
	@echo "  make lint              - Check code style"
	@echo "  make format            - Format code"
	@echo "  make fix               - Fix code style issues"
	@echo "  make dev               - Start development server"
	@echo "  make security          - Run security checks"
	@echo "  make benchmark         - Run performance tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker image (UV optimized)"
	@echo "  make docker-build-legacy - Build Docker image (legacy)"
	@echo "  make docker-run        - Run Docker container"
	@echo "  make docker-push       - Push Docker image to registry"
	@echo "  make dev-up            - Start development environment"
	@echo "  make dev-down          - Stop development environment"
	@echo ""
	@echo "Other:"
	@echo "  make grpc              - Generate gRPC code"
	@echo "  make k8s-deploy        - Deploy to Kubernetes"
	@echo "  make version           - Print version info"
	@echo "  make check-updates     - Check for dependency updates"
	@echo "  make help              - Show this help message"