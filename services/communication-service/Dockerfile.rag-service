FROM python:3.13.3-slim as builder

# 设置工作目录
WORKDIR /app

# 环境变量设置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# 安装基础依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 构建最终镜像
FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 环境变量设置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    RAG_CONFIG_PATH=/app/config/default.yaml \
    MILVUS_HOST=milvus-service \
    CACHE_TYPE=local \
    GENERATOR_TYPE=openai \
    EMBEDDING_DEVICE=cpu \
    LLM_DEVICE=cpu

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN groupadd -r suoke && useradd -r -g suoke suoke

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/data/models && \
    chown -R suoke:suoke /app

# 从构建器镜像复制安装的Python包
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY --chown=suoke:suoke . /app/

# 创建健康检查脚本
RUN echo '#!/bin/sh\ncurl -f http://localhost:8000/api/v1/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# 切换到非root用户
USER suoke

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD [ "/healthcheck.sh" ]

# 暴露端口 - REST和gRPC
EXPOSE 8000 50051

# 运行应用
CMD ["python", "-m", "cmd.server.main"] 