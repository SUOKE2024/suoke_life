# A2A 智能体网络微服务 Dockerfile
# 使用 Python 3.13.3 和 UV 包管理器

FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_LINK_MODE=copy

# 安装系统依赖和 UV
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.cargo/bin/uv /usr/local/bin/ \
    && rm -rf /var/lib/apt/lists/*

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖
RUN uv venv /app/.venv \
    && uv pip install --no-cache -r pyproject.toml

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs config

# 设置权限
RUN chmod +x app/server/main.py

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 暴露端口
EXPOSE 5000 5001

# 激活虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

# 启动命令
CMD ["python", "app/server/main.py"] 