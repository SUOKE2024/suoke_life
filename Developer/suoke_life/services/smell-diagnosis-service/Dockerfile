FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 编译TypeScript
RUN npm run build

# 生产阶段
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN addgroup -g 1000 suoke && \
    adduser -u 1000 -G suoke -s /bin/sh -D suoke && \
    mkdir -p /app/logs /app/dist /tmp/uploads && \
    chown -R suoke:suoke /app /tmp/uploads

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装生产依赖
RUN npm ci --only=production && \
    npm cache clean --force && \
    rm -rf /root/.npm

# 安装监控工具
RUN npm install -g prom-client@14.0.1 opentelemetry-js@1.8.0

# 从builder阶段复制编译后的代码
COPY --from=builder --chown=suoke:suoke /app/dist ./dist

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3002/health || exit 1

# 设置环境变量
ENV NODE_ENV=production \
    PORT=3002 \
    METRICS_PORT=9464 \
    METRICS_PATH=/metrics

# 切换到非root用户
USER suoke

# 暴露端口
EXPOSE 3002 9464

# 启动服务
CMD ["node", "dist/server.js"] 