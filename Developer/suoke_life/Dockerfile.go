FROM golang:1.20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装编译依赖
RUN apk add --no-cache git

# 复制Go模块文件
COPY go.mod go.sum* ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 编译应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o agent-coordinator-service ./cmd/main.go

# 使用精简的alpine镜像
FROM alpine:3.18

# 安装运行时依赖
RUN apk --no-cache add ca-certificates tzdata

# 添加非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 创建配置和日志目录
RUN mkdir -p /app/config /app/logs
RUN chown -R appuser:appgroup /app

# 切换到非root用户
USER appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制编译好的应用
COPY --from=builder --chown=appuser:appgroup /app/agent-coordinator-service .
COPY --chown=appuser:appgroup ./config /app/config

# 设置环境变量
ENV PORT=3007 \
    GIN_MODE=release \
    TZ=Asia/Shanghai

# 声明端口
EXPOSE 3007

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3007/health || exit 1

# 运行应用
CMD ["./agent-coordinator-service"] 