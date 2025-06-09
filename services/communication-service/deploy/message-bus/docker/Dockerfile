FROM python:3.13.3-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装依赖到指定目录
RUN pip install --no-cache-dir --user -r requirements.txt

# 开发阶段
FROM python:3.13.3-slim AS development

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=development

# 设置工作目录
WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local

# 把Python用户基础路径添加到环境变量中
ENV PATH=/root/.local/bin:$PATH

# 复制项目文件
COPY . .

# 创建非root用户
RUN groupadd -r sokelife && useradd -r -g sokelife sokelife \
    && mkdir -p /app/logs \
    && chown -R sokelife:sokelife /app/logs

# 暴露端口
EXPOSE 50051 9090

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; import sys; from api.grpc.message_bus_pb2_grpc import MessageBusServiceStub; from api.grpc.message_bus_pb2 import HealthCheckRequest; channel = grpc.insecure_channel('localhost:50051'); stub = MessageBusServiceStub(channel); response = stub.HealthCheck(HealthCheckRequest()); sys.exit(0 if response.status == 1 else 1)"

# 使用非root用户运行
USER sokelife

# 启动命令
CMD ["python", "cmd/server/main.py"]

# 生产阶段
FROM python:3.13.3-slim AS production

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

# 设置工作目录
WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local

# 把Python用户基础路径添加到环境变量中
ENV PATH=/root/.local/bin:$PATH

# 只复制需要的文件
COPY api/ /app/api/
COPY config/ /app/config/
COPY internal/ /app/internal/
COPY cmd/ /app/cmd/
COPY pkg/ /app/pkg/

# 创建日志目录
RUN mkdir -p /app/logs

# 创建必要的证书目录
RUN mkdir -p /etc/sokelife/certs/message-bus /etc/sokelife/certs/jwt

# 创建非root用户
RUN groupadd -r sokelife && useradd -r -g sokelife sokelife \
    && chown -R sokelife:sokelife /app/logs

# 安全加固
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 暴露端口
EXPOSE 50051 9090

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; import sys; from api.grpc.message_bus_pb2_grpc import MessageBusServiceStub; from api.grpc.message_bus_pb2 import HealthCheckRequest; channel = grpc.insecure_channel('localhost:50051'); stub = MessageBusServiceStub(channel); response = stub.HealthCheck(HealthCheckRequest()); sys.exit(0 if response.status == 1 else 1)"

# 使用非root用户运行
USER sokelife

# 启动命令
CMD ["python", "cmd/server/main.py"] 