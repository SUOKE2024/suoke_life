#!/bin/bash

# server_deploy.sh - 服务器部署脚本
#
# 此脚本用于将构建产物部署到阿里云服务器

set -e  # 遇到错误立即退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 设置环境变量
ENV=${1:-"staging"}
echo -e "${YELLOW}部署环境: $ENV${NC}"

# 服务器配置
SERVER_HOST=${SERVER_HOST:-"118.31.223.213"}
SERVER_USER=${SERVER_USER:-"root"}
SERVER_SSH_PORT=${SERVER_SSH_PORT:-"22"}
SERVER_TARGET_DIR="/var/www/suoke.life"

# 构建文件路径
WEB_BUILD_PATH="build/web"
SERVER_CONFIG_PATH="build/server"

# 检查SSH密钥
check_ssh_key() {
  echo -e "${YELLOW}检查SSH密钥...${NC}"
  
  if [ -z "$SSH_PRIVATE_KEY" ]; then
    echo -e "${RED}错误: 未设置SSH_PRIVATE_KEY环境变量${NC}"
    exit 1
  fi
  
  # 将SSH密钥写入临时文件
  mkdir -p ~/.ssh
  echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
  chmod 600 ~/.ssh/id_rsa
  
  # 配置SSH
  cat > ~/.ssh/config << EOL
Host $SERVER_HOST
  HostName $SERVER_HOST
  User $SERVER_USER
  Port $SERVER_SSH_PORT
  IdentityFile ~/.ssh/id_rsa
  StrictHostKeyChecking no
EOL
  
  chmod 600 ~/.ssh/config
  
  echo -e "${GREEN}SSH密钥配置完成${NC}"
}

# 部署Web应用
deploy_web_app() {
  echo -e "${YELLOW}部署Web应用...${NC}"
  
  if [ ! -d "$WEB_BUILD_PATH" ]; then
    echo -e "${RED}错误: Web构建目录不存在: $WEB_BUILD_PATH${NC}"
    exit 1
  fi
  
  # 创建远程目录
  ssh $SERVER_USER@$SERVER_HOST "mkdir -p $SERVER_TARGET_DIR/html"
  
  # 部署Web文件
  rsync -avz --delete $WEB_BUILD_PATH/ $SERVER_USER@$SERVER_HOST:$SERVER_TARGET_DIR/html/
  
  echo -e "${GREEN}Web应用部署完成${NC}"
}

# 配置Nginx
configure_nginx() {
  echo -e "${YELLOW}配置Nginx...${NC}"
  
  # 写入Nginx配置文件
  cat > nginx.conf << EOL
server {
    listen 80;
    server_name suoke.life www.suoke.life;
    
    root $SERVER_TARGET_DIR/html;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /ai/ {
        proxy_pass http://localhost:8081/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /users/ {
        proxy_pass http://localhost:8082/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /content/ {
        proxy_pass http://localhost:8083/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    access_log $SERVER_TARGET_DIR/logs/access.log;
    error_log $SERVER_TARGET_DIR/logs/error.log;
}
EOL
  
  # 上传Nginx配置
  scp nginx.conf $SERVER_USER@$SERVER_HOST:/etc/nginx/conf.d/suoke.conf
  
  # 创建日志目录
  ssh $SERVER_USER@$SERVER_HOST "mkdir -p $SERVER_TARGET_DIR/logs"
  
  # 重启Nginx
  ssh $SERVER_USER@$SERVER_HOST "nginx -t && systemctl restart nginx"
  
  # 清理临时文件
  rm nginx.conf
  
  echo -e "${GREEN}Nginx配置完成${NC}"
}

# 检查部署结果
check_deployment() {
  echo -e "${YELLOW}检查部署结果...${NC}"
  
  # 检查网站可访问性
  if curl -s --head --request GET http://$SERVER_HOST | grep "200 OK" > /dev/null; then
    echo -e "${GREEN}部署成功: 网站可正常访问${NC}"
  else
    echo -e "${YELLOW}警告: 网站似乎无法访问，请手动检查${NC}"
  fi
}

# 主函数
main() {
  echo -e "${YELLOW}开始部署到服务器...${NC}"
  
  check_ssh_key
  deploy_web_app
  configure_nginx
  check_deployment
  
  echo -e "${GREEN}部署完成!${NC}"
}

# 执行主函数
main 