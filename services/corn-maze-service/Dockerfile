# Corn Maze Service Dockerfile
# 索克生活迷宫探索微服务容器化配置

# 使用官方 Python 3.13 镜像作为基础镜像
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

# 安装 UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev

# 复制源代码
COPY corn_maze_service/ ./corn_maze_service/
COPY scripts/ ./scripts/

# 创建必要的目录
RUN mkdir -p data logs

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 50057 51057 51058

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:51057/health || exit 1

# 启动命令
CMD ["uv", "run", "python", "-m", "corn_maze_service.cmd.server.main"]

# 多阶段构建 - 开发镜像
FROM base as development

# 安装开发依赖
RUN uv sync --frozen

# 开发环境配置
ENV ENVIRONMENT=development \
    DEBUG=true \
    HTTP__RELOAD=true

# 多阶段构建 - 生产镜像
FROM base as production

# 生产环境配置
ENV ENVIRONMENT=production \
    DEBUG=false \
    HTTP__RELOAD=false

# 设置标签
LABEL maintainer="Suoke Life Team <dev@suokelife.com>" \
      version="0.2.0" \
      description="Corn Maze Service - 索克生活迷宫探索微服务" \
      org.opencontainers.image.source="https://github.com/suokelife/suoke_life" \
      org.opencontainers.image.documentation="https://docs.suokelife.com/services/corn-maze" \
      org.opencontainers.image.vendor="Suoke Life Team"