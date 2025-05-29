# 索克生活平台通用组件库 Makefile

.PHONY: help install install-dev test test-cov lint format type-check clean build publish docs serve-docs pre-commit setup-dev

# 默认目标
help:
	@echo "索克生活平台通用组件库 - 可用命令："
	@echo ""
	@echo "开发环境设置："
	@echo "  setup-dev     - 设置完整的开发环境"
	@echo "  install       - 安装项目依赖"
	@echo "  install-dev   - 安装开发依赖"
	@echo ""
	@echo "代码质量："
	@echo "  lint          - 运行代码检查 (ruff)"
	@echo "  format        - 格式化代码 (ruff format)"
	@echo "  type-check    - 类型检查 (mypy)"
	@echo "  pre-commit    - 运行预提交钩子"
	@echo ""
	@echo "测试："
	@echo "  test          - 运行测试"
	@echo "  test-cov      - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "构建和发布："
	@echo "  build         - 构建包"
	@echo "  publish       - 发布到 PyPI"
	@echo ""
	@echo "文档："
	@echo "  docs          - 构建文档"
	@echo "  serve-docs    - 本地服务文档"
	@echo ""
	@echo "清理："
	@echo "  clean         - 清理构建文件"

# 检查 UV 是否安装
check-uv:
	@which uv > /dev/null || (echo "错误: 需要安装 UV。请访问 https://docs.astral.sh/uv/" && exit 1)

# 设置开发环境
setup-dev: check-uv
	@echo "设置索克生活平台通用组件库开发环境..."
	uv python install 3.13.3
	uv venv --python 3.13.3
	uv pip install -e ".[dev,test,docs]"
	uv run pre-commit install
	@echo "开发环境设置完成！"

# 安装项目依赖
install: check-uv
	@echo "安装项目依赖..."
	uv pip install -e .

# 安装开发依赖
install-dev: check-uv
	@echo "安装开发依赖..."
	uv pip install -e ".[dev,test,docs]"

# 代码检查
lint: check-uv
	@echo "运行代码检查..."
	uv run ruff check .
	uv run ruff format --check .

# 格式化代码
format: check-uv
	@echo "格式化代码..."
	uv run ruff format .
	uv run ruff check --fix .

# 类型检查
type-check: check-uv
	@echo "运行类型检查..."
	uv run mypy suoke_common

# 运行测试
test: check-uv
	@echo "运行测试..."
	uv run pytest

# 运行测试并生成覆盖率报告
test-cov: check-uv
	@echo "运行测试并生成覆盖率报告..."
	uv run pytest --cov=suoke_common --cov-report=html --cov-report=term-missing

# 运行预提交钩子
pre-commit: check-uv
	@echo "运行预提交钩子..."
	uv run pre-commit run --all-files

# 清理构建文件
clean:
	@echo "清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 构建包
build: check-uv clean
	@echo "构建包..."
	uv build

# 发布到 PyPI
publish: check-uv build
	@echo "发布到 PyPI..."
	uv publish

# 构建文档
docs: check-uv
	@echo "构建文档..."
	uv run mkdocs build

# 本地服务文档
serve-docs: check-uv
	@echo "启动文档服务器..."
	uv run mkdocs serve

# 检查项目状态
status: check-uv
	@echo "项目状态检查..."
	@echo "Python 版本:"
	uv run python --version
	@echo ""
	@echo "已安装的包:"
	uv pip list
	@echo ""
	@echo "项目信息:"
	uv run python -c "import suoke_common; print(f'版本: {suoke_common.__version__}')"

# 运行所有检查
check-all: lint type-check test
	@echo "所有检查完成！"

# 快速开发循环
dev: format lint type-check test
	@echo "开发循环完成！"

# 安全检查
security: check-uv
	@echo "运行安全检查..."
	uv run pip-audit

# 依赖更新
update-deps: check-uv
	@echo "更新依赖..."
	uv pip install --upgrade -e ".[dev,test,docs]"

# 生成依赖锁定文件
lock: check-uv
	@echo "生成依赖锁定文件..."
	uv lock

# 同步依赖
sync: check-uv
	@echo "同步依赖..."
	uv sync 