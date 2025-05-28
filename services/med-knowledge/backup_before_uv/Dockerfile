# 索克生活-医学知识服务 Dockerfile
# 多阶段构建，优化镜像大小和安全性

# 第一阶段：构建阶段
FROM python:3.13.3-slim as builder

# 设置工作目录
WORKDIR /build

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装Python依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.13.3-slim as runtime

# 设置标签
LABEL maintainer="suoke-life-team"
LABEL version="1.0.0"
LABEL description="索克生活医学知识服务"

# 创建非root用户
RUN groupadd -r medknowledge && useradd -r -g medknowledge medknowledge

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 创建必要的目录
RUN mkdir -p /app/logs /app/data /app/config \
    && chown -R medknowledge:medknowledge /app

# 复制应用代码
COPY --chown=medknowledge:medknowledge . .

# 复制配置文件
COPY --chown=medknowledge:medknowledge config/ ./config/

# 设置权限
RUN chmod +x scripts/*.py

# 切换到非root用户
USER medknowledge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000 50051

# 设置入口点
ENTRYPOINT ["dumb-init", "--"]

# 默认命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 