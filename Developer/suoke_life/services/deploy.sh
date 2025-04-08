#!/bin/bash

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 显示帮助信息
show_help() {
    echo -e "${YELLOW}索克生活微服务部署脚本${NC}"
    echo ""
    echo -e "用法: $0 [选项]"
    echo ""
    echo -e "选项:"
    echo "  -e, --env <环境>      指定部署环境: dev(开发)或prod(生产) [默认: dev]"
    echo "  -v, --version <版本>  指定版本标签 [默认: latest]"
    echo "  -t, --test            部署前运行测试"
    echo "  -b, --build           部署前构建镜像"
    echo "  -p, --push            构建后推送镜像到阿里云"
    echo "  -c, --clean           部署后清理本地环境"
    echo "  -y, --yes             自动确认所有提示"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo -e "示例:"
    echo "  $0 -e dev -v 1.0.0 -b -p  构建v1.0.0版本并部署到开发环境"
    echo "  $0 -e prod -t -c         运行测试后部署到生产环境，并清理"
    echo ""
    exit 1
}

# 加载环境变量文件
load_env() {
    local env_file=".env"
    
    if [ ! -f "$env_file" ]; then
        if [ -f ".env-example" ]; then
            echo -e "${YELLOW}警告: .env文件不存在，将使用.env-example${NC}"
            echo -e "建议复制.env-example为.env并设置适当的值"
            env_file=".env-example"
        else
            echo -e "${RED}错误: 未找到环境变量文件${NC}"
            exit 1
        fi
    fi
    
    echo -e "${YELLOW}加载环境变量: $env_file${NC}"
    export $(grep -v '^#' "$env_file" | xargs)
    
    # 根据指定环境覆盖变量
    if [ "$ENV" == "prod" ]; then
        export SERVER="${PROD_SERVER}"
    else
        export SERVER="${DEV_SERVER}"
    fi
    
    echo -e "${GREEN}环境变量加载完成${NC}"
}

# 检查阿里云登录凭证
check_aliyun_login() {
    if [ -z "$ALIYUN_USERNAME" ] || [ -z "$ALIYUN_PASSWORD" ]; then
        echo -e "${RED}错误: 未设置阿里云容器镜像仓库凭证${NC}"
        echo -e "请在.env文件中设置ALIYUN_USERNAME和ALIYUN_PASSWORD"
        exit 1
    fi
    
    # 登录到阿里云容器镜像仓库
    echo -e "${YELLOW}登录到阿里云容器镜像仓库...${NC}"
    docker login --username "$ALIYUN_USERNAME" --password "$ALIYUN_PASSWORD" "$ALIYUN_REGISTRY"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}登录失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}登录成功${NC}"
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}运行测试...${NC}"
    
    cd tests
    ./run_tests.sh
    local result=$?
    cd ..
    
    if [ $result -ne 0 ]; then
        echo -e "${RED}测试失败，中止部署${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}测试通过${NC}"
}

# 构建Docker镜像
build_images() {
    echo -e "${YELLOW}构建Docker镜像...${NC}"
    
    # 使用docker-compose构建镜像
    ./scripts/docker-compose-env.sh build
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}构建失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}构建成功${NC}"
}

# 推送镜像到阿里云
push_images() {
    echo -e "${YELLOW}推送镜像到阿里云...${NC}"
    
    check_aliyun_login
    
    # 使用docker-compose推送镜像
    ./scripts/docker-compose-env.sh push
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}推送失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}推送成功${NC}"
}

# 部署到远程服务器
deploy_to_remote() {
    echo -e "${YELLOW}部署到${ENV}环境 (${SERVER})...${NC}"
    
    if [ -z "$SERVER" ]; then
        echo -e "${RED}错误: 未指定服务器地址${NC}"
        echo -e "请在.env文件中设置DEV_SERVER或PROD_SERVER"
        exit 1
    fi
    
    # 检查SSH登录信息
    if [ -z "$SSH_USER" ] || [ -z "$SSH_KEY" ]; then
        echo -e "${RED}错误: 未设置SSH连接信息${NC}"
        echo -e "请在.env文件中设置SSH_USER和SSH_KEY"
        exit 1
    fi
    
    # 检查SSH密钥文件
    if [ ! -f "$SSH_KEY" ]; then
        echo -e "${RED}错误: SSH密钥文件不存在: $SSH_KEY${NC}"
        exit 1
    fi
    
    # 测试SSH连接
    echo -e "${YELLOW}测试SSH连接...${NC}"
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER" "echo 连接成功"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}SSH连接失败${NC}"
        exit 1
    fi
    
    # 准备远程目录
    echo -e "${YELLOW}准备远程目录...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "mkdir -p /var/www/suoke.life"
    
    # 复制必要文件到远程服务器
    echo -e "${YELLOW}复制文件到远程服务器...${NC}"
    
    # 复制docker-compose文件
    scp -i "$SSH_KEY" docker-compose.yml "$SSH_USER@$SERVER:/var/www/suoke.life/"
    
    # 复制环境变量文件
    scp -i "$SSH_KEY" .env "$SSH_USER@$SERVER:/var/www/suoke.life/" 2>/dev/null || scp -i "$SSH_KEY" .env-example "$SSH_USER@$SERVER:/var/www/suoke.life/.env"
    
    # 复制配置文件
    for service in api-gateway auth-service user-service; do
        if [ -d "./$service/configs" ]; then
            ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "mkdir -p /var/www/suoke.life/$service/configs"
            scp -i "$SSH_KEY" ./$service/configs/* "$SSH_USER@$SERVER:/var/www/suoke.life/$service/configs/"
        fi
    done
    
    # 复制初始化脚本
    if [ -d "./init-scripts" ]; then
        ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "mkdir -p /var/www/suoke.life/init-scripts"
        scp -i "$SSH_KEY" ./init-scripts/* "$SSH_USER@$SERVER:/var/www/suoke.life/init-scripts/"
    fi
    
    # 在远程服务器上登录到阿里云容器镜像仓库
    echo -e "${YELLOW}在远程服务器上登录到阿里云容器镜像仓库...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "docker login --username $ALIYUN_USERNAME --password $ALIYUN_PASSWORD $ALIYUN_REGISTRY"
    
    # 在远程服务器上拉取并启动服务
    echo -e "${YELLOW}在远程服务器上拉取并启动服务...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life && docker-compose pull && docker-compose up -d"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}部署失败${NC}"
        exit 1
    fi
    
    # 检查服务状态
    echo -e "${YELLOW}检查服务状态...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life && docker-compose ps"
    
    echo -e "${GREEN}部署成功${NC}"
}

# 清理本地环境
clean_local() {
    echo -e "${YELLOW}清理本地环境...${NC}"
    
    if [ "$AUTO_CONFIRM" != "true" ]; then
        read -p "确认清理本地Docker环境? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}跳过清理${NC}"
            return
        fi
    fi
    
    # 使用docker-compose停止和移除容器
    ./scripts/docker-compose-env.sh down -v
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}清理失败${NC}"
    else
        echo -e "${GREEN}清理成功${NC}"
    fi
}

# 主函数
main() {
    # 设置默认值
    ENV=${ENV:-"dev"}
    VERSION=${VERSION:-"latest"}
    RUN_TESTS=false
    BUILD_IMAGES=false
    PUSH_IMAGES=false
    CLEAN_AFTER=false
    AUTO_CONFIRM=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENV="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -t|--test)
                RUN_TESTS=true
                shift
                ;;
            -b|--build)
                BUILD_IMAGES=true
                shift
                ;;
            -p|--push)
                PUSH_IMAGES=true
                shift
                ;;
            -c|--clean)
                CLEAN_AFTER=true
                shift
                ;;
            -y|--yes)
                AUTO_CONFIRM=true
                shift
                ;;
            -h|--help)
                show_help
                ;;
            *)
                echo -e "${RED}错误: 未知参数 $1${NC}"
                show_help
                ;;
        esac
    done
    
    # 参数验证
    if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
        echo -e "${RED}错误: 环境必须是dev或prod${NC}"
        exit 1
    fi
    
    # 确认生产环境部署
    if [ "$ENV" == "prod" ] && [ "$AUTO_CONFIRM" != "true" ]; then
        echo -e "${YELLOW}警告: 即将部署到生产环境${NC}"
        read -p "确认继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}部署取消${NC}"
            exit 1
        fi
    fi
    
    echo -e "${YELLOW}开始部署到${ENV}环境，版本: ${VERSION}${NC}"
    
    # 加载环境变量
    load_env
    
    # 运行测试
    if [ "$RUN_TESTS" == "true" ]; then
        run_tests
    fi
    
    # 构建镜像
    if [ "$BUILD_IMAGES" == "true" ]; then
        build_images
        
        # 推送镜像
        if [ "$PUSH_IMAGES" == "true" ]; then
            push_images
        fi
    fi
    
    # 部署到远程服务器
    deploy_to_remote
    
    # 清理本地环境
    if [ "$CLEAN_AFTER" == "true" ]; then
        clean_local
    fi
    
    echo -e "${GREEN}部署完成!${NC}"
    echo -e "环境: ${ENV}"
    echo -e "版本: ${VERSION}"
    echo -e "服务器: ${SERVER}"
}

# 执行主函数
main "$@" 