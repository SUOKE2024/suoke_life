#!/bin/bash

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 显示帮助信息
show_help() {
    echo -e "${YELLOW}索克生活微服务本地部署脚本${NC}"
    echo ""
    echo -e "用法: $0 [选项]"
    echo ""
    echo -e "选项:"
    echo "  -t, --test            部署前运行测试"
    echo "  -b, --build           部署前构建镜像"
    echo "  -c, --clean           部署后清理本地环境"
    echo "  -y, --yes             自动确认所有提示"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo -e "示例:"
    echo "  $0 -b                 构建并部署到本地环境"
    echo "  $0 -t -c              运行测试后部署到本地环境，并清理"
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

# 部署到本地环境
deploy_local() {
    echo -e "${YELLOW}部署到本地环境...${NC}"
    
    echo -e "${YELLOW}启动服务...${NC}"
    ./scripts/docker-compose-env.sh up -d
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}部署失败${NC}"
        exit 1
    fi
    
    # 检查服务状态
    echo -e "${YELLOW}检查服务状态...${NC}"
    ./scripts/docker-compose-env.sh ps
    
    echo -e "${GREEN}部署成功${NC}"
    echo -e "API网关可以通过以下地址访问: http://localhost:${API_GATEWAY_PORT}"
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
    RUN_TESTS=false
    BUILD_IMAGES=false
    CLEAN_AFTER=false
    AUTO_CONFIRM=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--test)
                RUN_TESTS=true
                shift
                ;;
            -b|--build)
                BUILD_IMAGES=true
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
    
    echo -e "${YELLOW}开始本地部署${NC}"
    
    # 加载环境变量
    load_env
    
    # 运行测试
    if [ "$RUN_TESTS" == "true" ]; then
        run_tests
    fi
    
    # 构建镜像
    if [ "$BUILD_IMAGES" == "true" ]; then
        build_images
    fi
    
    # 部署到本地环境
    deploy_local
    
    # 清理本地环境
    if [ "$CLEAN_AFTER" == "true" ]; then
        clean_local
    fi
    
    echo -e "${GREEN}部署完成!${NC}"
}

# 执行主函数
main "$@" 