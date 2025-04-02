FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache curl tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 复制package.json和package-lock.json
COPY package*.json ./

# 以安全方式安装依赖
RUN npm ci --only=production

# 复制应用程序代码
COPY . .

# 设置环境变量
ENV NODE_ENV=production \
    PORT=3002 \
    AUDIT_LOG_ENABLED=true \
    STRUCTURED_LOGGING=true \
    DATA_PRIVACY_ENABLED=true

# 创建必要的目录并设置权限
RUN mkdir -p /app/logs /app/dynamic-config /app/uploads \
    && chown -R appuser:appgroup /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 3002

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3002/health || exit 1

# 启动命令
CMD ["node", "server.js"] 