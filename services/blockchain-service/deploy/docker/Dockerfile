FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 多阶段构建，使用更小的基础镜像
FROM python:3.9-slim

# 创建非root用户
RUN groupadd -g 1000 blockchain && \
    useradd -u 1000 -g blockchain -s /bin/bash blockchain

# 设置工作目录
WORKDIR /app

# 从builder阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY . .

# 设置日志目录并赋予权限
RUN mkdir -p /app/logs && \
    chown -R blockchain:blockchain /app

# 切换到非root用户
USER blockchain

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CONFIG_FILE="/app/config/prod.yaml"

# 暴露gRPC端口
EXPOSE 50055

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.connect(('localhost', 50055))" || exit 1

# 启动服务
CMD ["python", "-m", "cmd.server.main"] 