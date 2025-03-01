#!/bin/bash

# real_deploy.sh - 实际部署脚本
#
# 此脚本用于执行实际的部署过程，将测试页面部署到阿里云服务器

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

# 检查SSH密钥
setup_ssh_key() {
  echo -e "${YELLOW}设置SSH密钥...${NC}"
  
  # 创建~/.ssh目录
  mkdir -p ~/.ssh
  
  if [ ! -f ~/.ssh/id_rsa_suoke ]; then
    echo -e "${YELLOW}未找到SSH密钥，请输入您的SSH私钥内容:${NC}"
    echo -e "${YELLOW}或者按Ctrl+C取消，然后手动将SSH密钥复制到~/.ssh/id_rsa_suoke${NC}"
    echo -e "${YELLOW}提示：您可以从之前生成的密钥中复制，或者通过cat ~/.ssh/id_rsa查看您的密钥${NC}"
    
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo -e "${RED}操作已取消${NC}"
      exit 1
    fi
    
    echo -e "${YELLOW}请输入SSH私钥内容 (Ctrl+D结束):${NC}"
    cat > ~/.ssh/id_rsa_suoke
    chmod 600 ~/.ssh/id_rsa_suoke
  else
    echo -e "${GREEN}找到现有SSH密钥: ~/.ssh/id_rsa_suoke${NC}"
  fi
  
  # 配置SSH
  cat > ~/.ssh/config << EOL
Host $SERVER_HOST
  HostName $SERVER_HOST
  User $SERVER_USER
  Port $SERVER_SSH_PORT
  IdentityFile ~/.ssh/id_rsa_suoke
  StrictHostKeyChecking no
EOL
  
  chmod 600 ~/.ssh/config
  
  # 测试SSH连接
  echo -e "${YELLOW}测试SSH连接...${NC}"
  if ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_HOST "echo 连接成功"; then
    echo -e "${GREEN}SSH连接成功${NC}"
  else
    echo -e "${RED}SSH连接失败，请检查SSH密钥和服务器配置${NC}"
    exit 1
  fi
}

# 部署Web应用
deploy_web_app() {
  echo -e "${YELLOW}部署Web应用...${NC}"
  
  if [ ! -d "$WEB_BUILD_PATH" ]; then
    echo -e "${RED}错误: Web构建目录不存在: $WEB_BUILD_PATH${NC}"
    exit 1
  fi
  
  echo -e "${YELLOW}正在检查远程目录...${NC}"
  # 创建远程目录
  ssh $SERVER_USER@$SERVER_HOST "mkdir -p $SERVER_TARGET_DIR/html"
  
  echo -e "${YELLOW}正在上传文件...${NC}"
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
  
  echo -e "${YELLOW}正在上传Nginx配置...${NC}"
  # 上传Nginx配置
  scp nginx.conf $SERVER_USER@$SERVER_HOST:/etc/nginx/conf.d/suoke.conf
  
  echo -e "${YELLOW}正在创建日志目录...${NC}"
  # 创建日志目录
  ssh $SERVER_USER@$SERVER_HOST "mkdir -p $SERVER_TARGET_DIR/logs"
  
  echo -e "${YELLOW}正在重启Nginx...${NC}"
  # 重启Nginx
  ssh $SERVER_USER@$SERVER_HOST "nginx -t && systemctl restart nginx"
  
  # 清理临时文件
  rm nginx.conf
  
  echo -e "${GREEN}Nginx配置完成${NC}"
}

# 检查部署结果
check_deployment() {
  echo -e "${YELLOW}检查部署结果...${NC}"
  
  echo -e "${YELLOW}等待服务器响应 (10秒)...${NC}"
  sleep 10
  
  # 检查网站可访问性
  echo -e "${YELLOW}尝试访问网站...${NC}"
  if curl -s --head --request GET http://$SERVER_HOST | grep "200" > /dev/null; then
    echo -e "${GREEN}部署成功: 网站可正常访问${NC}"
    echo -e "${GREEN}请在浏览器中访问 http://$SERVER_HOST 查看部署结果${NC}"
  else
    echo -e "${YELLOW}警告: 网站似乎无法访问，请手动检查 http://$SERVER_HOST${NC}"
  fi
}

# 主函数
main() {
  echo -e "${YELLOW}开始实际部署到服务器...${NC}"
  
  setup_ssh_key
  deploy_web_app
  configure_nginx
  check_deployment
  
  echo -e "${GREEN}部署完成!${NC}"
  echo -e "${GREEN}您现在可以通过访问 http://$SERVER_HOST 查看部署结果${NC}"
}

# 执行主函数
main 