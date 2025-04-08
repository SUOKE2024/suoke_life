FROM golang:1.21-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装基本工具和依赖
RUN apk add --no-cache git gcc musl-dev

# 拷贝go.mod和go.sum文件
COPY go.mod ./
COPY go.sum ./

# 下载依赖
RUN go mod download

# 拷贝源代码
COPY . .

# 编译为静态二进制文件
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o rag-service .

# 使用多阶段构建，使用更小的基础镜像
FROM alpine:latest

# 安装ca-certificates，用于HTTPS请求
RUN apk --no-cache add ca-certificates tzdata

# 设置工作目录
WORKDIR /app

# 从构建阶段拷贝二进制文件
COPY --from=builder /app/rag-service .

# 创建配置目录
RUN mkdir -p /app/config /app/data /app/logs

# 设置时区为上海
ENV TZ=Asia/Shanghai

# 公开端口
EXPOSE 8080

# 运行二进制文件
CMD ["./rag-service"]
