FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# 仅安装生产依赖
RUN npm ci --only=production

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3012

# 暴露应用和指标端口
EXPOSE 3012 9465

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3012/health/live || exit 1

# 启动应用
CMD ["node", "dist/index.js"] 