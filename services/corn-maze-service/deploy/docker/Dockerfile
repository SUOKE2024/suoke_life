FROM python:3.12-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app

# 创建必要的目录并设置权限
RUN mkdir -p /app/data /app/logs \
    && chown -R appuser:appuser /app/data /app/logs

# 切换到非root用户
USER appuser

# 暴露gRPC端口和指标端口
EXPOSE 50057 51057 51058

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:51058/health || exit 1

# 启动命令
CMD ["python", "cmd/server/main.py"] 