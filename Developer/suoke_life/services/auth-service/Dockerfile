FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/node:18-alpine

# 添加标签
LABEL maintainer="索克生活技术团队 <tech@suoke.life>" \
      com.suoke.title="索克生活认证服务" \
      com.suoke.description="提供用户认证、授权和会话管理功能" \
      com.suoke.vendor="索克生活" \
      com.suoke.version="1.4.0" \
      com.suoke.url="https://auth.suoke.life" \
      com.suoke.source="https://gitlab.suoke.life/suoke/auth-service"

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
RUN npm ci --only=production && npm cache clean --force

# 复制应用程序代码
COPY . .

# 设置环境变量
ENV NODE_ENV=production \
    PORT=3001 \
    AUDIT_LOG_ENABLED=true \
    STRUCTURED_LOGGING=true \
    APP_ENCRYPTION_ENABLED=true \
    APP_HOST=0.0.0.0 \
    OTEL_ENABLED=true \
    OTEL_SERVICE_NAME=auth-service

# 创建必要的目录并设置权限
RUN mkdir -p /app/logs /app/dynamic-config /app/tmp \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app

# 切换到非root用户
USER appuser

# 暴露端口 (HTTP和指标端口)
EXPOSE 3001 9090

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# 定义卷
VOLUME ["/app/logs", "/app/dynamic-config", "/app/tmp"]

# 启动命令
CMD ["node", "server.js"] 