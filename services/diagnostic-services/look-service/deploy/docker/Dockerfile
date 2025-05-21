FROM python:3.11-slim

LABEL maintainer="SuoKe Life <dev@suoke.com>"
LABEL description="Look Service for SuoKe Life APP"

# 设置工作目录
WORKDIR /app

# 设置Python环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# 拷贝依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p /app/data/images \
    && mkdir -p /app/data/analysis \
    && mkdir -p /app/logs \
    && mkdir -p /app/models/face_analyzer \
    && mkdir -p /app/models/body_analyzer

# 复制应用代码
COPY . .

# 创建非root用户
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露gRPC端口
EXPOSE 50053

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import grpc; from api.grpc import look_service_pb2, look_service_pb2_grpc; channel = grpc.insecure_channel('localhost:50053'); stub = look_service_pb2_grpc.LookServiceStub(channel); response = stub.HealthCheck(look_service_pb2.HealthCheckRequest()); exit(0 if response.status == 0 else 1)"

# 设置入口点
ENTRYPOINT ["python", "cmd/server.py"] 