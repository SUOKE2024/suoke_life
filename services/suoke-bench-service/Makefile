# SuokeBench 服务 Makefile

.PHONY: help install dev test test-coverage lint format type-check build clean docker-build docker-run deploy

# 默认目标
help:
	@echo "SuokeBench 服务管理命令:"
	@echo ""
	@echo "开发环境:"
	@echo "  install        安装依赖"
	@echo "  dev            启动开发服务器"
	@echo "  test           运行测试"
	@echo "  test-coverage  运行测试并生成覆盖率报告"
	@echo ""
	@echo "代码质量:"
	@echo "  lint           代码风格检查"
	@echo "  format         代码格式化"
	@echo "  type-check     类型检查"
	@echo "  sort-imports   排序导入"
	@echo ""
	@echo "构建部署:"
	@echo "  build          构建项目"
	@echo "  clean          清理构建文件"
	@echo "  docker-build   构建 Docker 镜像"
	@echo "  docker-run     运行 Docker 容器"
	@echo "  deploy         部署到 Kubernetes"
	@echo ""

# 开发环境
install:
	@echo "安装依赖..."
	uv sync
	@echo "依赖安装完成"

dev:
	@echo "启动开发服务器..."
	uvicorn cmd.server.main:app --host 0.0.0.0 --port 8000 --reload

dev-grpc:
	@echo "启动 gRPC 开发服务器..."
	python cmd/server/grpc_server.py

# 测试
test:
	@echo "运行测试..."
	pytest test/ -v

test-unit:
	@echo "运行单元测试..."
	pytest test/unit/ -v

test-integration:
	@echo "运行集成测试..."
	pytest test/integration/ -v

test-e2e:
	@echo "运行端到端测试..."
	pytest test/test_e2e.py -v

test-coverage:
	@echo "运行测试并生成覆盖率报告..."
	pytest test/ --cov=internal --cov=suoke_bench_service --cov-report=html --cov-report=term-missing
	@echo "覆盖率报告已生成到 htmlcov/ 目录"

test-watch:
	@echo "监控模式运行测试..."
	pytest-watch test/ -- -v

# 代码质量
lint:
	@echo "运行代码风格检查..."
	flake8 internal/ suoke_bench_service/ test/ cmd/
	@echo "代码风格检查完成"

format:
	@echo "格式化代码..."
	black internal/ suoke_bench_service/ test/ cmd/
	@echo "代码格式化完成"

sort-imports:
	@echo "排序导入..."
	isort internal/ suoke_bench_service/ test/ cmd/
	@echo "导入排序完成"

type-check:
	@echo "运行类型检查..."
	mypy internal/ suoke_bench_service/ cmd/
	@echo "类型检查完成"

check-all: lint type-check test
	@echo "所有检查完成"

fix-all: format sort-imports
	@echo "代码修复完成"

# 构建
build:
	@echo "构建项目..."
	python -m build
	@echo "构建完成"

clean:
	@echo "清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "清理完成"

# Docker
docker-build:
	@echo "构建 Docker 镜像..."
	docker build -t suokebench:latest .
	@echo "Docker 镜像构建完成"

docker-build-dev:
	@echo "构建开发 Docker 镜像..."
	docker build -f Dockerfile.dev -t suokebench:dev .
	@echo "开发 Docker 镜像构建完成"

docker-run:
	@echo "运行 Docker 容器..."
	docker run -p 8000:8000 --env-file .env suokebench:latest

docker-run-dev:
	@echo "运行开发 Docker 容器..."
	docker run -p 8000:8000 -v $(PWD):/app --env-file .env suokebench:dev

docker-compose-up:
	@echo "启动 Docker Compose 服务..."
	docker-compose -f deploy/docker-compose.yml up -d

docker-compose-down:
	@echo "停止 Docker Compose 服务..."
	docker-compose -f deploy/docker-compose.yml down

# 数据库
db-migrate:
	@echo "运行数据库迁移..."
	alembic upgrade head

db-migrate-create:
	@echo "创建数据库迁移..."
	alembic revision --autogenerate -m "$(name)"

db-reset:
	@echo "重置数据库..."
	alembic downgrade base
	alembic upgrade head

# 部署
deploy-k8s:
	@echo "部署到 Kubernetes..."
	kubectl apply -f deploy/kubernetes/

deploy-k8s-dev:
	@echo "部署到开发环境..."
	kubectl apply -f deploy/kubernetes/dev/

deploy-k8s-prod:
	@echo "部署到生产环境..."
	kubectl apply -f deploy/kubernetes/prod/

# 监控
logs:
	@echo "查看服务日志..."
	kubectl logs -f deployment/suokebench

logs-tail:
	@echo "实时查看日志..."
	tail -f logs/suokebench.log

metrics:
	@echo "查看指标..."
	curl http://localhost:8000/metrics

health:
	@echo "健康检查..."
	curl http://localhost:8000/health

# 开发工具
generate-proto:
	@echo "生成 gRPC 代码..."
	python -m grpc_tools.protoc \
		--proto_path=api/grpc \
		--python_out=api/grpc \
		--grpc_python_out=api/grpc \
		api/grpc/*.proto

install-dev-tools:
	@echo "安装开发工具..."
	pip install black isort flake8 mypy pytest pytest-cov pytest-watch

setup-pre-commit:
	@echo "设置 pre-commit hooks..."
	pre-commit install

# 性能测试
benchmark:
	@echo "运行性能基准测试..."
	python scripts/benchmark.py

profile:
	@echo "运行性能分析..."
	python -m cProfile -o profile.stats cmd/server/main.py
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# 安全检查
security-check:
	@echo "运行安全检查..."
	bandit -r internal/ suoke_bench_service/ cmd/

dependency-check:
	@echo "检查依赖漏洞..."
	safety check

# 文档
docs-build:
	@echo "构建文档..."
	mkdocs build

docs-serve:
	@echo "启动文档服务器..."
	mkdocs serve

docs-deploy:
	@echo "部署文档..."
	mkdocs gh-deploy

# 发布
release-patch:
	@echo "发布补丁版本..."
	bump2version patch

release-minor:
	@echo "发布次要版本..."
	bump2version minor

release-major:
	@echo "发布主要版本..."
	bump2version major

# 环境管理
env-create:
	@echo "创建虚拟环境..."
	python -m venv venv
	@echo "激活环境: source venv/bin/activate"

env-requirements:
	@echo "导出依赖..."
	pip freeze > requirements.txt

# 数据管理
data-download:
	@echo "下载测试数据..."
	python scripts/download_data.py

data-preprocess:
	@echo "预处理数据..."
	python scripts/preprocess_data.py

# 模型管理
model-download:
	@echo "下载模型..."
	python scripts/download_models.py

model-validate:
	@echo "验证模型..."
	python scripts/validate_models.py

# 配置管理
config-validate:
	@echo "验证配置..."
	python scripts/validate_config.py

config-generate:
	@echo "生成配置模板..."
	python scripts/generate_config.py

# 备份恢复
backup:
	@echo "备份数据..."
	python scripts/backup.py

restore:
	@echo "恢复数据..."
	python scripts/restore.py $(file)

# 清理和维护
clean-logs:
	@echo "清理日志文件..."
	find logs/ -name "*.log" -mtime +7 -delete

clean-cache:
	@echo "清理缓存..."
	python scripts/clean_cache.py

maintenance:
	@echo "运行维护任务..."
	python scripts/maintenance.py

# 快捷命令
quick-start: install dev

quick-test: format lint test

quick-deploy: test docker-build deploy-k8s

full-check: format sort-imports lint type-check test-coverage security-check

# 帮助信息
info:
	@echo "项目信息:"
	@echo "  名称: SuokeBench"
	@echo "  版本: $(shell python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")"
	@echo "  Python: $(shell python --version)"
	@echo "  环境: $(shell echo $$SUOKEBENCH_ENV)"