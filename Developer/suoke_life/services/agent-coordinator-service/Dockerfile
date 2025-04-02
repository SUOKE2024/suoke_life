FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache python3 make g++ tzdata git

# 复制package文件
COPY package*.json ./

# 安装所有依赖
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 安装生产环境必要的系统依赖
RUN apk add --no-cache curl tzdata dumb-init \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

# 创建非root用户
RUN addgroup -S agentapi && adduser -S agentapi -G agentapi

# 复制package文件
COPY package*.json ./

# 只安装生产依赖
RUN npm install --omit=dev

# 从构建阶段复制构建产物
COPY --from=builder --chown=agentapi:agentapi /app/dist /app/dist
COPY --from=builder --chown=agentapi:agentapi /app/config /app/config

# 设置环境变量
ENV NODE_ENV=production \
    PORT=3007 \
    LOG_LEVEL=info \
    COORDINATOR_MODE=distributed \
    AGENT_STATE_PERSISTENCE=redis \
    CONFIG_PATH=/app/config/coordinator-config.json

# 创建必要的目录并设置权限
RUN mkdir -p /app/logs /app/state /app/plugins \
    && chown -R agentapi:agentapi /app

# 切换到非root用户
USER agentapi

# 暴露端口
EXPOSE 3007

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3007/health || exit 1

# 使用dumb-init作为入口点以正确处理信号
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# 启动命令
CMD ["node", "dist/index.js"] 