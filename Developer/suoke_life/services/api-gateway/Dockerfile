# 第一阶段：构建二进制可执行文件
FROM golang:1.20-alpine AS builder

# 安装基础工具
RUN apk add --no-cache git ca-certificates tzdata && \
    update-ca-certificates

# 设置工作目录
WORKDIR /app

# 复制go.mod和go.sum
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 设置构建参数
ARG VERSION=dev
ARG BUILD_DATE=unknown
ARG GIT_COMMIT=unknown

# 构建可执行文件
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w \
    -X github.com/suoke-life/api-gateway/internal/version.Version=${VERSION} \
    -X github.com/suoke-life/api-gateway/internal/version.BuildDate=${BUILD_DATE} \
    -X github.com/suoke-life/api-gateway/internal/version.GitCommit=${GIT_COMMIT}" \
    -o api-gateway ./cmd/main.go

# 第二阶段：运行时镜像
FROM alpine:3.18

# 安装运行时依赖
RUN apk add --no-cache ca-certificates tzdata && \
    update-ca-certificates

# 设置时区
ENV TZ=Asia/Shanghai

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 创建必要的目录
RUN mkdir -p /app/configs /app/logs && \
    chown -R appuser:appgroup /app

# 设置工作目录
WORKDIR /app

# 从构建阶段复制编译好的可执行文件
COPY --from=builder /app/api-gateway .

# 复制配置文件
COPY --chown=appuser:appgroup configs/ ./configs/

# 设置环境变量
ENV PORT=8080
ENV CONFIG_PATH=/app/configs/config.json
ENV GIN_MODE=release

# 暴露服务端口
EXPOSE 8080

# 使用非root用户运行
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O- http://localhost:8080/health || exit 1

# 容器启动命令
CMD ["./api-gateway"] 