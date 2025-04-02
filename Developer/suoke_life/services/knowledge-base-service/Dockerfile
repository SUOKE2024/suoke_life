# 使用官方Node.js镜像作为基础镜像
FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段使用轻量级镜像
FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/node:18-alpine

# 设置标签
LABEL maintainer="SuoKe Platform Team <dev@suoke.life>" \
      org.opencontainers.image.title="Knowledge Base Service" \
      org.opencontainers.image.description="索克生活平台知识库服务" \
      org.opencontainers.image.vendor="SuoKe Platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.url="https://suoke.life" \
      org.opencontainers.image.source="https://github.com/suoke-life/knowledge-base-service"

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 仅安装生产依赖
RUN npm ci --only=production && npm cache clean --force

# 从构建阶段复制编译后的代码
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/config ./config

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/tmp && \
    chown -R node:node /app

# 设置环境变量
ENV NODE_ENV=production \
    PORT=3002 \
    APP_HOST=0.0.0.0 \
    LOG_LEVEL=info \
    OTEL_SERVICE_NAME=knowledge-base-service

# 暴露端口
EXPOSE 3002 9090

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3002/health || exit 1

# 使用非root用户
USER node

# 挂载卷
VOLUME ["/app/data", "/app/logs", "/app/tmp"]

# 启动应用
CMD ["node", "dist/server.js"]