# Deployment Guide

This document provides instructions on how to deploy the Suoke Life application.

## Prerequisites

- Docker
- Docker Compose

## Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/SUOKE2024/suoke-life.git
    cd suoke-life
    ```

2.  **Build and run the application using Docker Compose:**

    ```bash
    docker-compose up --build
    ```

    This command will build the Docker images and start the application along with its dependencies (Redis, LLM Service).

3.  **Access the application:**

    -   The main application will be available at `http://localhost:8080`.
    -   The LLM service will be available at `http://localhost:5000`.
    -   Prometheus will be available at `http://localhost:9090`.

## Docker Compose Configuration

The `docker-compose.yml` file defines the services for the application:

-   **app:** The main Flutter application.
-   **redis:** The Redis database for caching and session management.
-   **llm_service:** The LLM service for generating text.
-   **prometheus:** The Prometheus monitoring system.

## Monitoring

Prometheus is configured to scrape metrics from the application and the LLM service. You can access the Prometheus dashboard at `http://localhost:9090`.

## Notes

-   Ensure that the required ports (8080, 5000, 6379, 9090) are not in use by other applications.
-   The application is configured to use `http://localhost:8080/api/v1` as the base URL for API requests.
-   The LLM service is configured to use `http://localhost:5000/api/v1/llm/generate` as the endpoint for text generation.

## Docker

The application is containerized using Docker. The following services are included:

- **app:** The Flutter application.
- **redis:** The Redis server.
- **llm_service:** The LLM service.
- **prometheus:** The Prometheus monitoring server.

### Building the Docker Images

To build the Docker images, run the following command:

```bash
docker-compose build
```

## 系统要求

### 客户端
- Flutter 3.0+
- Dart 3.0+
- iOS 12.0+
- Android 5.0+
- 内存 2GB+
- 存储空间 100MB+

### 服务端
- Ubuntu 20.04 LTS
- MySQL 8.0+
- Redis 6.0+
- Nginx 1.18+
- Node.js 16+

## 环境配置

### Flutter 环境
```bash
# 安装 Flutter SDK
git clone https://github.com/flutter/flutter.git
export PATH="$PATH:`pwd`/flutter/bin"
flutter doctor

# 安装依赖
flutter pub get
```

### 开发环境变量
```bash
# 创建环境配置文件
cp .env.example .env

# 编辑配置
vim .env
```

### 证书配置
```bash
# 生成开发证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

## 打包发布

### Android
```bash
# 生成签名密钥
keytool -genkey -v -keystore suoke.keystore -alias suoke -keyalg RSA -validity 10000

# 打包 APK
flutter build apk --release

# 打包 AAB
flutter build appbundle --release
```

### iOS
```bash
# 配置证书
open ios/Runner.xcworkspace

# 打包 IPA
flutter build ios --release
```

## 服务器部署

### 数据库
```bash
# 安装 MySQL
apt install mysql-server

# 创建数据库
mysql -u root -p
CREATE DATABASE suoke;

# 导入数据
mysql -u root -p suoke < schema.sql
```

### Redis
```bash
# 安装 Redis
apt install redis-server

# 配置
vim /etc/redis/redis.conf
```

### Nginx
```nginx
server {
    listen 443 ssl;
    server_name api.suoke.life;

    ssl_certificate /etc/nginx/cert.pem;
    ssl_certificate_key /etc/nginx/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## CI/CD

### GitHub Actions
```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: flutter test
      - run: flutter build apk
```

## 监控告警

### 性能监控
- CPU 使用率 > 80%
- 内存使用率 > 80%
- 磁盘使用率 > 90%

### 错误监控
- 应用崩溃
- API 异常
- 数据库异常

### 业务监控
- DAU
- 用户增长
- AI 对话量

## 灾备方案

### 数据备份
```bash
# 数据库备份
mysqldump -u root -p suoke > backup.sql

# 文件备份
rsync -avz /data/suoke backup/
```

### 恢复流程
1. 启动备用服务器
2. 恢复数据库
3. 恢复文件
4. 切换域名解析

## 扩容方案

### 数据库扩容
- 主从复制
- 读写分离
- 分库分表

### 服务扩容
- 负载均衡
- 容器化部署
- 自动扩缩容 