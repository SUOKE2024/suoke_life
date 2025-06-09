#!/bin/bash

# 索克生活混合AI部署脚本
# 自动化部署本地与云端混合AI推理系统

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
    
    # 检查kubectl（可选）
    if command -v kubectl &> /dev/null; then
        log_success "检测到kubectl，支持Kubernetes部署"
        KUBECTL_AVAILABLE=true
    else
        log_warning "kubectl未安装，将跳过Kubernetes部署"
        KUBECTL_AVAILABLE=false
    fi
    
    # 检查系统资源
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    if [ "$TOTAL_MEM" -lt 4 ]; then
        log_warning "系统内存少于4GB，可能影响AI模型性能"
    fi
    
    log_success "依赖检查完成"
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    mkdir -p data/models/{local,cloud}
    mkdir -p data/cache
    mkdir -p logs
    mkdir -p config
    mkdir -p nginx
    
    # 设置权限
    chmod 755 data/models
    chmod 755 data/cache
    chmod 755 logs
    
    log_success "目录结构创建完成"
}

# 下载AI模型
download_models() {
    log_info "下载AI模型..."
    
    # 创建模型下载配置
    cat > config/models.json << EOF
{
  "local_models": [
    {
      "id": "health_basic_assessment",
      "name": "基础健康评估",
      "url": "https://models.suoke.life/onnx/health_basic_v1.0.onnx",
      "checksum": "sha256:abc123...",
      "size": "5MB"
    },
    {
      "id": "symptom_screening",
      "name": "症状初筛",
      "url": "https://models.suoke.life/tflite/symptom_screening_v1.2.tflite",
      "checksum": "sha256:def456...",
      "size": "3MB"
    },
    {
      "id": "voice_analysis",
      "name": "语音分析",
      "url": "https://models.suoke.life/onnx/voice_analysis_v2.0.onnx",
      "checksum": "sha256:ghi789...",
      "size": "8MB"
    }
  ],
  "cloud_models": [
    {
      "id": "deep_tcm_diagnosis",
      "name": "深度中医诊断",
      "endpoint": "https://api.suoke.life/ai/tcm-diagnosis",
      "version": "v3.0.1"
    },
    {
      "id": "personalized_treatment",
      "name": "个性化治疗方案",
      "endpoint": "https://api.suoke.life/ai/treatment-planning",
      "version": "v2.1.0"
    }
  ]
}
EOF

    # 使用Docker下载模型
    docker-compose -f docker-compose.hybrid-ai.yml --profile setup run --rm model-downloader
    
    log_success "AI模型下载完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx负载均衡..."
    
    cat > nginx/ai-gateway.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream hybrid_orchestrator {
        server hybrid-orchestrator:8080;
    }
    
    upstream local_ai {
        server local-ai-service:8080;
    }
    
    upstream cloud_ai {
        server cloud-ai-proxy:8080;
    }
    
    # 日志格式
    log_format ai_access '$remote_addr - $remote_user [$time_local] '
                        '"$request" $status $body_bytes_sent '
                        '"$http_referer" "$http_user_agent" '
                        'rt=$request_time uct="$upstream_connect_time" '
                        'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    server {
        listen 80;
        server_name _;
        
        access_log /var/log/nginx/ai_access.log ai_access;
        error_log /var/log/nginx/ai_error.log;
        
        # 健康检查
        location /health {
            proxy_pass http://hybrid_orchestrator/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # 混合推理API
        location /api/inference {
            proxy_pass http://hybrid_orchestrator;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # 本地推理API（直接访问）
        location /api/local {
            proxy_pass http://local_ai;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # 云端推理API（直接访问）
        location /api/cloud {
            proxy_pass http://cloud_ai;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # 监控指标
        location /metrics {
            proxy_pass http://hybrid_orchestrator/metrics;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # 静态文件
        location /static/ {
            alias /usr/share/nginx/html/;
            expires 1d;
        }
    }
}
EOF
    
    log_success "Nginx配置完成"
}

# 启动服务
start_services() {
    log_info "启动混合AI服务..."
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose -f docker-compose.hybrid-ai.yml build
    
    # 启动基础服务
    log_info "启动基础服务..."
    docker-compose -f docker-compose.hybrid-ai.yml up -d redis
    
    # 等待Redis启动
    sleep 10
    
    # 启动AI服务
    log_info "启动AI服务..."
    docker-compose -f docker-compose.hybrid-ai.yml up -d local-ai-service cloud-ai-proxy
    
    # 等待AI服务启动
    sleep 15
    
    # 启动编排器
    log_info "启动混合推理编排器..."
    docker-compose -f docker-compose.hybrid-ai.yml up -d hybrid-orchestrator
    
    # 等待编排器启动
    sleep 10
    
    # 启动网关和监控
    log_info "启动网关和监控服务..."
    docker-compose -f docker-compose.hybrid-ai.yml up -d ai-gateway ai-monitor
    
    log_success "所有服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署状态..."
    
    # 检查服务状态
    log_info "检查Docker容器状态..."
    docker-compose -f docker-compose.hybrid-ai.yml ps
    
    # 健康检查
    log_info "执行健康检查..."
    
    # 检查网关
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_success "✓ AI网关健康检查通过"
    else
        log_error "✗ AI网关健康检查失败"
    fi
    
    # 检查本地AI服务
    if curl -f http://localhost:8090/health > /dev/null 2>&1; then
        log_success "✓ 本地AI服务健康检查通过"
    else
        log_error "✗ 本地AI服务健康检查失败"
    fi
    
    # 检查云端代理
    if curl -f http://localhost:8091/health > /dev/null 2>&1; then
        log_success "✓ 云端AI代理健康检查通过"
    else
        log_error "✗ 云端AI代理健康检查失败"
    fi
    
    # 检查编排器
    if curl -f http://localhost:8092/health > /dev/null 2>&1; then
        log_success "✓ 混合推理编排器健康检查通过"
    else
        log_error "✗ 混合推理编排器健康检查失败"
    fi
    
    # 测试推理API
    log_info "测试推理API..."
    
    TEST_RESPONSE=$(curl -s -X POST http://localhost:8080/api/inference \
        -H "Content-Type: application/json" \
        -d '{
            "modelId": "health_basic_assessment",
            "inputData": {"symptoms": ["头痛", "失眠"]},
            "options": {"priority": "normal"}
        }')
    
    if [ $? -eq 0 ]; then
        log_success "✓ 推理API测试通过"
        echo "响应: $TEST_RESPONSE"
    else
        log_error "✗ 推理API测试失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 混合AI系统部署完成！"
    
    echo ""
    echo "=== 服务访问地址 ==="
    echo "AI网关:           http://localhost:8080"
    echo "本地AI服务:       http://localhost:8090"
    echo "云端AI代理:       http://localhost:8091"
    echo "混合推理编排器:   http://localhost:8092"
    echo "性能监控:         http://localhost:8093"
    echo ""
    echo "=== API端点 ==="
    echo "混合推理:         POST http://localhost:8080/api/inference"
    echo "本地推理:         POST http://localhost:8080/api/local"
    echo "云端推理:         POST http://localhost:8080/api/cloud"
    echo "健康检查:         GET  http://localhost:8080/health"
    echo "性能指标:         GET  http://localhost:8080/metrics"
    echo ""
    echo "=== 管理命令 ==="
    echo "查看日志:         docker-compose -f docker-compose.hybrid-ai.yml logs -f"
    echo "停止服务:         docker-compose -f docker-compose.hybrid-ai.yml down"
    echo "重启服务:         docker-compose -f docker-compose.hybrid-ai.yml restart"
    echo "查看状态:         docker-compose -f docker-compose.hybrid-ai.yml ps"
    echo ""
    echo "=== 配置文件 ==="
    echo "模型配置:         config/models.json"
    echo "Nginx配置:        nginx/ai-gateway.conf"
    echo "Docker配置:       docker-compose.hybrid-ai.yml"
    echo ""
}

# 主函数
main() {
    echo "🚀 开始部署索克生活混合AI系统"
    echo ""
    
    # 检查参数
    if [ "$1" = "--skip-models" ]; then
        SKIP_MODELS=true
        log_info "跳过模型下载"
    else
        SKIP_MODELS=false
    fi
    
    # 执行部署步骤
    check_dependencies
    create_directories
    configure_nginx
    
    if [ "$SKIP_MODELS" = false ]; then
        download_models
    fi
    
    start_services
    
    # 等待服务完全启动
    log_info "等待服务完全启动..."
    sleep 30
    
    verify_deployment
    show_deployment_info
    
    log_success "🎉 混合AI系统部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@" 