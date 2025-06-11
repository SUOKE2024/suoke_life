#!/bin/bash

# AI Model Service 开发工具脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 切换到项目目录
cd "$PROJECT_DIR"

usage() {
    cat << EOF
AI Model Service 开发工具

用法: $0 <命令> [选项]

命令:
    setup           初始化开发环境
    install         安装依赖
    test            运行测试
    test-cov        运行测试并生成覆盖率报告
    lint            代码检查
    format          代码格式化
    type-check      类型检查
    security        安全检查
    build           构建Docker镜像
    clean           清理临时文件
    docs            生成文档
    dev             开发模式启动
    check-all       运行所有检查

选项:
    -h, --help      显示此帮助信息

示例:
    $0 setup                    # 初始化开发环境
    $0 test                     # 运行测试
    $0 test-cov                 # 运行测试并生成覆盖率报告
    $0 lint                     # 代码检查
    $0 format                   # 代码格式化
    $0 build                    # 构建Docker镜像
    $0 dev                      # 开发模式启动

EOF
}

# 检查UV包管理器
check_uv() {
    if ! command -v uv &> /dev/null; then
        log_warn "UV包管理器未安装，正在安装..."
        pip install uv
    fi
}

# 初始化开发环境
setup() {
    log_info "初始化开发环境..."
    
    check_uv
    
    # 创建虚拟环境
    if [[ ! -d ".venv" ]]; then
        log_info "创建虚拟环境..."
        uv venv
    fi
    
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 安装依赖
    log_info "安装开发依赖..."
    uv sync --dev
    
    # 安装pre-commit钩子
    if command -v pre-commit &> /dev/null; then
        log_info "安装pre-commit钩子..."
        pre-commit install
    fi
    
    log_info "开发环境初始化完成！"
}

# 安装依赖
install() {
    log_info "安装依赖..."
    
    check_uv
    
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 安装依赖
    uv sync --dev
    
    log_info "依赖安装完成！"
}

# 运行测试
test() {
    log_info "运行测试..."
    
    source .venv/bin/activate
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
    
    # 运行测试
    python -m pytest tests/ -v --tb=short
    
    log_info "测试完成！"
}

# 运行测试并生成覆盖率报告
test_cov() {
    log_info "运行测试并生成覆盖率报告..."
    
    source .venv/bin/activate
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
    
    # 运行测试并生成覆盖率报告
    python -m pytest tests/ \
        --cov=ai_model_service \
        --cov-report=html \
        --cov-report=term \
        --cov-report=xml \
        -v
    
    log_info "测试和覆盖率报告生成完成！"
    log_info "HTML报告: htmlcov/index.html"
}

# 代码检查
lint() {
    log_info "运行代码检查..."
    
    source .venv/bin/activate
    
    # Ruff检查
    log_info "运行Ruff检查..."
    python -m ruff check src/ tests/
    
    # Black检查
    log_info "运行Black检查..."
    python -m black --check src/ tests/
    
    # isort检查
    log_info "运行isort检查..."
    python -m isort --check-only src/ tests/
    
    log_info "代码检查完成！"
}

# 代码格式化
format() {
    log_info "格式化代码..."
    
    source .venv/bin/activate
    
    # Black格式化
    log_info "运行Black格式化..."
    python -m black src/ tests/
    
    # isort格式化
    log_info "运行isort格式化..."
    python -m isort src/ tests/
    
    # Ruff自动修复
    log_info "运行Ruff自动修复..."
    python -m ruff check --fix src/ tests/
    
    log_info "代码格式化完成！"
}

# 类型检查
type_check() {
    log_info "运行类型检查..."
    
    source .venv/bin/activate
    
    # MyPy类型检查
    python -m mypy src/
    
    log_info "类型检查完成！"
}

# 安全检查
security() {
    log_info "运行安全检查..."
    
    source .venv/bin/activate
    
    # Bandit安全检查
    python -m bandit -r src/ -f json -o bandit-report.json
    python -m bandit -r src/
    
    log_info "安全检查完成！"
}

# 构建Docker镜像
build() {
    log_info "构建Docker镜像..."
    
    # 获取版本号
    VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    IMAGE_NAME="suoke/ai-model-service"
    
    log_info "构建镜像: $IMAGE_NAME:$VERSION"
    
    # 构建镜像
    docker build -t "$IMAGE_NAME:$VERSION" -t "$IMAGE_NAME:latest" .
    
    log_info "Docker镜像构建完成！"
    log_info "镜像标签: $IMAGE_NAME:$VERSION, $IMAGE_NAME:latest"
}

# 清理临时文件
clean() {
    log_info "清理临时文件..."
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # 清理测试和覆盖率文件
    rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml
    
    # 清理构建文件
    rm -rf build/ dist/ *.egg-info/
    
    # 清理日志文件
    rm -rf logs/ *.log
    
    # 清理安全检查报告
    rm -f bandit-report.json
    
    log_info "临时文件清理完成！"
}

# 生成文档
docs() {
    log_info "生成文档..."
    
    source .venv/bin/activate
    
    # 生成API文档
    if command -v sphinx-build &> /dev/null; then
        sphinx-build -b html docs/ docs/_build/html/
        log_info "Sphinx文档生成完成: docs/_build/html/index.html"
    fi
    
    # 生成OpenAPI文档
    python -c "
import json
from ai_model_service.api.app import create_app

app = create_app()
with open('docs/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
"
    log_info "OpenAPI文档生成完成: docs/openapi.json"
}

# 开发模式启动
dev() {
    log_info "开发模式启动..."
    
    # 使用启动脚本的开发模式
    ./scripts/start.sh -e development -r -d
}

# 运行所有检查
check_all() {
    log_info "运行所有检查..."
    
    format
    lint
    type_check
    security
    test_cov
    
    log_info "所有检查完成！"
}

# 主函数
main() {
    case "${1:-}" in
        setup)
            setup
            ;;
        install)
            install
            ;;
        test)
            test
            ;;
        test-cov)
            test_cov
            ;;
        lint)
            lint
            ;;
        format)
            format
            ;;
        type-check)
            type_check
            ;;
        security)
            security
            ;;
        build)
            build
            ;;
        clean)
            clean
            ;;
        docs)
            docs
            ;;
        dev)
            dev
            ;;
        check-all)
            check_all
            ;;
        -h|--help|help)
            usage
            ;;
        "")
            log_error "请指定命令"
            usage
            exit 1
            ;;
        *)
            log_error "未知命令: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@" 