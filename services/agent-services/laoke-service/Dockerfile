# 老克智能体服务 Dockerfile
# 基于 Python 3.13 官方镜像

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

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY laoke_service/ ./laoke_service/
COPY config/ ./config/
COPY scripts/ ./scripts/

# 创建虚拟环境并安装依赖
RUN uv venv --python 3.13 && \
    uv sync --extra performance --extra monitoring

# 创建非root用户
RUN useradd --create-home --shell /bin/bash laoke && \
    chown -R laoke:laoke /app
USER laoke

# 创建必要的目录
RUN mkdir -p logs data

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 暴露端口
EXPOSE 8080 50051 9091

# 设置入口点
ENTRYPOINT ["uv", "run"]
CMD ["laoke-server", "--host", "0.0.0.0", "--port", "8080"]

# 多阶段构建 - 开发环境
FROM base as development

# 安装开发依赖
RUN uv sync --extra dev --extra performance --extra monitoring

# 开发环境命令
CMD ["laoke-server", "--host", "0.0.0.0", "--port", "8080", "--reload", "--log-level", "debug"]

# 多阶段构建 - 生产环境
FROM base as production

# 生产环境优化
ENV ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=info

# 生产环境命令
CMD ["laoke-server", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"] 