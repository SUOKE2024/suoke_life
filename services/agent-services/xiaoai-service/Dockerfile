# 小艾智能体生产环境Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 安装Python依赖
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-dev

# 复制应用代码
COPY xiaoai/ ./xiaoai/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# 创建非root用户
RUN groupadd -r xiaoai && useradd -r -g xiaoai xiaoai
RUN chown -R xiaoai:xiaoai /app
USER xiaoai

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000 50051

# 启动命令
CMD ["python", "-m", "xiaoai.main"]