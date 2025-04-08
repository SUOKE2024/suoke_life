#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

# 如果在非终端环境运行，禁用颜色
if [ ! -t 1 ]; then
    GREEN=''
    BLUE=''
    RED=''
    YELLOW=''
    NC=''
fi

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务CI/CD自动化流程  ${NC}"
echo -e "${BLUE}==============================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || {
    echo -e "${RED}❌ 无法切换到项目根目录!${NC}"
    exit 1
}

# 检查Docker是否已安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装! 请先安装Docker${NC}"
    exit 1
fi

# 从环境变量中获取配置
# 如果环境变量不存在，则使用默认值或从Git计算
REGISTRY="${REGISTRY:-suoke-registry.cn-hangzhou.cr.aliyuncs.com}"
REPOSITORY="${REPOSITORY:-suoke/suoke-knowledge-graph-service}"
# 使用CI_REGISTRY_*变量作为备选，这些是GitLab CI中的标准变量
REGISTRY_USERNAME="${REGISTRY_USERNAME:-${CI_REGISTRY_USER:-}}"
REGISTRY_PASSWORD="${REGISTRY_PASSWORD:-${CI_REGISTRY_PASSWORD:-}}"
NAMESPACE="${NAMESPACE:-suoke-prod}"
DOCKERFILE="${DOCKERFILE:-Dockerfile.new}"
DOCKERFILE_AMD64="${DOCKERFILE_AMD64:-Dockerfile.amd64}"
SKIP_LINT="${SKIP_LINT:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
SKIP_BUILD="${SKIP_BUILD:-false}"
SKIP_DEPLOY="${SKIP_DEPLOY:-false}"
BUILD_ARM64="${BUILD_ARM64:-false}"
CI="${CI:-false}"

# 记录配置信息到日志文件
mkdir -p logs
LOG_FILE="logs/cicd-$(date +%Y%m%d%H%M%S).log"
{
    echo "运行时间: $(date)"
    echo "运行目录: $(pwd)"
    echo "REGISTRY: ${REGISTRY}"
    echo "REPOSITORY: ${REPOSITORY}"
    echo "NAMESPACE: ${NAMESPACE}"
    echo "DOCKERFILE: ${DOCKERFILE}"
    echo "DOCKERFILE_AMD64: ${DOCKERFILE_AMD64}"
    echo "SKIP_LINT: ${SKIP_LINT}"
    echo "SKIP_TESTS: ${SKIP_TESTS}"
    echo "SKIP_BUILD: ${SKIP_BUILD}"
    echo "SKIP_DEPLOY: ${SKIP_DEPLOY}"
    echo "BUILD_ARM64: ${BUILD_ARM64}"
    echo "CI: ${CI}"
} > "$LOG_FILE"

# 设置日志输出函数
log() {
    echo -e "$1"
    echo "$1" | sed -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,3})*)?[mGK]//g" >> "$LOG_FILE"
}

# 获取当前分支名称和版本
if [ -z "$VERSION" ]; then
    if [ -d ".git" ] || git rev-parse --git-dir > /dev/null 2>&1; then
        BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        SHORT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    else
        log "${YELLOW}未检测到Git仓库，使用时间戳作为版本号${NC}"
        BRANCH="unknown"
        SHORT_COMMIT="unknown"
    fi
    
    BUILD_DATE=$(date +'%Y%m%d')
    
    if [[ "$BRANCH" == "main" ]]; then
        VERSION="$BUILD_DATE-$SHORT_COMMIT-release"
    elif [[ "$BRANCH" == "develop" ]]; then
        VERSION="$BUILD_DATE-$SHORT_COMMIT-dev"
    elif [[ "$BRANCH" =~ ^release/.* ]]; then
        RELEASE_VERSION=$(echo $BRANCH | cut -d'/' -f2)
        VERSION="$RELEASE_VERSION-$BUILD_DATE-$SHORT_COMMIT-rc"
    else
        VERSION="$BUILD_DATE-$SHORT_COMMIT-snapshot"
    fi
fi

log "${BLUE}构建信息:${NC}"
log "${YELLOW}当前分支: ${BRANCH:-未知}${NC}"
log "${YELLOW}生成版本: ${VERSION}${NC}"
log "${YELLOW}镜像仓库: ${REGISTRY}/${REPOSITORY}${NC}"
log "${YELLOW}命名空间: ${NAMESPACE}${NC}"

# 设置镜像标签
TAG="${REGISTRY}/${REPOSITORY}:${VERSION}"
LATEST_TAG="${REGISTRY}/${REPOSITORY}:latest"
AMD64_TAG="${REGISTRY}/${REPOSITORY}:${VERSION}-amd64"
ARM64_TAG="${REGISTRY}/${REPOSITORY}:${VERSION}-arm64"

# 1. 运行代码检查
if [ "$SKIP_LINT" != "true" ]; then
    log "\n${BLUE}步骤1: 运行代码检查...${NC}"
    if command -v golangci-lint &> /dev/null; then
        log "${YELLOW}运行golangci-lint...${NC}"
        if golangci-lint run ./... >> "$LOG_FILE" 2>&1; then
            log "${GREEN}✅ 代码检查通过${NC}"
        else
            log "${RED}❌ 代码检查失败!${NC}"
            if [ "${CI}" == "true" ]; then
                exit 1
            else
                log "${YELLOW}在非CI环境中继续执行...${NC}"
            fi
        fi
    else
        log "${YELLOW}golangci-lint未安装，跳过代码检查${NC}"
    fi
else
    log "\n${BLUE}步骤1: 跳过代码检查${NC}"
fi

# 2. 运行单元测试
if [ "$SKIP_TESTS" != "true" ]; then
    log "\n${BLUE}步骤2: 运行单元测试...${NC}"
    if go test -v -race -coverprofile=coverage.out ./... >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✅ 单元测试通过${NC}"
    else
        log "${RED}❌ 单元测试失败!${NC}"
        if [ "${CI}" == "true" ]; then
            exit 1
        else
            log "${YELLOW}在非CI环境中继续执行...${NC}"
        fi
    fi
else
    log "\n${BLUE}步骤2: 跳过单元测试${NC}"
fi

# 3. 构建并推送Docker镜像
if [ "$SKIP_BUILD" != "true" ]; then
    log "\n${BLUE}步骤3: 设置Docker Buildx...${NC}"
    
    # 检查 Docker Buildx
    if ! docker buildx version &> /dev/null; then
        log "${RED}❌ Docker Buildx未安装!${NC}"
        log "${YELLOW}尝试启用Docker Buildx...${NC}"
        if ! docker buildx create --name multiarch-builder --use >> "$LOG_FILE" 2>&1; then
            log "${RED}❌ 无法启用Docker Buildx!${NC}"
            exit 1
        fi
    fi

    # 确认或创建buildx构建器
    if ! docker buildx ls | grep -q multiarch-builder; then
        log "${YELLOW}创建新的构建器: multiarch-builder${NC}"
        docker buildx create --name multiarch-builder --use >> "$LOG_FILE" 2>&1
    else
        log "${YELLOW}使用现有构建器: multiarch-builder${NC}"
        docker buildx use multiarch-builder >> "$LOG_FILE" 2>&1
    fi

    # 引导构建器
    log "${YELLOW}引导构建器...${NC}"
    docker buildx inspect --bootstrap >> "$LOG_FILE" 2>&1

    # 4. 登录到阿里云容器镜像服务
    log "\n${BLUE}步骤4: 登录到阿里云容器镜像服务...${NC}"
    
    # 检查凭据
    if [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
        log "${RED}❌ 缺少容器仓库凭据!${NC}"
        log "${YELLOW}尝试从~/.docker/config.json读取凭据${NC}"
        
        if [ -f ~/.docker/config.json ] && grep -q "\"$REGISTRY\"" ~/.docker/config.json; then
            log "${GREEN}✅ 发现现有Docker登录凭据${NC}"
        else
            # 在CI环境中，这是一个错误；在交互式环境中，请求用户输入
            if [ "${CI}" == "true" ]; then
                log "${RED}❌ 在CI环境中需要设置REGISTRY_USERNAME和REGISTRY_PASSWORD环境变量${NC}"
                exit 1
            else
                log "${YELLOW}请提供阿里云容器镜像仓库凭据${NC}"
                read -p "用户名: " REGISTRY_USERNAME
                read -sp "密码: " REGISTRY_PASSWORD
                echo ""
                if [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
                    log "${RED}❌ 无效的凭据!${NC}"
                    exit 1
                fi
            fi
        fi
    fi

    # 登录到阿里云容器镜像服务
    if [ -n "$REGISTRY_USERNAME" ] && [ -n "$REGISTRY_PASSWORD" ]; then
        log "${YELLOW}登录到${REGISTRY}...${NC}"
        if ! echo "$REGISTRY_PASSWORD" | docker login --username="$REGISTRY_USERNAME" --password-stdin "$REGISTRY" >> "$LOG_FILE" 2>&1; then
            log "${RED}❌ 登录失败!${NC}"
            exit 1
        else
            log "${GREEN}✅ 登录成功${NC}"
        fi
    else
        log "${YELLOW}跳过登录，使用现有凭据${NC}"
    fi

    # 5. 构建并推送多架构Docker镜像
    log "\n${BLUE}步骤5: 构建并推送多架构Docker镜像...${NC}"
    log "${YELLOW}构建多架构镜像: ${TAG}${NC}"

    # 使用Buildx构建并推送多架构镜像
    if docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag ${TAG} \
        --tag ${LATEST_TAG} \
        --file ${DOCKERFILE} \
        --push \
        . >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✅ 多架构镜像构建成功${NC}"
    else
        log "${RED}❌ 多架构构建失败!${NC}"
        log "${YELLOW}尝试构建单架构镜像...${NC}"
    fi

    # 6. 构建并推送AMD64架构Docker镜像
    log "\n${BLUE}步骤6: 构建并推送AMD64架构Docker镜像...${NC}"
    log "${YELLOW}构建AMD64镜像: ${AMD64_TAG}${NC}"

    if docker buildx build \
        --platform linux/amd64 \
        --tag ${AMD64_TAG} \
        --file ${DOCKERFILE_AMD64} \
        --push \
        . >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✅ AMD64镜像构建成功${NC}"
    else
        log "${RED}❌ AMD64构建失败!${NC}"
        exit 1
    fi
    
    # 可选：构建ARM64镜像
    if [ "${BUILD_ARM64}" == "true" ]; then
        log "\n${BLUE}步骤7: 构建并推送ARM64架构Docker镜像...${NC}"
        log "${YELLOW}构建ARM64镜像: ${ARM64_TAG}${NC}"

        if docker buildx build \
            --platform linux/arm64 \
            --tag ${ARM64_TAG} \
            --file ${DOCKERFILE} \
            --push \
            . >> "$LOG_FILE" 2>&1; then
            log "${GREEN}✅ ARM64镜像构建成功${NC}"
        else
            log "${RED}❌ ARM64构建失败!${NC}"
            log "${YELLOW}继续执行...${NC}"
        fi
    fi
else
    log "\n${BLUE}步骤3-6: 跳过Docker镜像构建${NC}"
fi

# 7. 部署到Kubernetes集群
if [ "$SKIP_DEPLOY" != "true" ]; then
    log "\n${BLUE}步骤7: 部署到Kubernetes集群...${NC}"
    log "${YELLOW}部署到命名空间: ${NAMESPACE}${NC}"

    # 检查kubectl是否可用
    if ! command -v kubectl &> /dev/null; then
        log "${RED}❌ kubectl未安装!${NC}"
        log "${YELLOW}跳过部署${NC}"
        SKIP_DEPLOY=true
    fi

    # 检查helm是否可用
    if ! command -v helm &> /dev/null; then
        log "${RED}❌ helm未安装!${NC}"
        log "${YELLOW}跳过部署${NC}"
        SKIP_DEPLOY=true
    fi

    if [ "$SKIP_DEPLOY" == "true" ]; then
        log "${YELLOW}由于缺少必要工具，部署步骤已跳过${NC}"
    else
        # 更新values文件中的版本号和部署日期
        DEPLOY_DATE=$(date +'%Y-%m-%dT%H:%M:%S')
        log "${YELLOW}更新部署时间为: ${DEPLOY_DATE}${NC}"

        # 确定使用哪个values文件
        VALUES_FILE="./helm/override-configs/values-${NAMESPACE#suoke-}.yaml"
        if [ ! -f "$VALUES_FILE" ]; then
            VALUES_FILE="./helm/override-configs/values-prod.yaml"
        fi
        
        log "${YELLOW}更新配置文件: ${VALUES_FILE}${NC}"
        
        # 创建临时文件而不是原地修改，避免.bak文件
        if [ -f "$VALUES_FILE" ]; then
            sed "s/tag: \".*\"/tag: \"${VERSION}\"/" "$VALUES_FILE" > "$VALUES_FILE.tmp" && mv "$VALUES_FILE.tmp" "$VALUES_FILE"
            sed "s/tagAMD64: \".*\"/tagAMD64: \"${VERSION}-amd64\"/" "$VALUES_FILE" > "$VALUES_FILE.tmp" && mv "$VALUES_FILE.tmp" "$VALUES_FILE"
            sed "s/tagARM64: \".*\"/tagARM64: \"${VERSION}-arm64\"/" "$VALUES_FILE" > "$VALUES_FILE.tmp" && mv "$VALUES_FILE.tmp" "$VALUES_FILE"
            sed "s/deploy-date: \".*\"/deploy-date: \"${DEPLOY_DATE}\"/" "$VALUES_FILE" > "$VALUES_FILE.tmp" && mv "$VALUES_FILE.tmp" "$VALUES_FILE"
            log "${GREEN}✅ 配置文件更新成功${NC}"
        else
            log "${RED}❌ 配置文件不存在: ${VALUES_FILE}${NC}"
            exit 1
        fi

        # 执行部署
        log "${YELLOW}执行部署...${NC}"
        export MULTI_ARCH_IMAGE=${TAG}
        export AMD64_IMAGE=${AMD64_TAG}
        export ARM64_IMAGE=${ARM64_TAG}
        
        DEPLOY_SCRIPT="./scripts/deploy-to-k8s.sh"
        
        if [ ! -f "$DEPLOY_SCRIPT" ]; then
            log "${RED}❌ 部署脚本不存在: ${DEPLOY_SCRIPT}${NC}"
            exit 1
        fi
        
        chmod +x "$DEPLOY_SCRIPT"
        if ! "$DEPLOY_SCRIPT" ${NAMESPACE} >> "$LOG_FILE" 2>&1; then
            log "${RED}❌ 部署失败!${NC}"
            log "${YELLOW}查看日志文件了解详情: ${LOG_FILE}${NC}"
            exit 1
        else
            log "${GREEN}✅ 部署脚本执行成功${NC}"
        fi

        # 8. 验证部署
        log "\n${BLUE}步骤8: 验证部署...${NC}"
        log "${YELLOW}等待Pod就绪...${NC}"
        if kubectl rollout status deployment/knowledge-graph-service -n ${NAMESPACE} --timeout=300s >> "$LOG_FILE" 2>&1; then
            log "${GREEN}✅ 部署成功${NC}"
        else
            log "${RED}❌ 部署未在指定时间内完成!${NC}"
            log "${YELLOW}请手动检查部署状态:${NC}"
            log "kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=knowledge-graph-service"
            
            # 显示当前Pod状态，即使有错误
            POD_STATUS=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=knowledge-graph-service 2>/dev/null || echo "无法获取Pod状态")
            log "\n${BLUE}当前Pod状态:${NC}\n${POD_STATUS}"
            
            # 在CI环境中，我们认为这是失败的
            if [ "${CI}" == "true" ]; then
                exit 1
            fi
        fi
    fi
else
    log "\n${BLUE}步骤7-8: 跳过Kubernetes部署${NC}"
fi

log "\n${GREEN}✅ CI/CD流程已完成!${NC}"
log "${BLUE}==============================================${NC}"
log "${GREEN}镜像信息:${NC}"
log "${YELLOW}多架构镜像: ${TAG}${NC}"
log "${YELLOW}AMD64镜像: ${AMD64_TAG}${NC}"
if [ "${BUILD_ARM64}" == "true" ]; then
    log "${YELLOW}ARM64镜像: ${ARM64_TAG}${NC}"
fi
log "${BLUE}==============================================${NC}"

# 如果是在CI环境中运行，创建输出文件供后续步骤使用
if [ "${CI}" == "true" ]; then
    mkdir -p ./artifacts
    echo "${VERSION}" > ./artifacts/version.txt
    echo "${TAG}" > ./artifacts/image.txt
    echo "${AMD64_TAG}" > ./artifacts/image-amd64.txt
    echo "${ARM64_TAG}" > ./artifacts/image-arm64.txt
    echo "${DEPLOY_DATE:-$(date +'%Y-%m-%dT%H:%M:%S')}" > ./artifacts/deploy-date.txt
    
    log "${BLUE}已创建构建信息文件，供CI/CD后续步骤使用${NC}"
fi

log "${GREEN}详细日志已保存到: ${LOG_FILE}${NC}"