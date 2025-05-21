# 使用多阶段构建减少最终镜像大小
# 构建阶段
FROM python:3.10-slim as builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行阶段
FROM python:3.10-slim

# 设置时区为上海
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 创建非root用户
RUN groupadd -r soer && useradd -r -g soer soer

# 设置工作目录
WORKDIR /app

# 从构建阶段复制安装好的Python包
COPY --from=builder /root/.local /home/soer/.local
ENV PATH=/home/soer/.local/bin:$PATH

# 复制应用程序代码
COPY . .

# 创建必要的目录并设置权限
RUN mkdir -p logs \
    && chown -R soer:soer /app \
    && chmod -R 755 /app

# 切换到非root用户
USER soer

# 设置Python环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8054/health || exit 1

# 暴露gRPC和REST API端口
EXPOSE 50054 8054 9098

# 启动命令
CMD ["python", "-m", "cmd.server"]