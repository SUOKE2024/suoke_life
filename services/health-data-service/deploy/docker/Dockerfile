# 多阶段构建的健康数据服务Docker镜像

# 第一阶段：构建阶段
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖管理工具
RUN pip install --no-cache-dir poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 配置Poetry
RUN poetry config virtualenvs.create false

# 安装Python依赖
RUN poetry install --no-dev --no-interaction --no-ansi

# 第二阶段：运行阶段
FROM python:3.11-slim as runtime

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从构建阶段复制Python环境
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY health_data_service/ ./health_data_service/
COPY alembic.ini ./
COPY migrations/ ./migrations/

# 创建必要的目录
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD ["python", "-m", "health_data_service.api.main"] 