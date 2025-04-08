#!/bin/bash

# 定义彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 日志文件
LOG_FILE="deploy-minimal-$(date +%Y%m%d-%H%M%S).log"

# 函数: 记录日志
log() {
    local message="$1"
    local level="${2:-INFO}"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# 函数: 执行命令并记录日志
execute() {
    local cmd="$1"
    local desc="${2:-Executing command}"
    
    log "$desc: $cmd" "CMD"
    
    if eval "$cmd" >> "$LOG_FILE" 2>&1; then
        log "命令执行成功" "SUCCESS"
        return 0
    else
        local exit_code=$?
        log "命令失败，退出代码: $exit_code" "ERROR"
        return $exit_code
    fi
}

# 检查必要的目录
check_directories() {
    log "检查必要的目录..."
    
    for dir in data logs deployment/nginx/conf.d deployment/nginx/ssl logs/nginx; do
        if [ ! -d "$dir" ]; then
            log "创建目录: $dir"
            execute "mkdir -p $dir"
        fi
    done
}

# 创建Nginx配置
create_nginx_config() {
    log "创建Nginx配置..."
    
    if [ ! -f "deployment/nginx/conf.d/default.conf" ]; then
        log "创建默认Nginx配置文件"
        cat > deployment/nginx/conf.d/default.conf << EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://rag-service:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://rag-service:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
        log "Nginx配置文件已创建" "SUCCESS"
    else
        log "Nginx配置文件已存在，跳过创建"
    fi
}

# 部署服务
deploy_services() {
    log "部署服务..."
    
    # 拉取busybox镜像
    log "拉取busybox镜像..."
    execute "docker pull busybox:latest"
    
    # 拉取nginx镜像
    log "拉取nginx镜像..."
    execute "docker pull nginx:stable-alpine"
    
    # 使用简化版compose文件
    execute "docker-compose -f docker-compose.minimal.yml down"
    execute "docker-compose -f docker-compose.minimal.yml up -d"
    
    if [ $? -ne 0 ]; then
        log "服务部署失败" "ERROR"
        exit 1
    fi
    
    log "服务部署完成" "SUCCESS"
}

# 检查服务状态
check_services() {
    log "检查服务状态..."
    
    # 等待服务启动
    log "等待服务启动..."
    sleep 5
    
    # 检查服务状态
    execute "docker-compose -f docker-compose.minimal.yml ps"
    
    # 检查服务日志
    log "检查rag-service服务日志..."
    execute "docker logs suoke-rag-service --tail=5"
    
    log "检查nginx服务日志..."
    execute "docker logs suoke-nginx --tail=5"
    
    # 检查健康状态
    log "检查健康状态..."
    execute "curl -s http://localhost:8080"
    execute "curl -s http://localhost"
}

# 主函数
main() {
    echo -e "${GREEN}===== 索克生活RAG服务最小化部署脚本 =====${NC}"
    echo -e "${YELLOW}开始部署时间: $(date)${NC}"
    
    # 检查是否在正确的目录
    if [ ! -f "docker-compose.minimal.yml" ]; then
        echo -e "${RED}错误: 请在项目根目录下运行此脚本${NC}"
        exit 1
    fi
    
    check_directories
    create_nginx_config
    deploy_services
    check_services
    
    echo -e "${GREEN}===== 部署完成 =====${NC}"
    echo -e "${YELLOW}完成时间: $(date)${NC}"
    echo -e "${GREEN}日志已保存至: ${LOG_FILE}${NC}"
    echo -e "${YELLOW}可通过以下地址访问服务:${NC}"
    echo -e "${GREEN}HTTP: http://localhost:8080${NC}"
    echo -e "${GREEN}Nginx代理: http://localhost${NC}"
}

# 执行主函数
main 