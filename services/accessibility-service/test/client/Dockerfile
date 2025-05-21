FROM python:3.10-slim

WORKDIR /app

# 安装依赖
RUN pip install --no-cache-dir grpcio==1.62.0 protobuf==4.25.2

# 将当前目录复制到容器
COPY . /app

# 设置执行权限
RUN chmod +x /app/test_client.py

# 设置入口点
ENTRYPOINT ["/bin/bash"] 