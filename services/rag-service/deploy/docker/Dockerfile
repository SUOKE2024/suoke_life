# 多阶段构建的RAG服务Docker镜像
# 用于索克生活RAG服务的容器化部署

# ================================
# 基础镜像阶段
# ================================
FROM python:3.13.3-slim as base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN groupadd -r rag && useradd -r -g rag rag

# 创建应用目录
WORKDIR /app

# ================================
# 依赖安装阶段
# ================================
FROM base as dependencies

# 复制依赖文件
COPY pyproject.toml requirements.txt* ./

# 安装Python依赖
RUN pip install --upgrade pip setuptools wheel && \
    if [ -f pyproject.toml ]; then \
        pip install -e .; \
    elif [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    fi

# ================================
# 开发环境阶段
# ================================
FROM dependencies as development

# 安装开发依赖
RUN pip install \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy \
    pre-commit

# 复制源代码
COPY . .

# 设置权限
RUN chown -R rag:rag /app

# 切换到应用用户
USER rag

# 暴露端口
EXPOSE 8080 50051

# 启动命令
CMD ["python", "cmd/server/main.py"]

# ================================
# 生产环境阶段
# ================================
FROM dependencies as production

# 复制源代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs data cache tmp && \
    chown -R rag:rag /app

# 切换到应用用户
USER rag

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 暴露端口
EXPOSE 8080 50051

# 启动命令
CMD ["python", "cmd/server/main.py"]

# ================================
# 测试阶段
# ================================
FROM development as test

# 运行测试
RUN python -m pytest test/ -v --cov=internal --cov-report=html

# ================================
# 最终阶段（默认为生产环境）
# ================================
FROM production as final

# 元数据标签
LABEL maintainer="Suoke Life Team <dev@suokelife.com>" \
      version="1.2.0" \
      description="索克生活RAG服务 - 中医智能检索增强生成服务" \
      org.opencontainers.image.title="Suoke Life RAG Service" \
      org.opencontainers.image.description="中医智能检索增强生成服务" \
      org.opencontainers.image.version="1.2.0" \
      org.opencontainers.image.vendor="Suoke Life" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/suokelife/suoke_life"