# message-bus Dockerfile
FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY message_bus/ ./message_bus/

# 安装Python依赖
RUN uv sync --frozen

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "python", "-m", "message_bus.main"]
