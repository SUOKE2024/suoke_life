# 医疗资源微服务 Dockerfile
FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖和 UV
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 使用 UV 安装 Python 依赖（使用国内镜像）
RUN uv sync --frozen --no-dev --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs data

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9084/health || exit 1

# 暴露端口
EXPOSE 9084

# 启动命令
CMD ["uv", "run", "python", "-m", "cmd.server.main"] 