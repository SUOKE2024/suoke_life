# 使用 Python 3.13 官方镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DEBUG=false

# 安装系统依赖和 UV
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 将 UV 添加到 PATH
ENV PATH="/root/.cargo/bin:$PATH"

# 配置 UV 使用国内镜像源
ENV UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY soer_service/ ./soer_service/

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash soer
RUN chown -R soer:soer /app
USER soer

# 暴露端口
EXPOSE 8003

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# 启动命令
CMD ["uv", "run", "python", "-m", "soer_service.main"]