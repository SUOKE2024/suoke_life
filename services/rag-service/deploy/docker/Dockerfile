# 构建阶段
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# 复制项目文件
COPY pyproject.toml poetry.lock* ./

# 配置Poetry不创建虚拟环境
RUN poetry config virtualenvs.create false

# 安装依赖但不安装开发依赖
RUN poetry install --no-dev --no-interaction --no-ansi

# 多阶段构建：生产镜像
FROM python:3.12-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制依赖
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建缓存和日志目录
RUN mkdir -p /app/cache /app/logs && \
    chmod -R 755 /app/cache /app/logs

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/liveness || exit 1

# 暴露HTTP和gRPC端口
EXPOSE 8000 9000

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    GRPC_PORT=9000 \
    ENV=production \
    LOG_LEVEL=info

# 启动命令
CMD ["python", "-m", "services.rag_service.cmd.server"]