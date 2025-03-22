#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
SERVER_IP="118.31.223.213"
NGINX_CONFIG_DIR="/etc/nginx/conf.d"
LOCAL_CONFIG_PATH="services/config/nginx/suoke.conf"
REMOTE_CONFIG_PATH="${NGINX_CONFIG_DIR}/suoke.conf"
BACKUP_CONFIG_PATH="${NGINX_CONFIG_DIR}/suoke.conf.bak"

print_info "开始更新Nginx配置..."

# 检查本地配置文件是否存在
if [ ! -f "$LOCAL_CONFIG_PATH" ]; then
  print_error "本地配置文件不存在: $LOCAL_CONFIG_PATH"
  exit 1
fi

# 备份当前配置
print_info "备份当前配置文件..."
ssh "root@$SERVER_IP" "cp $REMOTE_CONFIG_PATH $BACKUP_CONFIG_PATH"

if [ $? -ne 0 ]; then
  print_warning "无法备份当前配置，可能是首次部署"
fi

# 复制配置文件到服务器
print_info "将配置文件复制到服务器: $SERVER_IP"
scp "$LOCAL_CONFIG_PATH" "root@$SERVER_IP:$REMOTE_CONFIG_PATH"

if [ $? -ne 0 ]; then
  print_error "复制配置文件失败"
  exit 1
fi

print_success "配置文件已成功复制到服务器"

# 测试Nginx配置
print_info "测试Nginx配置"
if ! ssh "root@$SERVER_IP" "nginx -t"; then
  print_error "Nginx配置测试失败，准备回滚..."
  
  # 如果备份存在，则回滚
  if ssh "root@$SERVER_IP" "[ -f $BACKUP_CONFIG_PATH ]"; then
    print_warning "正在回滚到上一个可用配置..."
    ssh "root@$SERVER_IP" "cp $BACKUP_CONFIG_PATH $REMOTE_CONFIG_PATH && nginx -t"
    
    if [ $? -eq 0 ]; then
      print_info "回滚成功，正在重新加载Nginx..."
      ssh "root@$SERVER_IP" "systemctl reload nginx"
      print_success "已回滚到之前的配置"
    else
      print_error "回滚也失败，Nginx配置可能存在严重问题"
    fi
  fi
  
  exit 1
fi

print_success "Nginx配置测试通过"

# 重启Nginx
print_info "重启Nginx服务"
ssh "root@$SERVER_IP" "systemctl restart nginx"

if [ $? -ne 0 ]; then
  print_error "重启Nginx服务失败，尝试回滚..."
  
  # 回滚配置并尝试重启
  if ssh "root@$SERVER_IP" "[ -f $BACKUP_CONFIG_PATH ]"; then
    print_warning "正在回滚到上一个可用配置..."
    ssh "root@$SERVER_IP" "cp $BACKUP_CONFIG_PATH $REMOTE_CONFIG_PATH"
    ssh "root@$SERVER_IP" "systemctl restart nginx"
    
    if [ $? -eq 0 ]; then
      print_success "已回滚到之前的配置并重启成功"
    else
      print_error "回滚后重启仍然失败，请手动检查Nginx状态"
    fi
  fi
  
  exit 1
fi

print_success "Nginx服务已重启"

# 检查Nginx状态
print_info "检查Nginx服务状态"
ssh "root@$SERVER_IP" "systemctl status nginx"

# 检查配置是否生效 - 请求健康检查端点
print_info "验证配置是否正确应用..."
response_code=$(curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP/health")

if [ "$response_code" = "200" ] || [ "$response_code" = "502" ]; then
  print_success "配置验证: 健康检查端点响应代码 $response_code"
else
  print_warning "配置可能未正确应用: 健康检查端点返回 $response_code"
fi

print_success "Nginx配置更新完成"

# 通知其他开发人员
print_info "请通知团队成员：Nginx配置已更新"