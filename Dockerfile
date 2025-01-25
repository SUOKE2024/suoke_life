FROM ubuntu:latest

# 安装必要的工具
RUN apt-get update && apt-get install -y curl git unzip openjdk-17-jdk

# 下载并安装 Flutter
RUN curl -s https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.0-stable.tar.xz -o flutter.tar.xz
RUN tar -xf flutter.tar.xz
ENV PATH="$PATH:/flutter/bin"

# 安装 Dart
RUN apt-get update && apt-get install -y dart

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN flutter pub get

# 构建应用 (可选，根据需要启用)
# RUN flutter build apk --release

# 暴露端口 (使用构建参数)
ARG APP_PORT=8080
EXPOSE $APP_PORT

# 运行应用 (可选，根据需要启用)
# CMD ["flutter", "run", "--release", "--no-sound-null-safety"]