#!/bin/bash

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 显示帮助信息
show_help() {
    echo -e "${YELLOW}索克生活微服务SSH直接部署脚本${NC}"
    echo ""
    echo -e "用法: $0 [选项]"
    echo ""
    echo -e "选项:"
    echo "  -e, --env <环境>      指定部署环境: dev(开发)或prod(生产) [默认: dev]"
    echo "  -t, --test            部署前运行测试"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo -e "示例:"
    echo "  $0 -e dev             直接部署到开发环境"
    echo "  $0 -e prod -t         运行测试后直接部署到生产环境"
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
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "mkdir -p /var/www/suoke.life/services"
    
    # 创建各个服务的目录
    for service in api-gateway auth-service user-service; do
        echo -e "${YELLOW}为$service创建目录...${NC}"
        ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "mkdir -p /var/www/suoke.life/services/$service"
    done
    
    # 复制代码到远程服务器
    echo -e "${YELLOW}复制代码到远程服务器...${NC}"
    
    # 复制docker-compose文件
    scp -i "$SSH_KEY" docker-compose.yml "$SSH_USER@$SERVER:/var/www/suoke.life/services/"
    
    # 复制环境变量文件
    scp -i "$SSH_KEY" .env "$SSH_USER@$SERVER:/var/www/suoke.life/services/" 2>/dev/null || scp -i "$SSH_KEY" .env-example "$SSH_USER@$SERVER:/var/www/suoke.life/services/.env"
    
    # 复制各服务的源代码
    for service in api-gateway auth-service user-service; do
        echo -e "${YELLOW}复制$service源代码...${NC}"
        
        # 创建压缩包然后复制
        tar -czf "$service.tar.gz" ./$service/
        scp -i "$SSH_KEY" "$service.tar.gz" "$SSH_USER@$SERVER:/var/www/suoke.life/services/"
        
        # 在远程服务器上解压
        ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life/services/ && tar -xzf $service.tar.gz && rm $service.tar.gz"
        
        # 删除本地压缩包
        rm "$service.tar.gz"
    done
    
    # 复制脚本目录
    echo -e "${YELLOW}复制脚本目录...${NC}"
    tar -czf "scripts.tar.gz" ./scripts/
    scp -i "$SSH_KEY" "scripts.tar.gz" "$SSH_USER@$SERVER:/var/www/suoke.life/services/"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life/services/ && tar -xzf scripts.tar.gz && rm scripts.tar.gz && chmod +x scripts/*.sh"
    rm "scripts.tar.gz"
    
    # 复制初始化脚本
    if [ -d "./init-scripts" ]; then
        echo -e "${YELLOW}复制初始化脚本...${NC}"
        tar -czf "init-scripts.tar.gz" ./init-scripts/
        scp -i "$SSH_KEY" "init-scripts.tar.gz" "$SSH_USER@$SERVER:/var/www/suoke.life/services/"
        ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life/services/ && tar -xzf init-scripts.tar.gz && rm init-scripts.tar.gz && chmod +x init-scripts/*.sh"
        rm "init-scripts.tar.gz"
    fi
    
    # 在远程服务器上构建并启动服务
    echo -e "${YELLOW}在远程服务器上构建并启动服务...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life/services && chmod +x scripts/*.sh && ./scripts/docker-compose-env.sh build && ./scripts/docker-compose-env.sh up -d"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}部署失败${NC}"
        exit 1
    fi
    
    # 检查服务状态
    echo -e "${YELLOW}检查服务状态...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER" "cd /var/www/suoke.life/services && ./scripts/docker-compose-env.sh ps"
    
    echo -e "${GREEN}部署成功${NC}"
}

# 主函数
main() {
    # 设置默认值
    ENV=${ENV:-"dev"}
    RUN_TESTS=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENV="$2"
                shift 2
                ;;
            -t|--test)
                RUN_TESTS=true
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
    if [ "$ENV" == "prod" ]; then
        echo -e "${YELLOW}警告: 即将部署到生产环境${NC}"
        read -p "确认继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}部署取消${NC}"
            exit 1
        fi
    fi
    
    echo -e "${YELLOW}开始部署到${ENV}环境${NC}"
    
    # 加载环境变量
    load_env
    
    # 运行测试
    if [ "$RUN_TESTS" == "true" ]; then
        run_tests
    fi
    
    # 部署到远程服务器
    deploy_to_remote
    
    echo -e "${GREEN}部署完成!${NC}"
    echo -e "环境: ${ENV}"
    echo -e "服务器: ${SERVER}"
}

# 执行主函数
main "$@" 