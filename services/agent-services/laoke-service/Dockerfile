# 多阶段构建 Dockerfile

# 第1阶段：Python依赖构建
FROM python:3.12-slim AS builder

# 设置构建参数
ARG APP_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.4.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry==${POETRY_VERSION}

# 复制项目元数据
COPY pyproject.toml poetry.lock* ./

# 安装项目依赖
RUN poetry install --no-dev --no-interaction --no-ansi

# 第2阶段：构建GraphQL和gRPC代码
FROM builder AS schema-builder

WORKDIR /app

# 复制GraphQL schema文件并生成Python代码
COPY api/graphql/ /app/api/graphql/
RUN mkdir -p /app/generated/graphql

# 复制proto文件并生成Python代码（用于内部服务通信）
COPY api/grpc/ /app/api/grpc/
RUN mkdir -p /app/generated/grpc && \
    python -m grpc_tools.protoc \
    --proto_path=/app/api/grpc \
    --python_out=/app/generated/grpc \
    --grpc_python_out=/app/generated/grpc \
    /app/api/grpc/*.proto

# 第二阶段 - 最终镜像
FROM python:3.12-slim

# 设置运行时环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    SERVICE_ENV=production

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/logs

# 从构建器阶段复制依赖
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY . .

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/v1/health/status || exit 1

# 创建非特权用户
RUN groupadd -r laoke && useradd -r -g laoke laoke \
    && chown -R laoke:laoke /app/logs

# 切换到非特权用户
USER laoke

# 暴露端口
EXPOSE 8080 50051 51051

# 启动服务
CMD ["python", "-m", "cmd.server"] 