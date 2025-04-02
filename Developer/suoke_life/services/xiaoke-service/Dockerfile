FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force

COPY --from=builder /app/dist ./dist
COPY docker-entrypoint.sh /usr/local/bin/

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs /app/cache /app/config /app/models && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# 复制配置文件
COPY ./config /app/config

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3011/health || exit 1

# 设置非root用户
RUN addgroup -g 1001 -S xiaoke && \
    adduser -u 1001 -S xiaoke -G xiaoke && \
    chown -R xiaoke:xiaoke /app
USER xiaoke

# 暴露端口
EXPOSE 3011
EXPOSE 9464
EXPOSE 3012

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node", "dist/index.js"] 