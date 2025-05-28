# 老克智能体服务 Makefile

.PHONY: help install dev test lint format clean build docker run-dev run-prod

# 默认目标
help: ## 显示帮助信息
	@echo "老克智能体服务 - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 环境设置
install: ## 安装依赖
	@echo "🔧 安装项目依赖..."
	uv venv --python 3.13
	uv sync --extra dev --extra performance --extra monitoring
	@echo "✅ 依赖安装完成"

install-prod: ## 安装生产环境依赖
	@echo "🔧 安装生产环境依赖..."
	uv venv --python 3.13
	uv sync --extra performance --extra monitoring
	@echo "✅ 生产环境依赖安装完成"

# 开发
dev: ## 启动开发服务器
	@echo "🚀 启动开发环境..."
	./scripts/dev.sh

run-dev: ## 启动开发服务器（详细模式）
	@echo "🚀 启动开发服务器..."
	uv run laoke-server --host 0.0.0.0 --port 8080 --reload --log-level debug

run-prod: ## 启动生产服务器
	@echo "🚀 启动生产服务器..."
	uv run laoke-server --host 0.0.0.0 --port 8080 --workers 4 --log-level info

# 测试
test: ## 运行所有测试
	@echo "🧪 运行测试..."
	uv run pytest -v

test-unit: ## 运行单元测试
	@echo "🧪 运行单元测试..."
	uv run pytest test/unit/ -v

test-integration: ## 运行集成测试
	@echo "🧪 运行集成测试..."
	uv run pytest test/integration/ -v

test-cov: ## 运行测试并生成覆盖率报告
	@echo "🧪 运行测试并生成覆盖率报告..."
	uv run pytest --cov=laoke_service --cov-report=html --cov-report=term-missing

test-watch: ## 监视文件变化并自动运行测试
	@echo "👀 监视测试..."
	uv run pytest-watch

# 代码质量
lint: ## 运行代码检查
	@echo "🔍 运行代码检查..."
	uv run ruff check .
	uv run mypy .
	uv run bandit -r laoke_service/

format: ## 格式化代码
	@echo "🎨 格式化代码..."
	uv run black .
	uv run isort .
	uv run ruff check --fix .

format-check: ## 检查代码格式
	@echo "🎨 检查代码格式..."
	uv run black --check .
	uv run isort --check-only .

security: ## 运行安全检查
	@echo "🔒 运行安全检查..."
	uv run bandit -r laoke_service/
	uv run safety check

# CLI 工具
cli-help: ## 显示CLI帮助
	uv run laoke-cli --help

config-show: ## 显示当前配置
	uv run laoke-cli config show

config-validate: ## 验证配置
	uv run laoke-cli config validate

agent-status: ## 检查智能体状态
	uv run laoke-cli agent status

agent-test: ## 测试智能体（需要设置MESSAGE变量）
	uv run laoke-cli agent test -m "$(MESSAGE)"

db-init: ## 初始化数据库
	uv run laoke-cli db init

db-migrate: ## 执行数据库迁移
	uv run laoke-cli db migrate

db-status: ## 检查数据库状态
	uv run laoke-cli db status

# 构建和部署
build: ## 构建项目
	@echo "🏗️ 构建项目..."
	uv build

docker-build: ## 构建Docker镜像
	@echo "🐳 构建Docker镜像..."
	docker build -t laoke-service:latest .

docker-run: ## 运行Docker容器
	@echo "🐳 运行Docker容器..."
	docker run -p 8080:8080 -e ENVIRONMENT=development laoke-service:latest

docker-dev: ## 运行开发Docker容器
	@echo "🐳 运行开发Docker容器..."
	docker run -p 8080:8080 -v $(PWD):/app -e ENVIRONMENT=development laoke-service:latest

# 清理
clean: ## 清理临时文件
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	@echo "✅ 清理完成"

clean-all: clean ## 清理所有文件（包括虚拟环境）
	@echo "🧹 清理所有文件..."
	rm -rf .venv/
	rm -rf logs/
	@echo "✅ 完全清理完成"

# 文档
docs: ## 生成文档
	@echo "📚 生成文档..."
	uv run mkdocs build

docs-serve: ## 启动文档服务器
	@echo "📚 启动文档服务器..."
	uv run mkdocs serve

# 性能分析
profile: ## 性能分析
	@echo "📊 运行性能分析..."
	uv run py-spy record -o profile.svg -- python -m laoke_service.cmd.server.main

memory-profile: ## 内存分析
	@echo "📊 运行内存分析..."
	uv run memory-profiler laoke_service/cmd/server/main.py

# 监控
logs: ## 查看日志
	@echo "📋 查看日志..."
	tail -f logs/laoke-service.log

logs-error: ## 查看错误日志
	@echo "📋 查看错误日志..."
	grep -i error logs/laoke-service.log | tail -20

metrics: ## 查看指标
	@echo "📊 获取指标..."
	curl -s http://localhost:8080/metrics

health: ## 健康检查
	@echo "🏥 健康检查..."
	curl -s http://localhost:8080/health | jq .

# 开发工具
pre-commit: ## 运行预提交检查
	@echo "🔍 运行预提交检查..."
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test

commit: ## 提交代码（运行完整检查）
	@echo "📝 准备提交代码..."
	$(MAKE) pre-commit
	@echo "✅ 代码检查通过，可以提交"

setup-dev: ## 设置开发环境
	@echo "🛠️ 设置开发环境..."
	$(MAKE) install
	$(MAKE) config-validate
	@echo "✅ 开发环境设置完成"

# 示例命令
example-chat: ## 示例：测试聊天功能
	uv run laoke-cli agent test -m "你好，老克" -t general_chat

example-knowledge: ## 示例：测试知识查询
	uv run laoke-cli agent test -m "什么是阴阳学说" -t knowledge_query

example-learning: ## 示例：测试学习计划
	uv run laoke-cli agent test -m "制定中医入门学习计划" -t learning_plan

# 版本信息
version: ## 显示版本信息
	uv run laoke-cli version

# 快速开始
quick-start: ## 快速开始（完整流程）
	@echo "🚀 快速开始老克智能体服务..."
	$(MAKE) setup-dev
	$(MAKE) dev 