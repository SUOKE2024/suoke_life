.PHONY: all clean test lint format dev build docker-build docker-run docker-push dev-up dev-down grpc k8s-deploy

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

# 安装依赖
install:
	pip install -r requirements.txt

# 安装开发依赖
dev-install:
	pip install -r requirements.txt -r requirements-dev.txt

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
	rm -rf build/ dist/ .coverage

# 运行测试
test:
	python -m pytest test/ -v

# 运行单元测试
unit-test:
	python -m pytest test/unit/ -v

# 运行集成测试
integration-test:
	python -m pytest test/integration/ -v

# 代码覆盖率
coverage:
	python -m pytest --cov=internal --cov-report=html

# 代码风格检查
lint:
	flake8 internal/ cmd/ test/
	mypy internal/ cmd/

# 格式化代码
format:
	black internal/ cmd/ test/
	isort internal/ cmd/ test/

# 启动开发服务
dev:
	python -m cmd.server.main --config=$(CONFIG_FILE)

# 构建Docker镜像
docker-build:
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
	python -m grpc_tools.protoc \
		-I./api/grpc \
		--python_out=./api/grpc/generated \
		--grpc_python_out=./api/grpc/generated \
		./api/grpc/rag_service.proto

# 部署到Kubernetes
k8s-deploy:
	kubectl apply -f deploy/kubernetes/rag-service.yaml

# 打印版本信息
version:
	@echo $(VERSION)

# 帮助命令
help:
	@echo "Available commands:"
	@echo "  make install           - Install dependencies"
	@echo "  make dev-install       - Install development dependencies"
	@echo "  make clean             - Clean cache and build files"
	@echo "  make test              - Run all tests"
	@echo "  make unit-test         - Run unit tests"
	@echo "  make integration-test  - Run integration tests"
	@echo "  make coverage          - Generate code coverage report"
	@echo "  make lint              - Check code style"
	@echo "  make format            - Format code"
	@echo "  make dev               - Start development server"
	@echo "  make docker-build      - Build Docker image"
	@echo "  make docker-run        - Run Docker container"
	@echo "  make docker-push       - Push Docker image to registry"
	@echo "  make dev-up            - Start development environment"
	@echo "  make dev-down          - Stop development environment"
	@echo "  make grpc              - Generate gRPC code"
	@echo "  make k8s-deploy        - Deploy to Kubernetes"
	@echo "  make version           - Print version info"
	@echo "  make help              - Show this help message"