# 第一阶段：构建阶段（使用阿里云Node.js基础镜像）
FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/pause:3.6 AS builder
WORKDIR /app
COPY package*.json ./
COPY server.js ./

# 安装生产依赖（使用阿里云镜像加速）
RUN npm install --production --registry=https://registry.npmmirror.com

# 第二阶段：精简运行时镜像
FROM scratch AS runtime
COPY --from=builder /app /app
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY .env.example /app/.env

# 第三阶段：最终镜像（指定架构）
FROM suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-base:latest
ARG TARGETARCH=amd64
ARG TARGETOS=linux

# 设置中国时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 复制构建产物
COPY --from=runtime /app /app

# 安全配置
RUN addgroup --system --gid 1001 suoke && \
    adduser --system --uid 1001 --ingroup suoke suoke
USER suoke

EXPOSE 3002
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3002/health || exit 1

CMD ["node", "/app/server.js"] 