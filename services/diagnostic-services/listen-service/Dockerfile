# 标准化的多阶段构建Dockerfile - 使用UV包管理器
# 构建阶段
FROM python:3.13.3-slim AS builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目配置文件
COPY pyproject.toml uv.lock* ./

# 创建虚拟环境并安装依赖
RUN uv venv && \
    uv pip install -e .

# 运行阶段
FROM python:3.13.3-slim AS runtime

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# 创建非root用户
RUN groupadd -r suoke && useradd -r -g suoke -d /app -s /bin/bash suoke

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用代码
COPY --chown=suoke:suoke . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/data /app/cache && \
    chown -R suoke:suoke /app

# 切换到非root用户
USER suoke

# 暴露端口 (统一端口规范)
EXPOSE 8080 50051

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
