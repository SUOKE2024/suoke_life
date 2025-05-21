FROM python:3.9-slim

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=pypi.org

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY .env .
COPY cmd ./cmd
COPY config ./config
COPY data ./data
COPY internal ./internal
COPY api ./api

# 使用指定的镜像源安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt \
    --index-url ${PIP_INDEX_URL} \
    --trusted-host ${PIP_TRUSTED_HOST}

# 创建必要的目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONPATH=/app

# 设置默认为模拟模式
ENV USE_MOCK_MODE=true
ENV MOCK_EXTERNAL_SERVICES=true
ENV SERVICE_ENV=development

# 启动服务
CMD ["python", "cmd/server.py"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket, sys; \
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); \
    s.connect(('localhost', 50052)) or sys.exit(1); \
    s.close()"