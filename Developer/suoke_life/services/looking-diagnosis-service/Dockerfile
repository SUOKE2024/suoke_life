# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM node:18-alpine

# 安装必要工具包
RUN apk add --no-cache bash curl jq netcat-openbsd tzdata

# 设置工作目录
WORKDIR /app

# 设置非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
    && mkdir -p /app/data /app/logs /app/uploads /app/temp \
    && chown -R appuser:appgroup /app

# 复制构建产物和生产依赖
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# 复制启动脚本
COPY scripts/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# 设置时区为亚洲/上海
ENV TZ=Asia/Shanghai

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 切换到非root用户
USER appuser

# 暴露应用端口
EXPOSE 3000

# 设置默认环境变量
ENV PORT=3000 \
    NODE_ENV=production \
    API_PREFIX=/api \
    DATA_DIR=/app/data \
    LOG_DIR=/app/logs \
    UPLOAD_DIR=/app/uploads \
    TEMP_DIR=/app/temp

# 设置入口点
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["node", "dist/main.js"] 