#!/bin/bash

PORT=8080
echo "启动简单健康检查服务在端口 $PORT..."
while true; do
  echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"healthy\",\"service\":\"rag-minimal-fallback\",\"version\":\"1.0.0\"}" | nc -l -p $PORT
done
