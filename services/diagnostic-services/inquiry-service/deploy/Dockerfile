# 多阶段构建 - 构建阶段
FROM python:3.13.3-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY internal/ ./internal/
COPY proto/ ./proto/
COPY config/ ./config/
COPY data/ ./data/

# 创建虚拟环境并安装依赖
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -r pyproject.toml

# 生成protobuf文件
RUN python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/*.proto

# 运行阶段
FROM python:3.13.3-slim as runtime

# 创建非root用户
RUN groupadd -r inquiry && useradd -r -g inquiry inquiry

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY --from=builder /app/src ./src
COPY --from=builder /app/internal ./internal
COPY --from=builder /app/proto ./proto
COPY --from=builder /app/config ./config
COPY --from=builder /app/data ./data

# 复制启动脚本
COPY deploy/entrypoint.sh ./
COPY start_server.py ./

# 创建必要的目录
RUN mkdir -p logs && \
    chown -R inquiry:inquiry /app

# 设置权限
RUN chmod +x entrypoint.sh

# 切换到非root用户
USER inquiry

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 暴露端口
EXPOSE 8080 50051 9090

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# 启动命令
ENTRYPOINT ["./entrypoint.sh"]
CMD ["both"] 