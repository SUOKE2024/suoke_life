.PHONY: help install dev test lint format clean run docker-build docker-run

# 默认目标
help:
	@echo "可用命令:"
	@echo "  install     - 安装项目依赖"
	@echo "  dev         - 安装开发依赖"
	@echo "  test        - 运行测试"
	@echo "  lint        - 运行代码检查"
	@echo "  format      - 格式化代码"
	@echo "  clean       - 清理缓存文件"
	@echo "  run         - 启动开发服务器"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run  - 运行Docker容器"

# 安装依赖
install:
	uv sync

# 安装开发依赖
dev:
	uv sync --group dev
	uv run pre-commit install

# 运行测试
test:
	uv run pytest tests/ -v --cov=health_data_service --cov-report=html --cov-report=term-missing

# 代码检查
lint:
	uv run ruff check health_data_service/
	uv run mypy health_data_service/

# 格式化代码
format:
	uv run ruff format health_data_service/
	uv run ruff check --fix health_data_service/

# 清理缓存
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

# 启动开发服务器
run:
	uv run health-data-service serve --reload

# 检查配置
check-config:
	uv run health-data-service check-config

# 健康检查
health:
	uv run health-data-service health

# 导出OpenAPI规范
export-openapi:
	uv run health-data-service export-openapi

# 构建Docker镜像
docker-build:
	docker build -t health-data-service:latest .

# 运行Docker容器
docker-run:
	docker run -p 8000:8000 --env-file .env.development health-data-service:latest

# 运行数据库迁移
migrate:
	uv run alembic upgrade head

# 创建新的数据库迁移
migration:
	uv run alembic revision --autogenerate -m "$(MSG)"

# 安装pre-commit hooks
pre-commit:
	uv run pre-commit install
	uv run pre-commit run --all-files 