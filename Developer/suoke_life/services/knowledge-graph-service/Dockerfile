# 构建阶段 - 使用官方标准镜像
FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/node:18-alpine as builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建TypeScript
RUN npm run build

# 生产阶段 - 使用官方标准镜像
FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/node:18-alpine

WORKDIR /app

# 设置标签
LABEL maintainer="SuoKe Platform Team <dev@suoke.life>" \
      org.opencontainers.image.title="Knowledge Graph Service" \
      org.opencontainers.image.description="索克生活平台知识图谱服务" \
      org.opencontainers.image.vendor="SuoKe Platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.url="https://suoke.life" \
      org.opencontainers.image.source="https://github.com/suoke-life/knowledge-graph-service"

# 复制package文件和构建产物
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist

# 只安装生产依赖
RUN npm ci --only=production && npm cache clean --force

# 创建非root用户
RUN addgroup -g 1000 appuser && \
    adduser -u 1000 -G appuser -s /bin/sh -D appuser

# 创建必要的目录并设置权限
RUN mkdir -p /app/data /app/models /app/tmp /app/logs && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 设置环境变量
ENV NODE_ENV=production \
    PORT=3000 \
    APP_HOST=0.0.0.0 \
    LOG_LEVEL=info \
    OTEL_SERVICE_NAME=knowledge-graph-service

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -q --spider http://localhost:3000/health/live || exit 1

# 暴露端口
EXPOSE 3000 9090

# 挂载卷
VOLUME ["/app/data", "/app/models", "/app/tmp"]

# 启动命令
CMD ["node", "dist/index.js"]