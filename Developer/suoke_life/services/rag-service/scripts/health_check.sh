#!/bin/bash

# 安装netcat
apt-get update && apt-get install -y netcat

echo "Starting RAG Service health check server on port 8080..."
while true; do
  echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nRAG Service is healthy" | nc -l -p 8080
done 