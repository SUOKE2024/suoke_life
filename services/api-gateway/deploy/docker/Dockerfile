FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CONFIG_PATH=/app/config/config.yaml \
    LOGGING_FILE=/app/logs/api_gateway.log \
    LOG_LEVEL=INFO

# 创建非 root 用户和组
RUN groupadd -r suoke -g 1000 && \
    useradd -u 1000 -r -g suoke -s /bin/bash -c "Suoke User" suoke

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建日志目录并设置正确的权限
RUN mkdir -p /app/logs && \
    chown -R suoke:suoke /app/logs

# 复制项目文件
COPY . .
RUN chmod +x /app/scripts/start_service.sh && \
    chown -R suoke:suoke /app

# 切换到非 root 用户
USER suoke

# 暴露端口（REST和gRPC）
EXPOSE 8080 50050

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 设置入口点
ENTRYPOINT ["/app/scripts/start_service.sh"] 