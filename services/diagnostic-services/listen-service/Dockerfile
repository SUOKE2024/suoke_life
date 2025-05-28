# 多阶段构建，优化镜像大小
# 基础构建阶段
FROM python:3.13.3-slim as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 最终运行镜像
FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 复制必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/models /var/log/listen_service /tmp/listen_service

# 设置环境变量
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config/config.yaml

# 非root用户运行
RUN groupadd -r listenservice && useradd -r -g listenservice listenservice
RUN chown -R listenservice:listenservice /app /var/log/listen_service /tmp/listen_service
USER listenservice

# 暴露gRPC和Prometheus端口
EXPOSE 50052 9090

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import grpc; channel = grpc.insecure_channel('localhost:50052'); stub = grpc.health.v1.health_pb2_grpc.HealthStub(channel); response = stub.Check(grpc.health.v1.health_pb2.HealthCheckRequest(service='listen_service.ListenService')); exit(0 if response.status == grpc.health.v1.health_pb2.HealthCheckResponse.SERVING else 1)" || exit 1

# 启动服务
CMD ["python", "cmd/server.py"] 