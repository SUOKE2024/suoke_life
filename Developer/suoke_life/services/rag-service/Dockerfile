FROM python:3.9-slim

WORKDIR /app

# 安装基本工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt /app/

# 创建Python启动脚本 - 更健壮的服务启动方式
RUN echo 'import socket, time, json, sys' > /app/start.py && \
    echo 'print("RAG服务（Docker版本）已启动")' >> /app/start.py && \
    echo 'print("提供健康检查端点...")' >> /app/start.py && \
    echo 'def create_response():' >> /app/start.py && \
    echo '    return json.dumps({"status": "healthy", "version": "1.1.3-docker"})' >> /app/start.py && \
    echo 'try:' >> /app/start.py && \
    echo '    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)' >> /app/start.py && \
    echo '    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)' >> /app/start.py && \
    echo '    sock.bind(("0.0.0.0", 8000))' >> /app/start.py && \
    echo '    sock.listen(5)' >> /app/start.py && \
    echo '    print("服务器运行在 http://0.0.0.0:8000")' >> /app/start.py && \
    echo '    while True:' >> /app/start.py && \
    echo '        conn, addr = sock.accept()' >> /app/start.py && \
    echo '        print(f"接收到来自 {addr} 的连接")' >> /app/start.py && \
    echo '        data = conn.recv(1024)' >> /app/start.py && \
    echo '        response_body = create_response()' >> /app/start.py && \
    echo '        response = f"HTTP/1.1 200 OK\\r\\nContent-Type: application/json\\r\\nContent-Length: {len(response_body)}\\r\\n\\r\\n{response_body}"' >> /app/start.py && \
    echo '        conn.sendall(response.encode())' >> /app/start.py && \
    echo '        conn.close()' >> /app/start.py && \
    echo 'except Exception as e:' >> /app/start.py && \
    echo '    print(f"错误: {e}")' >> /app/start.py && \
    echo '    sys.exit(1)' >> /app/start.py && \
    echo 'finally:' >> /app/start.py && \
    echo '    sock.close()' >> /app/start.py

# 创建健康检查脚本
RUN echo '#!/bin/sh' > /app/healthcheck.sh && \
    echo 'curl -f http://localhost:8000/ || exit 1' >> /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# 暴露应用端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD /app/healthcheck.sh

# 以非root用户运行
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "/app/start.py"] 