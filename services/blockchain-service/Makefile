# 索克生活区块链服务 Makefile
# 使用 UV 和 Python 3.13.3 的现代化项目管理

.PHONY: help install install-dev sync update clean test test-cov lint format type-check security-check pre-commit run dev build docker-build docker-run deploy-contracts migrate-db docs serve-docs

# 默认目标
help: ## 显示帮助信息
	@echo "索克生活区块链服务 - 可用命令："
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 环境管理
install: ## 安装生产依赖
	uv sync --no-dev

install-dev: ## 安装开发依赖
	uv sync

sync: ## 同步依赖（基于 uv.lock）
	uv sync

update: ## 更新依赖
	uv lock --upgrade
	uv sync

# 清理
clean: ## 清理临时文件和缓存
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/

# 测试
test: ## 运行测试
	uv run pytest

test-unit: ## 运行单元测试
	uv run pytest tests/unit -v

test-integration: ## 运行集成测试
	uv run pytest tests/integration -v

test-cov: ## 运行测试并生成覆盖率报告
	uv run pytest --cov=suoke_blockchain_service --cov-report=html --cov-report=term

test-watch: ## 监视文件变化并自动运行测试
	uv run pytest-watch

# 代码质量
lint: ## 运行代码检查
	uv run ruff check .

lint-fix: ## 自动修复代码问题
	uv run ruff check --fix .

format: ## 格式化代码
	uv run ruff format .

format-check: ## 检查代码格式
	uv run ruff format --check .

type-check: ## 运行类型检查
	uv run mypy suoke_blockchain_service

security-check: ## 运行安全检查
	uv run bandit -r suoke_blockchain_service
	uv run safety check

# Git hooks
pre-commit-install: ## 安装 pre-commit hooks
	uv run pre-commit install

pre-commit: ## 运行 pre-commit 检查
	uv run pre-commit run --all-files

# 开发服务器
run: ## 运行服务
	uv run python -m suoke_blockchain_service.main serve

dev: ## 开发模式运行服务
	uv run python -m suoke_blockchain_service.main serve --reload

# 数据库
migrate-db: ## 运行数据库迁移
	uv run python -m suoke_blockchain_service.main migrate-db

create-migration: ## 创建新的数据库迁移
	uv run alembic revision --autogenerate -m "$(name)"

# 区块链
deploy-contracts: ## 部署智能合约
	uv run python -m suoke_blockchain_service.main deploy-contracts

# 构建和部署
build: ## 构建 Python 包
	uv build

docker-build: ## 构建 Docker 镜像
	docker build -t suoke/blockchain-service:latest -f deploy/docker/Dockerfile .

docker-run: ## 运行 Docker 容器
	docker run -d --name blockchain-service \
		-p 50055:50055 -p 8080:8080 -p 9090:9090 \
		-v $(PWD)/config:/app/config \
		--env-file .env \
		suoke/blockchain-service:latest

docker-stop: ## 停止 Docker 容器
	docker stop blockchain-service || true
	docker rm blockchain-service || true

# 文档
docs: ## 生成文档
	uv run mkdocs build

serve-docs: ## 启动文档服务器
	uv run mkdocs serve

# 性能分析
profile: ## 运行性能分析
	uv run py-spy record -o profile.svg -- python -m suoke_blockchain_service.main serve

memory-profile: ## 运行内存分析
	uv run mprof run python -m suoke_blockchain_service.main serve
	uv run mprof plot

# 完整的 CI/CD 流程
ci: clean install-dev lint format-check type-check security-check test-cov ## 运行完整的 CI 检查

# 项目初始化
init: ## 初始化项目（首次设置）
	cp env.example .env
	uv sync
	uv run pre-commit install
	@echo "项目初始化完成！请编辑 .env 文件配置环境变量。"

# 版本管理
version-patch: ## 升级补丁版本
	uv run bump2version patch

version-minor: ## 升级次要版本
	uv run bump2version minor

version-major: ## 升级主要版本
	uv run bump2version major

# 健康检查
health-check: ## 检查服务健康状态
	curl -f http://localhost:8080/health || exit 1

ready-check: ## 检查服务就绪状态
	curl -f http://localhost:8080/ready || exit 1

# 监控
metrics: ## 查看 Prometheus 指标
	curl http://localhost:9090/metrics

# 开发工具
shell: ## 启动 Python shell
	uv run python

jupyter: ## 启动 Jupyter notebook
	uv run jupyter lab

# 备份和恢复
backup-db: ## 备份数据库
	pg_dump $(DATABASE_URL) > backup_$(shell date +%Y%m%d_%H%M%S).sql

# 日志查看
logs: ## 查看服务日志
	docker logs -f blockchain-service

logs-tail: ## 实时查看日志
	tail -f logs/blockchain-service.log 