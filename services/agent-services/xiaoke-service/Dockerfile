# 多阶段构建 Dockerfile

# 第1阶段：Python依赖构建
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel setuptools && \
    pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt

# 第2阶段：构建gRPC代码
FROM builder AS grpc-builder

WORKDIR /app

# 复制proto文件并生成Python代码
COPY api/grpc/ /app/api/grpc/
RUN mkdir -p /app/generated && \
    python -m grpc_tools.protoc \
    --proto_path=/app/api/grpc \
    --python_out=/app/generated \
    --grpc_python_out=/app/generated \
    /app/api/grpc/*.proto

# 第3阶段：最终镜像
FROM python:3.12-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN addgroup --system xiaoke && \
    adduser --system --ingroup xiaoke xiaoke

# 从构建阶段复制依赖包
COPY --from=builder /app/wheels /app/wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /app/wheels/* && \
    rm -rf /app/wheels

# 从构建阶段复制生成的gRPC代码
COPY --from=grpc-builder /app/generated /app/api/

# 复制应用代码
COPY config/ /app/config/
COPY internal/ /app/internal/
COPY pkg/ /app/pkg/
COPY cmd/ /app/cmd/
COPY api/grpc/ /app/api/grpc/
COPY integration/ /app/integration/

# 创建必要的目录结构
RUN mkdir -p /app/logs /app/data && \
    chown -R xiaoke:xiaoke /app

# 设置环境变量
ENV PYTHONPATH="/app:${PYTHONPATH}" \
    PYTHONUNBUFFERED=1 \
    SERVICE_ENV=production \
    SERVICE_VERSION="1.0.0" \
    GRPC_PORT="50054" \
    MONITORING_PORT="51054" \
    LOG_DIR="/app/logs"

# 切换到非root用户
USER xiaoke

# 健康检查 - 使用HTTP健康检查而不是直接的socket检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${MONITORING_PORT}/health || exit 1

# 暴露服务端口
EXPOSE 50054
EXPOSE 51054

# 启动服务
CMD ["python", "-m", "cmd.server"]