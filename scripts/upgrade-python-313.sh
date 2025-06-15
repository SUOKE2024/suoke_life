#!/bin/bash

# 索克生活 - Python 3.13+ 升级脚本
# Suoke Life - Python 3.13+ Upgrade Script

set -e

echo "🚀 开始升级到 Python 3.13+"
echo "Starting upgrade to Python 3.13+"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${BLUE}检测到操作系统: ${MACHINE}${NC}"

# 函数：检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 函数：安装 Python 3.13
install_python_313() {
    echo -e "${YELLOW}正在安装 Python 3.13...${NC}"
    
    if [[ "$MACHINE" == "Mac" ]]; then
        # macOS 使用 Homebrew
        if command_exists brew; then
            echo "使用 Homebrew 安装 Python 3.13..."
            brew install python@3.13 || brew upgrade python@3.13
            
            # 创建符号链接
            brew link --force python@3.13
            
            # 更新 PATH
            echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
            echo 'export PATH="/opt/homebrew/opt/python@3.13/bin:$PATH"' >> ~/.zshrc
            
        else
            echo -e "${RED}请先安装 Homebrew: https://brew.sh${NC}"
            exit 1
        fi
        
    elif [[ "$MACHINE" == "Linux" ]]; then
        # Linux 使用 deadsnakes PPA (Ubuntu/Debian)
        if command_exists apt-get; then
            echo "使用 apt 安装 Python 3.13..."
            sudo apt update
            sudo apt install -y software-properties-common
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt update
            sudo apt install -y python3.13 python3.13-dev python3.13-venv python3.13-distutils
            
            # 安装 pip
            curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13
            
        elif command_exists yum; then
            echo "使用 yum 安装 Python 3.13..."
            sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel
            
            # 从源码编译安装
            cd /tmp
            wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
            tar xzf Python-3.13.0.tgz
            cd Python-3.13.0
            ./configure --enable-optimizations
            make altinstall
            
        else
            echo -e "${RED}不支持的 Linux 发行版${NC}"
            exit 1
        fi
    else
        echo -e "${RED}不支持的操作系统: ${MACHINE}${NC}"
        exit 1
    fi
}

# 检查 Python 3.13 是否已安装
if command_exists python3.13; then
    PYTHON_VERSION=$(python3.13 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}Python 3.13 已安装: ${PYTHON_VERSION}${NC}"
else
    install_python_313
fi

# 验证 Python 版本
PYTHON_VERSION=$(python3.13 --version 2>&1 | cut -d' ' -f2)
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [[ $MAJOR_VERSION -eq 3 && $MINOR_VERSION -ge 13 ]]; then
    echo -e "${GREEN}✅ Python 版本验证通过: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}❌ Python 版本不符合要求 (需要 3.13+): ${PYTHON_VERSION}${NC}"
    exit 1
fi

# 创建虚拟环境
echo -e "${YELLOW}创建 Python 3.13 虚拟环境...${NC}"
if [[ -d "venv" ]]; then
    echo "删除旧的虚拟环境..."
    rm -rf venv
fi

python3.13 -m venv venv
source venv/bin/activate

# 升级 pip 和基础工具
echo -e "${YELLOW}升级 pip 和基础工具...${NC}"
pip install --upgrade pip setuptools wheel

# 安装 uv (更快的包管理器)
echo -e "${YELLOW}安装 uv 包管理器...${NC}"
pip install uv

# 使用 pip 安装依赖 (uv在某些包上有兼容性问题)
echo -e "${YELLOW}使用 pip 安装 Python 依赖...${NC}"
pip install -e . --verbose

# 验证关键包安装
echo -e "${YELLOW}验证关键包安装...${NC}"
python3.13 -c "
import sys
print(f'Python 版本: {sys.version}')

# 验证关键包
packages_to_check = [
    'torch', 'transformers', 'fastapi', 'numpy', 
    'pandas', 'opencv-python', 'openai', 'anthropic'
]

for package in packages_to_check:
    try:
        __import__(package)
        print(f'✅ {package} 安装成功')
    except ImportError as e:
        print(f'❌ {package} 安装失败: {e}')
"

# 创建 Python 3.13 配置文件
echo -e "${YELLOW}创建 Python 3.13 配置文件...${NC}"
cat > .python-version << EOF
3.13.0
EOF

# 更新 GitHub Actions 配置
if [[ -f ".github/workflows/ci.yml" ]]; then
    echo -e "${YELLOW}更新 GitHub Actions 配置...${NC}"
    sed -i.bak 's/python-version: .*/python-version: "3.13"/' .github/workflows/ci.yml
fi

# 创建 Dockerfile 更新
echo -e "${YELLOW}创建 Python 3.13 Dockerfile...${NC}"
cat > Dockerfile.python313 << EOF
# 索克生活 - Python 3.13 Docker 镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    build-essential \\
    cmake \\
    git \\
    libopencv-dev \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install uv

# 复制项目文件
COPY pyproject.toml ./
COPY README.md ./

# 安装 Python 依赖
RUN uv pip install --system -e .

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 创建开发环境配置
echo -e "${YELLOW}创建开发环境配置...${NC}"
cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.analysis.typeCheckingMode": "strict"
}
EOF

# 性能测试
echo -e "${YELLOW}运行 Python 3.13 性能测试...${NC}"
python3.13 -c "
import time
import sys

print(f'Python 版本: {sys.version}')
print(f'性能测试开始...')

# 测试基础性能
start_time = time.time()
result = sum(i**2 for i in range(1000000))
end_time = time.time()

print(f'计算性能测试: {end_time - start_time:.4f} 秒')
print(f'结果: {result}')

# 测试导入性能
start_time = time.time()
import numpy as np
import pandas as pd
end_time = time.time()

print(f'包导入性能: {end_time - start_time:.4f} 秒')
print('✅ Python 3.13 升级完成!')
"

echo -e "${GREEN}🎉 Python 3.13 升级完成!${NC}"
echo -e "${BLUE}主要改进:${NC}"
echo "  • 更好的错误消息和调试体验"
echo "  • 改进的性能和内存使用"
echo "  • 新的类型系统特性"
echo "  • 更好的异步支持"
echo "  • 实验性的 JIT 编译器"

echo -e "${YELLOW}下一步:${NC}"
echo "  1. 激活虚拟环境: source venv/bin/activate"
echo "  2. 运行测试: pytest"
echo "  3. 启动开发服务器: uvicorn src.main:app --reload"

echo -e "${GREEN}升级完成! 🚀${NC}" 