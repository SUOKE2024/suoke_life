#!/bin/bash

# 索克生活 - Docker镜像构建脚本
# 用于构建和推送所有微服务的Docker镜像

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/build-$(date +%Y%m%d-%H%M%S).log"

# 创建日志目录
mkdir -p "${PROJECT_ROOT}/logs"

# 日志函数
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE" >&2
}

log_success() {
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# 显示帮助信息
show_help() {
    cat << EOF
索克生活 Docker镜像构建脚本

用法: $0 [选项] [服务名...]

选项:
  -h, --help              显示此帮助信息
  -t, --tag TAG           指定镜像标签 (默认: latest)
  -r, --registry REGISTRY 指定镜像仓库 (默认: ghcr.io/suoke2024/suoke_life)
  -p, --push              构建后推送镜像
  -f, --force             强制重新构建，不使用缓存
  -a, --all               构建所有服务
  --platform PLATFORM     指定构建平台 (默认: linux/amd64,linux/arm64)
  --no-cache              不使用Docker缓存
  --parallel              并行构建

服务名:
  api-gateway                    API网关服务
  user-management-service        用户管理服务
  unified-health-data-service    健康数据服务
  blockchain-service             区块链服务
  communication-service          通信服务
  xiaoai-service                 小艾智能体服务
  xiaoke-service                 小克智能体服务
  laoke-service                  老克智能体服务
  soer-service                   索儿智能体服务

示例:
  $0 --all --push                           # 构建所有服务并推送
  $0 api-gateway user-management-service     # 构建指定服务
  $0 --tag v1.2.3 --push api-gateway        # 构建指定版本并推送

EOF
}

# 默认配置
TAG="latest"
REGISTRY="ghcr.io/suoke2024/suoke_life"
PUSH_IMAGES=false
FORCE_BUILD=false
BUILD_ALL=false
PLATFORM="linux/amd64,linux/arm64"
USE_CACHE=true
PARALLEL_BUILD=false
SERVICES=()

# 所有可用服务
ALL_SERVICES=(
    "api-gateway"
    "user-management-service"
    "unified-health-data-service"
    "blockchain-service"
    "communication-service"
    "agent-services/xiaoai-service"
    "agent-services/xiaoke-service"
    "agent-services/laoke-service"
    "agent-services/soer-service"
)

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_IMAGES=true
            shift
            ;;
        -f|--force)
            FORCE_BUILD=true
            shift
            ;;
        -a|--all)
            BUILD_ALL=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --no-cache)
            USE_CACHE=false
            shift
            ;;
        --parallel)
            PARALLEL_BUILD=true
            shift
            ;;
        api-gateway|user-management-service|unified-health-data-service|blockchain-service|communication-service|xiaoai-service|xiaoke-service|laoke-service|soer-service)
            SERVICES+=("$1")
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 确定要构建的服务
if [[ "$BUILD_ALL" == "true" ]]; then
    SERVICES=("${ALL_SERVICES[@]}")
elif [[ ${#SERVICES[@]} -eq 0 ]]; then
    log_error "必须指定要构建的服务或使用 --all 选项"
    show_help
    exit 1
fi

log_info "开始构建Docker镜像"
log_info "标签: $TAG"
log_info "仓库: $REGISTRY"
log_info "平台: $PLATFORM"
log_info "服务: ${SERVICES[*]}"

# 检查Docker
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker守护进程未运行"
        exit 1
    fi
    
    # 检查Docker Buildx
    if ! docker buildx version &> /dev/null; then
        log_error "Docker Buildx未安装"
        exit 1
    fi
    
    log_success "Docker环境检查完成"
}

# 登录镜像仓库
login_registry() {
    if [[ "$PUSH_IMAGES" == "true" ]]; then
        log_info "登录镜像仓库..."
        
        if [[ "$REGISTRY" == ghcr.io* ]]; then
            # GitHub Container Registry
            if [[ -n "${GITHUB_TOKEN:-}" ]]; then
                echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
            else
                log_error "需要设置GITHUB_TOKEN环境变量"
                exit 1
            fi
        else
            # 其他仓库
            if [[ -n "${REGISTRY_USERNAME:-}" && -n "${REGISTRY_PASSWORD:-}" ]]; then
                echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY" -u "$REGISTRY_USERNAME" --password-stdin
            else
                log_error "需要设置REGISTRY_USERNAME和REGISTRY_PASSWORD环境变量"
                exit 1
            fi
        fi
        
        log_success "镜像仓库登录完成"
    fi
}

# 构建单个服务
build_service() {
    local service="$1"
    local service_path="services/$service"
    local service_name
    
    # 处理智能体服务路径
    if [[ "$service" == *"/"* ]]; then
        service_name=$(basename "$service")
    else
        service_name="$service"
    fi
    
    log_info "构建服务: $service_name"
    
    # 检查服务目录
    if [[ ! -d "$PROJECT_ROOT/$service_path" ]]; then
        log_error "服务目录不存在: $service_path"
        return 1
    fi
    
    # 检查Dockerfile
    local dockerfile="$PROJECT_ROOT/$service_path/Dockerfile"
    if [[ ! -f "$dockerfile" ]]; then
        dockerfile="$PROJECT_ROOT/$service_path/deploy/docker/Dockerfile"
        if [[ ! -f "$dockerfile" ]]; then
            log_error "Dockerfile不存在: $service_path"
            return 1
        fi
    fi
    
    # 构建镜像名称
    local image_name="$REGISTRY/$service_name:$TAG"
    local latest_image="$REGISTRY/$service_name:latest"
    
    # 构建参数
    local build_args=()
    build_args+=("--file" "$dockerfile")
    build_args+=("--tag" "$image_name")
    build_args+=("--tag" "$latest_image")
    build_args+=("--platform" "$PLATFORM")
    
    if [[ "$USE_CACHE" == "false" ]]; then
        build_args+=("--no-cache")
    fi
    
    if [[ "$PUSH_IMAGES" == "true" ]]; then
        build_args+=("--push")
    else
        build_args+=("--load")
    fi
    
    # 添加构建上下文
    build_args+=("$PROJECT_ROOT/$service_path")
    
    # 执行构建
    log_info "执行构建命令: docker buildx build ${build_args[*]}"
    
    if docker buildx build "${build_args[@]}"; then
        log_success "服务构建完成: $service_name"
        
        # 显示镜像信息
        if [[ "$PUSH_IMAGES" == "false" ]]; then
            docker images "$REGISTRY/$service_name"
        fi
        
        return 0
    else
        log_error "服务构建失败: $service_name"
        return 1
    fi
}

# 并行构建服务
build_services_parallel() {
    log_info "并行构建服务..."
    
    local pids=()
    local failed_services=()
    
    for service in "${SERVICES[@]}"; do
        build_service "$service" &
        pids+=($!)
    done
    
    # 等待所有构建完成
    for i in "${!pids[@]}"; do
        local pid=${pids[$i]}
        local service=${SERVICES[$i]}
        
        if wait "$pid"; then
            log_success "并行构建完成: $service"
        else
            log_error "并行构建失败: $service"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "以下服务构建失败: ${failed_services[*]}"
        return 1
    fi
    
    log_success "所有服务并行构建完成"
}

# 串行构建服务
build_services_serial() {
    log_info "串行构建服务..."
    
    local failed_services=()
    
    for service in "${SERVICES[@]}"; do
        if ! build_service "$service"; then
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "以下服务构建失败: ${failed_services[*]}"
        return 1
    fi
    
    log_success "所有服务串行构建完成"
}

# 验证镜像
verify_images() {
    log_info "验证构建的镜像..."
    
    for service in "${SERVICES[@]}"; do
        local service_name
        if [[ "$service" == *"/"* ]]; then
            service_name=$(basename "$service")
        else
            service_name="$service"
        fi
        
        local image_name="$REGISTRY/$service_name:$TAG"
        
        if [[ "$PUSH_IMAGES" == "true" ]]; then
            # 验证远程镜像
            if docker manifest inspect "$image_name" &> /dev/null; then
                log_success "镜像验证成功: $image_name"
            else
                log_error "镜像验证失败: $image_name"
                return 1
            fi
        else
            # 验证本地镜像
            if docker image inspect "$image_name" &> /dev/null; then
                log_success "镜像验证成功: $image_name"
            else
                log_error "镜像验证失败: $image_name"
                return 1
            fi
        fi
    done
    
    log_success "所有镜像验证完成"
}

# 清理旧镜像
cleanup_old_images() {
    log_info "清理旧镜像..."
    
    # 清理悬空镜像
    docker image prune -f
    
    # 清理旧版本镜像（保留最近5个版本）
    for service in "${SERVICES[@]}"; do
        local service_name
        if [[ "$service" == *"/"* ]]; then
            service_name=$(basename "$service")
        else
            service_name="$service"
        fi
        
        local old_images
        old_images=$(docker images "$REGISTRY/$service_name" --format "table {{.Repository}}:{{.Tag}}" | tail -n +2 | head -n -5)
        
        if [[ -n "$old_images" ]]; then
            echo "$old_images" | xargs -r docker rmi
        fi
    done
    
    log_success "旧镜像清理完成"
}

# 生成构建报告
generate_build_report() {
    log_info "生成构建报告..."
    
    local report_file="${PROJECT_ROOT}/reports/build-report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# 索克生活 Docker镜像构建报告

## 构建信息
- **构建时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **构建标签**: $TAG
- **镜像仓库**: $REGISTRY
- **构建平台**: $PLATFORM
- **推送状态**: $PUSH_IMAGES

## 构建的服务

EOF
    
    for service in "${SERVICES[@]}"; do
        local service_name
        if [[ "$service" == *"/"* ]]; then
            service_name=$(basename "$service")
        else
            service_name="$service"
        fi
        
        local image_name="$REGISTRY/$service_name:$TAG"
        
        cat >> "$report_file" << EOF
### $service_name
- **镜像名称**: \`$image_name\`
- **服务路径**: \`services/$service\`
- **构建状态**: ✅ 成功

EOF
    done
    
    cat >> "$report_file" << EOF

## 镜像列表

\`\`\`bash
EOF
    
    for service in "${SERVICES[@]}"; do
        local service_name
        if [[ "$service" == *"/"* ]]; then
            service_name=$(basename "$service")
        else
            service_name="$service"
        fi
        
        echo "$REGISTRY/$service_name:$TAG" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF
\`\`\`

## 使用方法

\`\`\`bash
# 拉取镜像
docker pull $REGISTRY/api-gateway:$TAG

# 运行容器
docker run -d -p 8000:8000 $REGISTRY/api-gateway:$TAG
\`\`\`

EOF
    
    log_success "构建报告生成完成: $report_file"
}

# 主函数
main() {
    cd "$PROJECT_ROOT"
    
    check_docker
    login_registry
    
    # 创建构建器
    if ! docker buildx inspect suoke-builder &> /dev/null; then
        docker buildx create --name suoke-builder --use
    fi
    
    # 构建镜像
    if [[ "$PARALLEL_BUILD" == "true" ]]; then
        build_services_parallel
    else
        build_services_serial
    fi
    
    verify_images
    cleanup_old_images
    generate_build_report
    
    log_success "所有镜像构建完成！"
}

# 错误处理
handle_error() {
    local exit_code=$?
    log_error "镜像构建失败，退出码: $exit_code"
    exit $exit_code
}

trap handle_error ERR

# 执行主函数
main "$@"