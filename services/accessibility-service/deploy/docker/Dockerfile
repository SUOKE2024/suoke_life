FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务代码
COPY . .

# 创建日志目录
RUN mkdir -p /var/log/accessibility-service

# 设置环境变量
ENV PYTHONPATH=/app
ENV ACCESSIBILITY_CONFIG_PATH=/app/config/config.yaml

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.socket().connect(('localhost', 50051))" || exit 1

# 开放端口
EXPOSE 50051

# 设置入口点
ENTRYPOINT ["python", "cmd/server/main.py"] 