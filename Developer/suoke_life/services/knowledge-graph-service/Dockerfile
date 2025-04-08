FROM golang:1.24.0 AS builder

# 设置工作目录
WORKDIR /build

# 设置Go模块和代理参数
ENV GO111MODULE=on
ENV GOPROXY=https://goproxy.cn,direct

# 复制Go模块定义
COPY go.mod go.sum ./

# 降级依赖
RUN go get -u github.com/klauspost/cpuid/v2@v2.1.2
RUN go get -u golang.org/x/arch@v0.5.0
RUN go get -u github.com/gin-contrib/cors@v1.4.0

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 编译应用程序
RUN CGO_ENABLED=0 GOOS=linux go build -a -o knowledge-graph-service ./cmd/server

# 第二阶段：基于alpine构建精简镜像
FROM alpine:3.17

# 设置工作目录
WORKDIR /app

# 安装必要的软件包
RUN apk add --no-cache ca-certificates tzdata wget

# 设置时区
ENV TZ=Asia/Shanghai

# 复制编译好的二进制文件和环境变量示例文件
COPY --from=builder /build/knowledge-graph-service .
COPY --from=builder /build/.env.example ./.env

# 设置环境变量
ENV GIN_MODE=release
ENV NEO4J_SERVICE_PORT=8080

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["./knowledge-graph-service"]
