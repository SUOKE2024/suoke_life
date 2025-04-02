#!/bin/bash
# RAG服务依赖安装脚本
# 用于在开发环境或CI/CD流程中快速安装所需依赖

set -e

echo "开始安装RAG服务依赖..."

# 系统依赖
if command -v apt-get &> /dev/null; then
    echo "使用apt安装系统依赖..."
    apt-get update
    apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        gcc \
        g++ \
        git \
        netcat \
        wget \
        unzip
elif command -v yum &> /dev/null; then
    echo "使用yum安装系统依赖..."
    yum update -y
    yum install -y \
        curl \
        python3-devel \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        gcc \
        gcc-c++ \
        git \
        nmap-ncat \
        wget \
        unzip
elif command -v brew &> /dev/null; then
    echo "使用Homebrew安装系统依赖..."
    brew update
    brew install \
        python@3.9 \
        gcc \
        netcat \
        wget
else
    echo "未检测到支持的包管理器，请手动安装依赖"
    exit 1
fi

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 安装开发依赖
if [ "$1" == "--dev" ]; then
    echo "安装开发依赖..."
    pip install -r requirements-dev.txt
    
    # 安装预提交钩子
    pre-commit install
    
    echo "设置开发环境..."
    cp .env.example .env
    echo "请编辑.env文件以配置您的开发环境"
fi

# 验证核心依赖
echo "验证依赖安装..."
python -c "import fastapi; print(f'FastAPI版本: {fastapi.__version__}')"
python -c "import qdrant_client; print(f'Qdrant客户端版本: {qdrant_client.__version__}')"
python -c "import neo4j; print(f'Neo4j客户端版本: {neo4j.__version__}')"
python -c "import redis; print(f'Redis客户端版本: {redis.__version__}')"
python -c "import opentelemetry; print(f'OpenTelemetry版本: {opentelemetry.__version__}')"

echo "依赖安装完成!"
echo "要激活虚拟环境，请运行: source venv/bin/activate"

if [ "$1" != "--dev" ]; then
    echo "提示: 添加--dev参数以安装开发依赖和设置开发环境"
fi