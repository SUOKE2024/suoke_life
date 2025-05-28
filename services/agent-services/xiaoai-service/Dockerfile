# 小艾智能体服务 Dockerfile
# XiaoAI Agent Service Dockerfile
# 
# 多阶段构建，优化镜像大小和安全性
# 支持开发和生产环境

# ===== 基础镜像 =====
FROM python:3.13.3-slim as base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 UV 包管理器
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 创建应用用户
RUN groupadd --gid 1000 xiaoai && \
    useradd --uid 1000 --gid xiaoai --shell /bin/bash --create-home xiaoai

# 设置工作目录
WORKDIR /app

# ===== 依赖安装阶段 =====
FROM base as dependencies

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen --no-dev

# ===== 开发环境 =====
FROM dependencies as development

# 安装开发依赖
RUN uv sync --frozen --extra dev --extra ai

# 复制源代码
COPY --chown=xiaoai:xiaoai . .

# 切换到应用用户
USER xiaoai

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uv", "run", "xiaoai-server", "--host", "0.0.0.0", "--port", "8000"]

# ===== 生产环境构建阶段 =====
FROM base as builder

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖
RUN uv sync --frozen --no-dev

# 复制源代码
COPY . .

# 构建项目
RUN uv build

# ===== 生产环境运行阶段 =====
FROM python:3.13.3-slim as production

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT=production

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建应用用户
RUN groupadd --gid 1000 xiaoai && \
    useradd --uid 1000 --gid xiaoai --shell /bin/bash --create-home xiaoai

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder --chown=xiaoai:xiaoai /app/.venv /app/.venv

# 从构建阶段复制构建产物
COPY --from=builder --chown=xiaoai:xiaoai /app/dist /app/dist

# 安装构建的包
RUN pip install --no-cache-dir /app/dist/*.whl

# 复制配置文件和脚本
COPY --chown=xiaoai:xiaoai config/ /app/config/
COPY --chown=xiaoai:xiaoai scripts/ /app/scripts/
COPY --chown=xiaoai:xiaoai env.example /app/.env.example

# 创建必要的目录
RUN mkdir -p /app/logs /app/data /app/temp /app/uploads && \
    chown -R xiaoai:xiaoai /app

# 切换到应用用户
USER xiaoai

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["xiaoai-server", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ===== 标签信息 =====
LABEL maintainer="Suoke Life Team <dev@suokelife.com>" \
      version="1.0.0" \
      description="小艾智能体服务 - 索克生活智能健康管理平台的核心AI智能体" \
      org.opencontainers.image.title="XiaoAI Agent Service" \
      org.opencontainers.image.description="小艾智能体服务 - 基于中医理论的智能健康管理" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Suoke Life" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/suokelife/suoke_life" \
      org.opencontainers.image.documentation="https://docs.suokelife.com/xiaoai" 