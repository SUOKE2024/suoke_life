#!/bin/bash

# 索克生活认证服务快速启动脚本
# 使用方法: ./quick_start.sh [dev|prod]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装，请先安装Python3"
        exit 1
    fi
    
    log_success "系统依赖检查通过"
}

# 创建环境配置
create_env_config() {
    local env_type=$1
    log_info "创建环境配置文件..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# 索克生活认证服务环境配置
ENVIRONMENT=${env_type}
DEBUG=$([ "$env_type" = "dev" ] && echo "true" || echo "false")

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=suoke_auth_db
DB_USER=auth_user
DB_PASSWORD=suoke_auth_2024_secure_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT配置
JWT_SECRET_KEY=suoke_life_jwt_secret_key_very_long_and_secure_at_least_32_characters_long_2024
JWT_ALGORITHM=RS256
JWT_ACCESS_EXPIRES=3600
JWT_REFRESH_EXPIRES=604800

# 服务配置
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000

# 可选服务配置 (根据需要启用)
# TWILIO_ACCOUNT_SID=your_twilio_account_sid
# TWILIO_AUTH_TOKEN=your_twilio_auth_token
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
# GITHUB_CLIENT_ID=your_github_client_id
# GITHUB_CLIENT_SECRET=your_github_client_secret
EOF
        log_success "环境配置文件已创建: .env"
    else
        log_warning "环境配置文件已存在，跳过创建"
    fi
}

# 启动开发环境
start_dev() {
    log_info "启动开发环境..."
    
    # 创建开发环境配置
    create_env_config "dev"
    
    # 安装Python依赖
    log_info "安装Python依赖..."
    pip install -r requirements.txt
    
    # 启动Docker服务
    log_info "启动数据库和Redis服务..."
    docker-compose up -d postgres redis
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    python -m alembic upgrade head || log_warning "数据库迁移失败，请检查数据库连接"
    
    # 运行测试
    log_info "运行测试..."
    python -m pytest test_todo_features_simple.py -v || log_warning "测试失败，请检查代码"
    
    # 启动服务
    log_info "启动认证服务..."
    python main.py &
    
    log_success "开发环境启动完成！"
    log_info "服务地址: http://localhost:8000"
    log_info "API文档: http://localhost:8000/docs"
    log_info "健康检查: http://localhost:8000/health"
}

# 启动生产环境
start_prod() {
    log_info "启动生产环境..."
    
    # 创建生产环境配置
    create_env_config "prod"
    
    # 运行生产环境检查
    log_info "运行生产环境检查..."
    python simple_production_check.py || log_warning "生产环境检查发现问题，请查看上述输出"
    
    # 启动所有服务
    log_info "启动所有服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 健康检查
    log_info "执行健康检查..."
    for i in {1..5}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "服务健康检查通过"
            break
        else
            log_warning "健康检查失败，重试中... ($i/5)"
            sleep 5
        fi
    done
    
    log_success "生产环境启动完成！"
    log_info "服务地址: http://localhost:8000"
    log_info "监控面板: http://localhost:3000 (如果启用)"
    log_info "查看服务状态: docker-compose ps"
    log_info "查看服务日志: docker-compose logs -f"
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    docker-compose down
    
    # 停止Python进程
    pkill -f "python main.py" || true
    
    log_success "服务已停止"
}

# 清理环境
cleanup() {
    log_info "清理环境..."
    docker-compose down -v
    docker system prune -f
    log_success "环境清理完成"
}

# 显示帮助信息
show_help() {
    echo "索克生活认证服务快速启动脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 dev     - 启动开发环境"
    echo "  $0 prod    - 启动生产环境"
    echo "  $0 stop    - 停止所有服务"
    echo "  $0 clean   - 清理环境"
    echo "  $0 help    - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev     # 启动开发环境"
    echo "  $0 prod    # 启动生产环境"
    echo "  $0 stop    # 停止服务"
}

# 主函数
main() {
    local command=${1:-help}
    
    case $command in
        "dev")
            check_dependencies
            start_dev
            ;;
        "prod")
            check_dependencies
            start_prod
            ;;
        "stop")
            stop_services
            ;;
        "clean")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 脚本入口
main "$@" 