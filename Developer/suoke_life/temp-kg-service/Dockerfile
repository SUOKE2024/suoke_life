FROM registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.9 AS base

# 由于pause镜像非常精简，我们创建一个最小化的镜像
FROM scratch

# 复制文件到scratch镜像中
COPY --from=base /pause /
COPY config ./config
COPY cmd/knowledge-graph-service/main.go ./main.go
COPY knowledge-graph-service ./knowledge-graph-service

# 设置元数据
LABEL maintainer="索克生活"
LABEL version="1.0"
LABEL description="索克生活知识图谱服务 - 基于中医理论的知识服务"

# 暴露API端口
EXPOSE 8080

# 入口点（实际上scratch镜像无法执行此命令，仅作标记）
# CMD ["/knowledge-graph-service"] 