# 索克生活人工审核微服务 Dockerfile
# Human Review Service Dockerfile

# 使用Python 3.13官方镜像作为基础镜像
FROM python:3.13-slim

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
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 复制项目配置文件
COPY pyproject.toml ./

# 创建虚拟环境并安装依赖
RUN uv venv .venv
RUN uv pip install -e .

# 复制应用代码
COPY human_review_service/ ./human_review_service/

# 创建必要的目录
RUN mkdir -p logs uploads

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# 切换到非root用户
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD [".venv/bin/python", "-m", "human_review_service.cli.main", "serve", "--host", "0.0.0.0", "--port", "8000"] 