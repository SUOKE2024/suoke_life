FROM golang:1.18-alpine AS builder

WORKDIR /app

# 复制go.mod和go.sum文件（如果存在）
COPY go.mod ./
COPY go.sum ./

# 安装依赖
RUN go mod download

# 复制源代码
COPY . .

# 编译应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o rag-service ./cmd/server

# 使用alpine作为基础镜像
FROM alpine:latest  

WORKDIR /app

# 从构建阶段复制编译好的可执行文件
COPY --from=builder /app/rag-service .

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/config

# 设置时区
RUN apk --no-cache add tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk --no-cache del tzdata

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["./rag-service"] 