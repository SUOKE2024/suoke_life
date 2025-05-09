FROM nginx:1.23.1-alpine

# 元数据
LABEL maintainer="索克生活APP开发组"
LABEL version="1.0.0"
LABEL description="索克生活APP API网关服务"

# 复制配置文件
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# 设置工作目录
WORKDIR /usr/share/nginx/html

# 添加静态欢迎页
RUN echo '{"apiVersion":"1.0.0","serviceName":"suoke-api-gateway","status":"running"}' > /usr/share/nginx/html/info.json

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["nginx", "-g", "daemon off;"] 