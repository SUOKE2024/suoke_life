# 索克生活触诊服务 Dockerfile
# 多阶段构建，遵循 Python 项目最佳实践

# ============================================================================
# 基础镜像阶段
# ============================================================================
FROM python:3.13.3-slim-bookworm AS base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安装 UV
RUN pip install uv==0.6.16

# 创建应用用户
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# 设置工作目录
WORKDIR /app

# ============================================================================
# 依赖安装阶段
# ============================================================================
FROM base AS deps

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖到虚拟环境
RUN uv sync --frozen --no-dev --no-install-project

# ============================================================================
# 开发阶段
# ============================================================================
FROM deps AS development

# 安装开发依赖
RUN uv sync --frozen --extra dev --extra test --extra docs

# 复制源代码
COPY . .

# 安装项目
RUN uv sync --frozen

# 切换到应用用户
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uv", "run", "palpation-service", "serve", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# 生产阶段
# ============================================================================
FROM base AS production

# 安装生产系统依赖
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    libpq5 \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 从依赖阶段复制虚拟环境
COPY --from=deps /app/.venv /app/.venv

# 复制源代码
COPY . .

# 安装项目（仅生产依赖）
RUN uv sync --frozen --no-dev --no-install-project && \
    uv pip install -e .

# 创建必要的目录
RUN mkdir -p logs config data && \
    chown -R app:app /app

# 切换到应用用户
USER app

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uv", "run", "palpation-service", "serve", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# 测试阶段
# ============================================================================
FROM development AS test

# 运行测试
RUN uv run pytest --cov=palpation_service --cov-report=xml

# ============================================================================
# 构建信息
# ============================================================================
LABEL maintainer="Suoke Life Team <dev@suoke.life>" \
      version="1.0.0" \
      description="索克生活触诊服务 - 基于AI的中医触诊智能分析微服务" \
      org.opencontainers.image.title="palpation-service" \
      org.opencontainers.image.description="索克生活触诊服务" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Suoke Life" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/SUOKE2024/suoke_life" 