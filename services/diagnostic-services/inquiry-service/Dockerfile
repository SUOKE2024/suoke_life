# 多阶段构建 Dockerfile for Inquiry Service
# 使用 Python 3.13.3 和 UV 进行现代化构建

# 构建阶段
FROM python:3.13.3-slim as builder

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# 安装系统依赖和 UV
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 将 UV 添加到 PATH
ENV PATH="/root/.cargo/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装依赖到虚拟环境
RUN uv sync --frozen --no-dev

# 复制源代码
COPY inquiry_service/ ./inquiry_service/
COPY README.md ./

# 构建项目
RUN uv build

# 运行阶段
FROM python:3.13.3-slim as runtime

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境和构建产物
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/dist /app/dist

# 复制配置文件
COPY --chown=app:app config/ ./config/
COPY --chown=app:app data/ ./data/

# 安装构建的包
RUN /app/.venv/bin/pip install /app/dist/*.whl

# 切换到应用用户
USER app

# 创建必要的目录
RUN mkdir -p logs temp

# 暴露端口
EXPOSE 50052 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 设置启动命令
CMD ["inquiry-service"] 