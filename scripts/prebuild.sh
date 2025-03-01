#!/bin/bash

# prebuild.sh - 构建前处理脚本
# 
# 此脚本在构建前执行，主要用于：
# 1. 根据环境变量设置正确的API端点和配置
# 2. 处理资源文件
# 3. 进行其他必要的构建前准备工作

set -e  # 遇到错误立即退出

# 设置环境变量
ENV=${ENV:-"development"}  # 如果没有设置ENV，默认为development
echo "构建环境: $ENV"

# 创建配置目录（如果不存在）
CONFIG_DIR="lib/core/config"
mkdir -p $CONFIG_DIR

# 根据环境生成配置文件
generate_config() {
  local env=$1
  local api_url=""
  local socket_url=""
  local enable_logging=""
  
  case $env in
    "development")
      api_url="http://192.168.1.100:8080/api"
      socket_url="ws://192.168.1.100:8080/ws"
      enable_logging="true"
      ;;
    "staging")
      api_url="http://118.31.223.213/api"
      socket_url="ws://118.31.223.213/ws"
      enable_logging="true"
      ;;
    "production")
      api_url="https://api.suoke.life"
      socket_url="wss://socket.suoke.life"
      enable_logging="false"
      ;;
    *)
      echo "未知环境: $env"
      exit 1
      ;;
  esac
  
  # 写入环境配置文件
  cat > $CONFIG_DIR/environment.dart << EOL
// 此文件由CI/CD过程自动生成，请勿手动修改
// 生成时间: $(date)
// 环境: $env

class Environment {
  static const String apiUrl = "$api_url";
  static const String socketUrl = "$socket_url";
  static const bool enableLogging = $enable_logging;
  static const String environment = "$env";
}
EOL

  echo "已生成环境配置文件: $CONFIG_DIR/environment.dart"
}

# 准备资源文件
prepare_assets() {
  echo "准备应用资源文件..."
  # 这里可以添加资源处理逻辑，如图片优化、JSON压缩等
}

# 处理国际化文件
process_localization() {
  echo "处理国际化文件..."
  # 这里可以添加国际化处理逻辑
}

# 主函数
main() {
  echo "开始构建前处理..."
  
  # 生成环境配置
  generate_config $ENV
  
  # 准备资源
  prepare_assets
  
  # 处理国际化
  process_localization
  
  echo "构建前处理完成!"
}

# 执行主函数
main 