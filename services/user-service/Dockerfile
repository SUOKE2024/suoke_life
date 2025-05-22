FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p /data

# 设置环境变量
ENV USER_SERVICE_DB_PATH=/data/users.db \
    USER_SERVICE_REST_PORT=8000 \
    USER_SERVICE_GRPC_PORT=50051 \
    USER_SERVICE_DEBUG=false \
    PYTHONPATH=/app

# 暴露端口
EXPOSE 8000 50051

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
CMD ["python", "cmd/server/main.py"] 