# 索克生活闻诊服务 Makefile
# 基于 Python 3.13.3 和 UV 包管理器

.PHONY: help install dev test lint format clean run-rest run-grpc run-hybrid docker-build docker-run

# 默认目标
help:
	@echo "索克生活闻诊服务开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install      - 安装依赖包"
	@echo "  dev          - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo "  clean        - 清理临时文件"
	@echo "  run-rest     - 启动REST API服务器"
	@echo "  run-grpc     - 启动gRPC服务器"
	@echo "  run-hybrid   - 启动混合服务器"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run   - 运行Docker容器"

# 安装依赖
install:
	@echo "安装生产依赖..."
	uv sync --no-dev

# 安装开发依赖
dev:
	@echo "安装开发依赖..."
	uv sync

# 运行测试
test:
	@echo "运行测试..."
	uv run pytest tests/ -v

# 运行测试并生成覆盖率报告
test-cov:
	@echo "运行测试并生成覆盖率报告..."
	uv run pytest tests/ -v --cov=listen_service --cov-report=html --cov-report=term

# 代码检查
lint:
	@echo "运行代码检查..."
	uv run ruff check listen_service/ tests/
	uv run mypy listen_service/

# 格式化代码
format:
	@echo "格式化代码..."
	uv run ruff format listen_service/ tests/
	uv run ruff check --fix listen_service/ tests/

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.coverage" -delete 2>/dev/null || true

# 启动REST API服务器
run-rest:
	@echo "启动REST API服务器..."
	uv run python scripts/start_server.py

# 启动gRPC服务器
run-grpc:
	@echo "启动gRPC服务器..."
	uv run python -m listen_service.cmd.server grpc

# 启动混合服务器
run-hybrid:
	@echo "启动混合服务器..."
	uv run python -m listen_service.cmd.server hybrid

# 测试组件
test-components:
	@echo "测试组件功能..."
	uv run python -m listen_service.cmd.server test-components

# 构建Docker镜像
docker-build:
	@echo "构建Docker镜像..."
	docker build -t suoke-listen-service:latest .

# 运行Docker容器
docker-run:
	@echo "运行Docker容器..."
	docker run -p 8000:8000 -p 50051:50051 suoke-listen-service:latest

# 开发模式（自动重载）
dev-rest:
	@echo "启动开发模式REST API服务器..."
	uv run python -m listen_service.cmd.server rest --reload

# 生成API文档
docs:
	@echo "生成API文档..."
	uv run python -c "from listen_service.delivery.rest_api import create_rest_app; import json; app = create_rest_app(); print(json.dumps(app.openapi(), indent=2))" > docs/openapi.json

# 检查依赖安全性
security:
	@echo "检查依赖安全性..."
	uv run safety check

# 性能测试
perf-test:
	@echo "运行性能测试..."
	uv run pytest tests/test_performance.py -v

# 集成测试
integration-test:
	@echo "运行集成测试..."
	uv run pytest tests/test_integration.py -v

# 完整测试流程
test-all: lint test integration-test
	@echo "所有测试完成!"

# 发布准备
release-prep: clean format lint test-cov
	@echo "发布准备完成!"

# 健康检查
health-check:
	@echo "检查服务健康状态..."
	curl -f http://localhost:8000/health || echo "服务未运行"

# 查看日志
logs:
	@echo "查看服务日志..."
	tail -f logs/listen_service.log

# 监控指标
metrics:
	@echo "查看监控指标..."
	curl -s http://localhost:8000/api/v1/performance/metrics | python -m json.tool

# 清空缓存
clear-cache:
	@echo "清空服务缓存..."
	curl -X DELETE http://localhost:8000/api/v1/cache/clear

# 开发环境设置
setup-dev: dev
	@echo "设置开发环境..."
	@echo "创建必要的目录..."
	mkdir -p logs data temp
	@echo "开发环境设置完成!"

# 生产环境设置
setup-prod: install
	@echo "设置生产环境..."
	mkdir -p logs data temp
	@echo "生产环境设置完成!" 