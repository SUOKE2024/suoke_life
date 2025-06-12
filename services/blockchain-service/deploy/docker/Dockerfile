# 索克生活区块链服务 Dockerfile
# 使用多阶段构建优化镜像大小

# 构建阶段
FROM python:3.13.3-slim as builder

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 UV
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY suoke_blockchain_service/ ./suoke_blockchain_service/

# 安装依赖并构建
RUN uv sync --frozen --no-dev
RUN uv build

# 运行阶段
FROM python:3.13.3-slim as runtime

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 创建非 root 用户
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 安装 UV
RUN pip install uv

# 复制构建产物
COPY --from=builder /app/dist/*.whl ./
COPY --from=builder /app/pyproject.toml /app/uv.lock ./

# 创建虚拟环境并安装应用
RUN uv venv && \
    uv pip install *.whl

# 复制配置文件
COPY config/ ./config/
COPY alembic.ini ./

# 创建必要的目录
RUN mkdir -p logs data && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 暴露端口
EXPOSE 50055 8080 9090

# 启动命令
CMD ["uv", "run", "python", "-m", "suoke_blockchain_service.main", "serve"]

# 元数据标签
LABEL maintainer="SuoKe Life Team <dev@suoke.life>" \
      version="0.1.0" \
      description="索克生活区块链服务" \
      org.opencontainers.image.title="SuoKe Blockchain Service" \
      org.opencontainers.image.description="健康数据的区块链存储、验证和访问控制" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.vendor="SuoKe Life" \
      org.opencontainers.image.licenses="Proprietary" 