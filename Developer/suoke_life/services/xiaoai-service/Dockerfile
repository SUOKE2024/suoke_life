FROM node:18-alpine

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制构建好的应用
COPY dist/ ./dist/

# 设置环境变量
ENV NODE_ENV=production

# 创建非root用户并设置权限
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser && \
    mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 3040

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3040/health || exit 1

# 运行应用
CMD ["node", "dist/index.js"]