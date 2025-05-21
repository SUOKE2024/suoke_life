# 使用Python官方镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置Python环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建非root用户
RUN useradd -m appuser

# 复制应用程序代码
COPY . .

# 确保日志目录存在并设置权限
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# 切换到非root用户
USER appuser

# 设置环境变量，可以在运行时覆盖
ENV LOG_LEVEL=info \
    LOG_FORMAT=json \
    LOG_OUTPUT=stdout

# 暴露端口
EXPOSE 50051 8080 9090

# 运行应用
CMD ["python", "cmd/server/main.py", "--config", "config/config.yaml"] 