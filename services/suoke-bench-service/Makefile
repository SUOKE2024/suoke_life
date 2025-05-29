.PHONY: all clean install test lint format build docker-build docker-push deploy help

# 变量定义
PYTHON := python3
UV := uv
DOCKER := docker
KUBECTL := kubectl
IMAGE_NAME := suoke/bench-service
IMAGE_TAG := latest
NAMESPACE := suoke-bench

# 帮助信息
help:
	@echo "可用命令:"
	@echo "  make install        安装依赖"
	@echo "  make test          运行测试"
	@echo "  make lint          运行代码检查"
	@echo "  make format        格式化代码"
	@echo "  make clean         清理临时文件"
	@echo "  make build         构建项目"
	@echo "  make docker-build  构建Docker镜像"
	@echo "  make docker-push   推送Docker镜像"
	@echo "  make deploy        部署到Kubernetes"
	@echo "  make bench         运行基准测试"
	@echo "  make docs          生成文档"

# 安装依赖
install:
	$(UV) sync

# 安装开发依赖
install-dev:
	$(UV) sync --dev

# 运行测试
test:
	$(UV) run pytest test/ -v --cov=internal --cov-report=term-missing

# 代码检查
lint:
	$(UV) run ruff check internal/ test/
	$(UV) run mypy internal/ test/

# 格式化代码
format:
	$(UV) run ruff format internal/ test/
	$(UV) run ruff check --fix internal/ test/

# 清理临时文件
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# 构建项目
build: clean
	$(UV) build

# 构建Docker镜像
docker-build:
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# 推送Docker镜像
docker-push:
	$(DOCKER) push $(IMAGE_NAME):$(IMAGE_TAG)

# 部署到Kubernetes
deploy:
	$(KUBECTL) apply -f deploy/kubernetes/suoke-bench.yaml

# 运行基准测试
bench:
	$(UV) run python -m internal.suokebench.runner

# 生成文档
docs:
	$(UV) run mkdocs build

# 启动开发服务器
dev:
	$(UV) run uvicorn cmd.server.main:app --reload --host 0.0.0.0 --port 8000

# 生成gRPC代码
grpc:
	$(UV) run python -m grpc_tools.protoc \
		-I api/grpc \
		--python_out=internal/grpc \
		--grpc_python_out=internal/grpc \
		api/grpc/*.proto

# 创建迁移
migrate-create:
	$(UV) run alembic revision --autogenerate -m "$(message)"

# 应用迁移
migrate:
	$(UV) run alembic upgrade head

# 回滚迁移
migrate-rollback:
	$(UV) run alembic downgrade -1

# 检查依赖更新
deps-check:
	$(UV) tree

# 更新依赖
deps-update:
	$(UV) sync --upgrade

# 添加新依赖
add:
	$(UV) add $(package)

# 添加开发依赖
add-dev:
	$(UV) add --dev $(package)

# 移除依赖
remove:
	$(UV) remove $(package)

# 安全检查
security-check:
	$(UV) run safety check
	$(UV) run bandit -r internal/

# 性能分析
profile:
	$(UV) run py-spy record -o profile.svg -- python -m internal.suokebench.runner

# 默认目标
all: clean install lint test build