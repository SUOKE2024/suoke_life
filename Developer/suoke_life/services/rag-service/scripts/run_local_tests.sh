#!/bin/bash
# 本地测试脚本 - 执行代码检查、单元测试和Docker构建

set -e  # 任何命令失败则立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 初始化测试结果标记
TEST_FAILED=0

# 打印带颜色的标题
print_header() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# 打印成功消息
print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

# 打印错误消息
print_error() {
  echo -e "${RED}❌ $1${NC}"
  TEST_FAILED=1
}

# 打印警告消息
print_warning() {
  echo -e "${YELLOW}⚠️ $1${NC}"
}

# 检查命令是否存在
check_command() {
  if ! command -v $1 &> /dev/null; then
    print_error "命令 '$1' 未找到，请先安装"
    exit 1
  fi
}

# 导航到项目根目录
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)
print_header "当前目录: $ROOT_DIR"

# 检查必要命令
check_command python
check_command pip
check_command docker

# 创建虚拟环境(如果不存在)
if [ ! -d "venv" ]; then
  print_header "创建虚拟环境"
  python -m venv venv
fi

# 激活虚拟环境
print_header "激活虚拟环境"
source venv/bin/activate || source venv/Scripts/activate

# 安装依赖
print_header "安装依赖"
pip install -r requirements.txt
pip install black mypy pylint pytest pytest-cov locust

# 1. 代码格式检查
print_header "运行代码格式检查 (Black)"
if python -m black --check src tests; then
  print_success "代码格式检查通过"
else
  print_error "代码格式检查失败"
  print_warning "运行 'black src tests' 来格式化代码"
fi

# 2. 类型检查
print_header "运行类型检查 (MyPy)"
if python -m mypy src; then
  print_success "类型检查通过"
else
  print_error "类型检查失败"
fi

# 3. 代码风格检查
print_header "运行代码风格检查 (Pylint)"
if python -m pylint --disable=all --enable=E,F,W src tests; then
  print_success "代码风格检查通过"
else
  print_error "代码风格检查失败"
fi

# 4. 单元测试
print_header "运行单元测试 (Pytest)"
if python -m pytest --cov=src tests/; then
  print_success "单元测试通过"
else
  print_error "单元测试失败"
fi

# 5. Docker构建测试
print_header "Docker构建测试"
if docker build -t rag-service:test .; then
  print_success "Docker构建成功"
else
  print_error "Docker构建失败"
fi

# 6. 运行本地功能测试
print_header "运行功能测试"
if [ -f ".env" ]; then
  if python scripts/verify_deployment.py --env=dev --verbose --retries=1; then
    print_success "功能测试通过"
  else
    print_warning "功能测试失败，但这可能是因为远程服务未运行"
  fi
else
  print_warning "未找到.env文件，跳过功能测试"
fi

# 退出虚拟环境
deactivate

# 总结
print_header "测试结果摘要"
if [ $TEST_FAILED -eq 0 ]; then
  print_success "所有本地测试通过! 可以安全提交代码触发CI/CD流程"
  echo -e "\n${GREEN}请执行以下命令提交并触发CI/CD流程:${NC}"
  echo -e "git add ."
  echo -e "git commit -m \"描述你的更改\""
  echo -e "git push origin 你的分支名"
else
  print_error "本地测试失败。请修复上述问题后再提交代码"
  exit 1
fi 