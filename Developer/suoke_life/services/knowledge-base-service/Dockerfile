# 构建阶段
FROM golang:1.24-alpine AS builder

# 设置工作目录
WORKDIR /app

# 设置Go代理
ENV GOPROXY=https://goproxy.cn,direct

# 复制go.mod和go.sum文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN go build -o knowledge-base-service ./cmd/server

# 生产阶段使用轻量级镜像
FROM alpine:3.19

# 设置标签
LABEL maintainer="SuoKe Platform Team <dev@suoke.life>" \
      org.opencontainers.image.title="Knowledge Base Service" \
      org.opencontainers.image.description="索克生活平台知识库服务" \
      org.opencontainers.image.vendor="SuoKe Platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.url="https://suoke.life" \
      org.opencontainers.image.source="https://github.com/suoke-life/knowledge-base-service"

# 工作目录
WORKDIR /app

# 从构建阶段复制编译后的二进制文件
COPY --from=builder /app/knowledge-base-service /app/
COPY --from=builder /app/config /app/config

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/tmp && \
    adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app

# 设置环境变量
ENV PORT=3002 \
    APP_HOST=0.0.0.0 \
    LOG_LEVEL=info \
    OTEL_SERVICE_NAME=knowledge-base-service

# 暴露端口
EXPOSE 3002 9090

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3002/api/v1/health || exit 1

# 使用非root用户
USER appuser

# 挂载卷
VOLUME ["/app/data", "/app/logs", "/app/tmp"]

# 启动应用
CMD ["/app/knowledge-base-service"]