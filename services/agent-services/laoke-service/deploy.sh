#!/bin/bash

# 老克智能体服务 - 自动化部署脚本
# 索克生活项目 v1.0.0

set -e  # 遇到错误立即退出

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
    log_info "检查部署依赖..."
    
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
    
    log_success "依赖检查通过"
}

# 环境检查
check_environment() {
    log_info "检查环境配置..."
    
    # 检查环境变量
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warning "OPENAI_API_KEY环境变量未设置"
        read -p "请输入OpenAI API Key: " OPENAI_API_KEY
        export OPENAI_API_KEY
    fi
    
    # 创建必要目录
    mkdir -p logs data monitoring/grafana/{dashboards,datasources}
    
    log_success "环境检查完成"
}

# 代码质量检查
quality_check() {
    log_info "执行代码质量检查..."
    
    # 语法检查
    python -c "import ast; files = ['internal/knowledge/knowledge_service.py', 'internal/knowledge/knowledge_graph.py', 'internal/repository/knowledge_repository.py']; [ast.parse(open(f).read()) for f in files]"
    
    # 代码风格检查
    if command -v flake8 &> /dev/null; then
        flake8 --select=E,W --ignore=E501,W503 internal/ pkg/ --count
    fi
    
    log_success "代码质量检查通过"
}

# 构建镜像
build_image() {
    log_info "构建Docker镜像..."
    
    # 构建镜像
    docker build -t suoke/laoke-service:latest .
    
    # 标记版本
    docker tag suoke/laoke-service:latest suoke/laoke-service:v1.0.0
    
    log_success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log_info "部署服务..."
    
    # 停止现有服务
    docker-compose down --remove-orphans
    
    # 启动服务
    docker-compose up -d
    
    log_success "服务部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 30
    
    # 检查服务状态
    if curl -f http://localhost:8080/health &> /dev/null; then
        log_success "老克智能体服务健康检查通过"
    else
        log_error "老克智能体服务健康检查失败"
        docker-compose logs laoke-service
        exit 1
    fi
    
    # 检查数据库连接
    if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping')" &> /dev/null; then
        log_success "MongoDB连接正常"
    else
        log_warning "MongoDB连接检查失败"
    fi
    
    if docker-compose exec -T neo4j cypher-shell -u neo4j -p laoke_password "RETURN 1" &> /dev/null; then
        log_success "Neo4j连接正常"
    else
        log_warning "Neo4j连接检查失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_info "部署信息:"
    echo "=================================="
    echo "🚀 老克智能体服务: http://localhost:8080"
    echo "📊 Grafana监控: http://localhost:3000 (admin/laoke_grafana_password)"
    echo "📈 Prometheus: http://localhost:9090"
    echo "🗄️  Neo4j浏览器: http://localhost:7474 (neo4j/laoke_password)"
    echo "📱 MongoDB: localhost:27017"
    echo "🔄 Redis: localhost:6379"
    echo "=================================="
    echo "📋 查看日志: docker-compose logs -f laoke-service"
    echo "🛑 停止服务: docker-compose down"
    echo "🔄 重启服务: docker-compose restart"
    echo "=================================="
}

# 主函数
main() {
    echo "🚀 老克智能体服务部署脚本 v1.0.0"
    echo "索克生活项目 - 生产环境部署"
    echo "=================================="
    
    # 执行部署步骤
    check_dependencies
    check_environment
    quality_check
    build_image
    deploy_services
    health_check
    show_deployment_info
    
    log_success "🎉 老克智能体服务部署完成！"
}

# 处理命令行参数
case "${1:-}" in
    "check")
        check_dependencies
        check_environment
        quality_check
        ;;
    "build")
        build_image
        ;;
    "deploy")
        deploy_services
        ;;
    "health")
        health_check
        ;;
    "info")
        show_deployment_info
        ;;
    *)
        main
        ;;
esac 