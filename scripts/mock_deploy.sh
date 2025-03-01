#!/bin/bash

# mock_deploy.sh - 模拟部署脚本
#
# 此脚本模拟部署过程，用于测试CI/CD流程

set -e  # 遇到错误立即退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 设置环境变量
ENV=${1:-"staging"}
echo -e "${YELLOW}模拟部署环境: $ENV${NC}"

# 服务器配置
SERVER_HOST=${SERVER_HOST:-"118.31.223.213"}
SERVER_USER=${SERVER_USER:-"root"}
SERVER_TARGET_DIR="/var/www/suoke.life"

# 构建文件路径
WEB_BUILD_PATH="build/web"

# 模拟部署Web应用
mock_deploy_web_app() {
  echo -e "${YELLOW}模拟部署Web应用...${NC}"
  
  if [ ! -d "$WEB_BUILD_PATH" ]; then
    echo -e "${RED}错误: Web构建目录不存在: $WEB_BUILD_PATH${NC}"
    exit 1
  fi
  
  # 模拟创建远程目录
  echo -e "模拟执行: ssh $SERVER_USER@$SERVER_HOST \"mkdir -p $SERVER_TARGET_DIR/html\""
  
  # 模拟部署Web文件
  echo -e "模拟执行: rsync -avz --delete $WEB_BUILD_PATH/ $SERVER_USER@$SERVER_HOST:$SERVER_TARGET_DIR/html/"
  
  echo -e "${GREEN}Web应用模拟部署完成${NC}"
}

# 模拟配置Nginx
mock_configure_nginx() {
  echo -e "${YELLOW}模拟配置Nginx...${NC}"
  
  # 模拟上传Nginx配置
  echo -e "模拟执行: scp nginx.conf $SERVER_USER@$SERVER_HOST:/etc/nginx/conf.d/suoke.conf"
  
  # 模拟创建日志目录
  echo -e "模拟执行: ssh $SERVER_USER@$SERVER_HOST \"mkdir -p $SERVER_TARGET_DIR/logs\""
  
  # 模拟重启Nginx
  echo -e "模拟执行: ssh $SERVER_USER@$SERVER_HOST \"nginx -t && systemctl restart nginx\""
  
  echo -e "${GREEN}Nginx模拟配置完成${NC}"
}

# 检查模拟部署结果
mock_check_deployment() {
  echo -e "${YELLOW}模拟检查部署结果...${NC}"
  
  # 模拟检查网站可访问性
  echo -e "模拟执行: curl -s --head --request GET http://$SERVER_HOST"
  echo -e "${GREEN}模拟部署成功: 网站可正常访问${NC}"
}

# 主函数
main() {
  echo -e "${YELLOW}开始模拟部署到服务器...${NC}"
  
  mock_deploy_web_app
  mock_configure_nginx
  mock_check_deployment
  
  echo -e "${GREEN}模拟部署完成!${NC}"
  echo -e "${YELLOW}在实际环境中，您需要提供有效的SSH密钥才能进行真实部署${NC}"
  echo -e "${YELLOW}实际访问地址: http://$SERVER_HOST/${NC}"
}

# 执行主函数
main 