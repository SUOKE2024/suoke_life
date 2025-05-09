FROM node:18-alpine

# 元数据
LABEL maintainer="索克生活APP开发组"
LABEL version="1.0.0"
LABEL description="索克生活APP RAG向量检索服务"

# 创建工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production && \
    # 安装RAG服务特有依赖
    npm install @pinecone-database/pinecone@latest hnswlib-node@latest

# 复制源代码
COPY src/ ./src/
COPY config/ ./config/

# 创建向量存储目录
RUN mkdir -p /data/vectors && \
    chown -R node:node /data

# 使用非root用户运行
USER node

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8082/health || exit 1

# 暴露端口
EXPOSE 8082

# 挂载点
VOLUME ["/data"]

# 启动命令
CMD ["node", "src/server.js"] 