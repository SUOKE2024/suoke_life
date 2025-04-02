# 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 配置NPM镜像
RUN npm config set registry https://registry.npmmirror.com

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 如果有构建步骤，在这里执行（例如TypeScript编译）
RUN if [ -f "tsconfig.json" ]; then \
      npm install -g typescript && \
      npm run build; \
    fi

# 运行阶段
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 安装必要的工具，但保持镜像小
RUN apk --no-cache add curl jq tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

# 创建非root用户
RUN addgroup -g 1000 nodeapp && \
    adduser -u 1000 -G nodeapp -s /bin/sh -D nodeapp && \
    mkdir -p /app/logs /app/config /vault/secrets && \
    chown -R nodeapp:nodeapp /app /vault/secrets

# 从构建阶段复制文件
COPY --from=builder --chown=nodeapp:nodeapp /app/node_modules /app/node_modules
COPY --from=builder --chown=nodeapp:nodeapp /app/package.json /app/
COPY --from=builder --chown=nodeapp:nodeapp /app/dist /app/dist
COPY --from=builder --chown=nodeapp:nodeapp /app/config /app/config

# 创建卷挂载点
VOLUME ["/app/logs", "/app/config", "/vault/secrets"]

# 切换到非root用户
USER nodeapp

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000/health/live || exit 1

# 设置环境变量
ENV NODE_ENV=production \
    TZ=Asia/Shanghai \
    PORT=3000 \
    HOST=0.0.0.0 \
    LOG_LEVEL=info

# 元数据标签
LABEL org.opencontainers.image.title="Suoke API Gateway" \
      org.opencontainers.image.description="API Gateway for Suoke Life Platform" \
      org.opencontainers.image.vendor="Suoke Life Technology" \
      org.opencontainers.image.authors="Suoke DevOps Team <devops@suoke.life>" \
      org.opencontainers.image.created="2023-12-01" \
      org.opencontainers.image.url="https://suoke.life" \
      org.opencontainers.image.source="https://github.com/suoke/api-gateway" \
      org.opencontainers.image.documentation="https://github.com/suoke/api-gateway/README.md" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.revision="1" \
      org.opencontainers.image.base.name="node:18-alpine" \
      com.suoke.service.name="api-gateway" \
      com.suoke.service.version="1.0.0" \
      com.suoke.service.category="Gateway" \
      com.suoke.service.tier="frontend" \
      com.suoke.security.scanned="true"

# 启动命令
CMD ["node", "dist/index.js"] 