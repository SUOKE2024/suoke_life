#!/bin/bash

# 定义彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 日志文件
LOG_FILE="deploy-local-$(date +%Y%m%d-%H%M%S).log"

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

# 检查Docker是否运行
check_docker() {
    log "检查Docker是否运行..."
    
    if ! docker info > /dev/null 2>&1; then
        log "Docker未运行，请先启动Docker" "ERROR"
        exit 1
    fi
    
    log "Docker运行正常" "SUCCESS"
}

# 检查必要的目录
check_directories() {
    log "检查必要的目录..."
    
    for dir in data logs config; do
        if [ ! -d "$dir" ]; then
            log "创建目录: $dir"
            execute "mkdir -p $dir"
        fi
    done
}

# 构建并部署服务
build_and_deploy() {
    log "构建并部署服务..."
    
    # 先停止旧服务
    execute "docker-compose -f docker-compose.local.yml down"
    
    # 构建镜像
    execute "docker-compose -f docker-compose.local.yml build"
    
    if [ $? -ne 0 ]; then
        log "镜像构建失败" "ERROR"
        exit 1
    fi
    
    # 启动服务
    execute "docker-compose -f docker-compose.local.yml up -d"
    
    if [ $? -ne 0 ]; then
        log "服务启动失败" "ERROR"
        exit 1
    fi
    
    log "服务已成功部署" "SUCCESS"
}

# 检查服务状态
check_service() {
    log "检查服务状态..."
    
    # 等待服务启动
    log "等待服务启动..."
    sleep 5
    
    # 检查容器状态
    execute "docker ps -a | grep suoke-rag-service"
    
    # 检查容器日志
    execute "docker logs suoke-rag-service --tail=10"
    
    # 尝试访问健康检查
    log "尝试访问健康检查端点..."
    execute "curl -s http://localhost:8080"
}

# 主函数
main() {
    echo -e "${GREEN}===== 索克生活RAG服务本地部署脚本 =====${NC}"
    echo -e "${YELLOW}开始部署时间: $(date)${NC}"
    
    # 检查是否在正确的目录
    if [ ! -f "docker-compose.local.yml" ] || [ ! -f "Dockerfile.local" ]; then
        echo -e "${RED}错误: 请在项目根目录下运行此脚本${NC}"
        exit 1
    fi
    
    check_docker
    check_directories
    build_and_deploy
    check_service
    
    echo -e "${GREEN}===== 部署完成 =====${NC}"
    echo -e "${YELLOW}完成时间: $(date)${NC}"
    echo -e "${GREEN}日志已保存至: ${LOG_FILE}${NC}"
    echo -e "${YELLOW}您可以通过 http://localhost:8080 访问服务${NC}"
}

# 执行主函数
main 