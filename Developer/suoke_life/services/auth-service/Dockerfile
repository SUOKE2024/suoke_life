FROM scratch

WORKDIR /app

# 复制预编译好的二进制文件
COPY ./bin/auth-service /app/auth-service
COPY ./configs /app/configs

# 注意：scratch镜像中不能运行mkdir命令，需要在构建前确保bin目录存在

# 暴露服务端口
EXPOSE 8081

# 运行服务
CMD ["/app/auth-service"]