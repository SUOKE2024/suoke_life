#!/bin/bash

# 索克生活医学知识服务部署脚本
# 提供一键部署、更新、备份等功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="suoke-med-knowledge"
COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "系统依赖检查完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p $BACKUP_DIR
    mkdir -p $LOG_DIR
    mkdir -p ./data
    mkdir -p ./deploy/nginx/ssl
    mkdir -p ./deploy/grafana/dashboards
    mkdir -p ./deploy/grafana/datasources
    
    log_success "目录创建完成"
}

# 生成SSL证书（自签名）
generate_ssl_cert() {
    log_info "生成SSL证书..."
    
    if [ ! -f "./deploy/nginx/ssl/cert.pem" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ./deploy/nginx/ssl/key.pem \
            -out ./deploy/nginx/ssl/cert.pem \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=SuokeLife/CN=localhost"
        
        log_success "SSL证书生成完成"
    else
        log_info "SSL证书已存在，跳过生成"
    fi
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    docker-compose down
    
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    docker-compose restart
    
    log_success "服务重启完成"
}

# 查看服务状态
show_status() {
    log_info "服务状态："
    docker-compose ps
    
    echo ""
    log_info "服务日志（最近50行）："
    docker-compose logs --tail=50
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    # 创建备份
    tar -czf $BACKUP_FILE \
        --exclude='./logs/*' \
        --exclude='./backups/*' \
        --exclude='./.git/*' \
        --exclude='./node_modules/*' \
        --exclude='./__pycache__/*' \
        .
    
    log_success "数据备份完成: $BACKUP_FILE"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份文件路径"
        exit 1
    fi
    
    BACKUP_FILE=$1
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
    
    log_info "恢复数据从: $BACKUP_FILE"
    
    # 停止服务
    stop_services
    
    # 恢复数据
    tar -xzf $BACKUP_FILE
    
    # 重启服务
    start_services
    
    log_success "数据恢复完成"
}

# 查看日志
show_logs() {
    SERVICE=${1:-""}
    
    if [ -z "$SERVICE" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $SERVICE
    fi
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    
    # 停止服务
    docker-compose down -v
    
    # 清理未使用的镜像
    docker image prune -f
    
    # 清理未使用的卷
    docker volume prune -f
    
    log_success "资源清理完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    if ! docker-compose ps | grep -q "Up"; then
        log_error "服务未正常运行"
        return 1
    fi
    
    # 检查API健康状态
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API健康检查通过"
    else
        log_error "API健康检查失败"
        return 1
    fi
    
    # 检查数据库连接
    if docker-compose exec -T neo4j cypher-shell -u neo4j -p password "RETURN 1" > /dev/null 2>&1; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
        return 1
    fi
    
    # 检查Redis连接
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis连接正常"
    else
        log_error "Redis连接失败"
        return 1
    fi
    
    log_success "所有健康检查通过"
}

# 更新服务
update_service() {
    log_info "更新服务..."
    
    # 备份数据
    backup_data
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建镜像
    build_images
    
    # 重启服务
    restart_services
    
    # 健康检查
    sleep 30
    health_check
    
    log_success "服务更新完成"
}

# 数据导入
import_data() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        log_error "用法: $0 import <数据类型> <文件路径> [格式]"
        log_info "数据类型: constitutions, symptoms, acupoints, herbs, syndromes, biomarkers, western_diseases, prevention_evidence, integrated_treatments, lifestyle_interventions"
        exit 1
    fi
    
    DATA_TYPE=$1
    FILE_PATH=$2
    FORMAT=${3:-"json"}
    
    log_info "导入 $DATA_TYPE 数据从 $FILE_PATH"
    
    docker-compose exec med-knowledge python scripts/data_import.py \
        --type $DATA_TYPE \
        --source $FILE_PATH \
        --format $FORMAT
    
    log_success "数据导入完成"
}

# 显示帮助信息
show_help() {
    echo "索克生活医学知识服务部署脚本"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  init          初始化环境（检查依赖、创建目录、生成证书）"
    echo "  build         构建Docker镜像"
    echo "  start         启动所有服务"
    echo "  stop          停止所有服务"
    echo "  restart       重启所有服务"
    echo "  status        查看服务状态"
    echo "  logs [服务名]  查看日志"
    echo "  backup        备份数据"
    echo "  restore <文件> 恢复数据"
    echo "  health        健康检查"
    echo "  update        更新服务"
    echo "  cleanup       清理Docker资源"
    echo "  import <类型> <文件> [格式] 导入数据"
    echo "  help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 init                    # 初始化环境"
    echo "  $0 start                   # 启动服务"
    echo "  $0 logs med-knowledge      # 查看med-knowledge服务日志"
    echo "  $0 import herbs data.json  # 导入中药数据"
}

# 主函数
main() {
    case "${1:-help}" in
        init)
            check_dependencies
            create_directories
            generate_ssl_cert
            log_success "环境初始化完成"
            ;;
        build)
            build_images
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs $2
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data $2
            ;;
        health)
            health_check
            ;;
        update)
            update_service
            ;;
        cleanup)
            cleanup
            ;;
        import)
            import_data $2 $3 $4
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 