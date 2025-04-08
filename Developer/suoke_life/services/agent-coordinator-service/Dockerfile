# 多阶段构建的Go应用Dockerfile
# 第一阶段: 构建二进制可执行文件
FROM golang:1.20-alpine AS builder

# 构建参数
ARG VERSION=dev
ARG BUILD_DATE=unknown
ARG GIT_COMMIT=unknown

# 环境变量
ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

# 安装依赖工具
RUN apk --no-cache add ca-certificates git make

# 设置工作目录
WORKDIR /app

# 复制go mod文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN go build -ldflags="-s -w \
    -X github.com/suoke-life/agent-coordinator-service/pkg/version.Version=${VERSION} \
    -X github.com/suoke-life/agent-coordinator-service/pkg/version.BuildDate=${BUILD_DATE} \
    -X github.com/suoke-life/agent-coordinator-service/pkg/version.GitCommit=${GIT_COMMIT}" \
    -o /app/bin/agent-coordinator ./cmd/main.go

# 第二阶段: 最小运行时镜像
FROM alpine:3.17

# 添加运行时依赖
RUN apk --no-cache add ca-certificates tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    adduser -D -u 1000 appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/bin/agent-coordinator /app/agent-coordinator

# 复制配置文件和资源
COPY --from=builder /app/config /app/config
COPY --from=builder /app/assets /app/assets

# 添加版本信息标签
LABEL maintainer="suoke-life <dev@suoke.life>" \
      version="${VERSION}" \
      build-date="${BUILD_DATE}" \
      git-commit="${GIT_COMMIT}"

# 使用非root用户运行应用
USER appuser

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 暴露服务端口
EXPOSE 8080

# 运行服务
ENTRYPOINT ["/app/agent-coordinator"] 