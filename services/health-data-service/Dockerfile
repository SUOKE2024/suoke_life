FROM python:3.13.3-slim-bullseye

LABEL maintainer="SUOKE Health Data Service Team"
LABEL description="索克生活健康数据服务"
LABEL version="1.0.0"

# 设置工作目录
WORKDIR /app

# 设置Python环境
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONPATH="/app:${PYTHONPATH}"

# 安装系统依赖和UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 将UV添加到PATH
ENV PATH="/root/.cargo/bin:$PATH"

# 创建非root用户
RUN groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser appuser

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建目录并设置权限
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app/logs /app/data

# 切换到非root用户
USER appuser

# 指定健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 设置默认配置文件
ENV CONFIG_PATH=/app/config/default.yaml
ENV LOG_LEVEL=INFO

# 暴露端口
EXPOSE 8080 50051 9180

# 启动命令
ENTRYPOINT ["uv", "run", "health-data-service", "serve"]
CMD ["--config", "${CONFIG_PATH}"] 