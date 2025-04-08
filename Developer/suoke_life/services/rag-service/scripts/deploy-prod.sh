#!/bin/bash

# 定义彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 服务名称
SERVICE_NAME="rag-service"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
TAG="latest"
FULL_IMAGE_NAME="${REGISTRY}/${SERVICE_NAME}:${TAG}"

# 日志文件
LOG_FILE="deploy-$(date +%Y%m%d-%H%M%S).log"

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
    
    for dir in config data logs models deployment/nginx/conf.d deployment/nginx/ssl; do
        if [ ! -d "$dir" ]; then
            log "创建目录: $dir"
            execute "mkdir -p $dir"
        fi
    done
}

# 登录到镜像仓库
login_registry() {
    log "登录到阿里云容器镜像仓库..."
    USERNAME="netsong@sina.com"
    PASSWORD="Netsong2025"
    
    execute "echo '${PASSWORD}' | docker login --username '${USERNAME}' --password-stdin '${REGISTRY}'"
    
    if [ $? -ne 0 ]; then
        log "登录失败，无法继续部署" "ERROR"
        exit 1
    fi
    
    log "登录成功" "SUCCESS"
}

# 拉取最新镜像
pull_image() {
    log "拉取最新镜像 ${FULL_IMAGE_NAME}..."
    execute "docker pull ${FULL_IMAGE_NAME}"
    
    if [ $? -ne 0 ]; then
        log "镜像拉取失败" "ERROR"
        exit 1
    fi
    
    log "镜像拉取成功" "SUCCESS"
}

# 部署服务
deploy_services() {
    log "部署服务..."
    
    # 检查生产配置文件是否存在
    if [ ! -f ".env.production" ]; then
        log "警告: .env.production 文件不存在，将使用 .env.example" "WARNING"
        execute "cp .env.example .env.production"
    fi
    
    # 创建空SSL证书文件（仅为占位符）
    if [ ! -f "./deployment/nginx/ssl/suoke.life.crt" ]; then
        log "创建空SSL证书占位符文件" "INFO"
        execute "touch ./deployment/nginx/ssl/suoke.life.crt"
        execute "touch ./deployment/nginx/ssl/suoke.life.key"
        log "警告: 请替换SSL证书文件为有效证书！" "WARNING"
    fi
    
    # 更新docker-compose.prod.yml中的镜像地址
    log "更新docker-compose.prod.yml中的镜像地址"
    execute "sed -i '' 's|image: suoke/rag-service:latest|image: ${FULL_IMAGE_NAME}|g' docker-compose.prod.yml"
    
    # 使用生产环境的docker-compose文件
    execute "docker-compose -f docker-compose.prod.yml --env-file .env.production down"
    execute "docker-compose -f docker-compose.prod.yml --env-file .env.production up -d"
    
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
    sleep 10
    
    # 检查服务状态
    execute "docker-compose -f docker-compose.prod.yml ps"
    
    # 检查服务日志
    log "检查服务日志..."
    execute "docker-compose -f docker-compose.prod.yml logs --tail=20 rag-service"
    
    # 检查健康状态
    log "检查健康状态..."
    if curl -s http://localhost:8080/health | grep -q "ok"; then
        log "服务健康状态: 正常" "SUCCESS"
    else
        log "服务健康状态: 异常" "ERROR"
        log "请检查服务日志获取更多信息" "ERROR"
    fi
}

# 清理旧备份和镜像
cleanup() {
    log "清理旧备份和未使用的镜像..."
    
    # 删除14天以前的备份
    if [ -d "./deployment/backups" ]; then
        execute "find ./deployment/backups -name \"*.tar.gz\" -type f -mtime +14 -delete"
    fi
    
    # 清理未使用的Docker镜像
    execute "docker image prune -f"
}

# 主函数
main() {
    echo -e "${GREEN}===== 索克生活RAG服务部署脚本 =====${NC}"
    echo -e "${YELLOW}开始部署时间: $(date)${NC}"
    
    # 检查是否在正确的目录
    if [ ! -f "docker-compose.prod.yml" ]; then
        echo -e "${RED}错误: 请在项目根目录下运行此脚本${NC}"
        exit 1
    fi
    
    check_directories
    login_registry
    pull_image
    deploy_services
    check_services
    cleanup
    
    echo -e "${GREEN}===== 部署完成 =====${NC}"
    echo -e "${YELLOW}完成时间: $(date)${NC}"
    echo -e "${GREEN}日志已保存至: ${LOG_FILE}${NC}"
}

# 执行主函数
main