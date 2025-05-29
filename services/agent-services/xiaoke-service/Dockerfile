# 多阶段构建 Dockerfile

# 第1阶段：Python依赖构建
FROM python:3.13.3-slim AS builder

WORKDIR /app

# 安装系统依赖和 uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    git \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 将 uv 添加到 PATH
ENV PATH="/root/.cargo/bin:$PATH"

# 配置国内镜像源
ENV UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

# 复制项目配置文件
COPY pyproject.toml uv.lock* ./

# 使用 uv 安装依赖
RUN uv sync --frozen --no-dev --no-install-project

# 第2阶段：构建gRPC代码
FROM builder AS grpc-builder

WORKDIR /app

# 复制proto文件并生成Python代码
COPY api/grpc/ /app/api/grpc/
RUN mkdir -p /app/generated && \
    .venv/bin/python -m grpc_tools.protoc \
    --proto_path=/app/api/grpc \
    --python_out=/app/generated \
    --grpc_python_out=/app/generated \
    /app/api/grpc/*.proto

# 第3阶段：最终镜像
FROM python:3.13.3-slim

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

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 从构建阶段复制生成的gRPC代码
COPY --from=grpc-builder /app/generated /app/api/

# 复制应用代码
COPY xiaoke_service/ /app/xiaoke_service/
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
    LOG_DIR="/app/logs" \
    PATH="/app/.venv/bin:$PATH"

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