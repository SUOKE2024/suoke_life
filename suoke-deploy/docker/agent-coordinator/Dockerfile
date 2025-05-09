FROM node:18-alpine

# 元数据
LABEL maintainer="索克生活APP开发组"
LABEL version="1.0.0"
LABEL description="索克生活APP 智能体协调器服务"

# 创建工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY src/ ./src/
COPY config/ ./config/

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["node", "src/server.js"] 