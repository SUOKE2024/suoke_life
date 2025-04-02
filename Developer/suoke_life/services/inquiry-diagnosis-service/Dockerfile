# 使用官方Node.js镜像作为基础镜像
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制所有源代码
COPY . .

# 编译TypeScript
RUN npm run build

# 使用更小的镜像进行生产部署
FROM node:18-alpine AS production

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production

# 从builder阶段复制依赖和编译后的代码
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# 复制配置文件和必要的资源
COPY --from=builder /app/config ./config

# 创建非root用户并切换到该用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001 && \
    mkdir -p /app/logs && \
    chown -R nodeuser:nodejs /app

USER nodeuser

# 暴露服务端口
EXPOSE 3000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# 启动服务
CMD ["node", "dist/index.js"]