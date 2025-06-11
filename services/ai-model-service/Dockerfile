# AI Model Service Dockerfile
# 基于Python 3.13.3官方镜像
FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装Python依赖
RUN uv sync --frozen --no-dev

# 复制源代码
COPY src/ ./src/
COPY config/ ./config/

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health/live || exit 1

# 暴露端口
EXPOSE 8080 9090

# 启动命令
CMD ["uv", "run", "python", "-m", "ai_model_service.main"] 