#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Docker网络代理配置与镜像构建 =====${NC}"

# 默认代理配置
HTTP_PROXY=${HTTP_PROXY:-"http://127.0.0.1:7890"}
HTTPS_PROXY=${HTTPS_PROXY:-"http://127.0.0.1:7890"}
NO_PROXY=${NO_PROXY:-"localhost,127.0.0.1,internal.domain"}

# 检查当前目录是否包含.env文件
if [ ! -f .env ]; then
    echo -e "${RED}错误：当前目录中没有找到.env文件${NC}"
    echo -e "${YELLOW}请确保在知识库服务目录中运行此脚本${NC}"
    exit 1
fi

# 从.env文件加载配置
source .env

# 检查必要的环境变量
if [ -z "$REGISTRY_URL" ] || [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
    echo -e "${RED}错误：容器镜像仓库配置不完整${NC}"
    echo -e "${YELLOW}请在.env文件中设置以下变量：${NC}"
    echo -e "REGISTRY_URL=registry.cn-hangzhou.aliyuncs.com"
    echo -e "REGISTRY_USERNAME=<您的阿里云容器镜像服务用户名>"
    echo -e "REGISTRY_PASSWORD=<您的阿里云容器镜像服务密码>"
    exit 1
fi

# 配置Docker守护进程代理
setup_docker_proxy() {
    echo -e "${YELLOW}正在配置Docker守护进程代理...${NC}"
    
    # 创建或更新Docker配置目录
    mkdir -p ~/.docker
    
    # 检查Docker配置文件是否存在
    if [ ! -f ~/.docker/config.json ]; then
        echo "{}" > ~/.docker/config.json
    fi
    
    # 创建临时配置文件
    local temp_config=$(mktemp)
    cat << EOF > $temp_config
{
  "proxies": {
    "default": {
      "httpProxy": "$HTTP_PROXY",
      "httpsProxy": "$HTTPS_PROXY",
      "noProxy": "$NO_PROXY"
    }
  }
}
EOF

    # 合并配置文件
    jq -s '.[0] * .[1]' ~/.docker/config.json $temp_config > ~/.docker/config.json.new
    mv ~/.docker/config.json.new ~/.docker/config.json
    rm $temp_config
    
    echo -e "${GREEN}Docker代理配置完成！${NC}"
    echo -e "${YELLOW}HTTP_PROXY: $HTTP_PROXY${NC}"
    echo -e "${YELLOW}HTTPS_PROXY: $HTTPS_PROXY${NC}"
    echo -e "${YELLOW}NO_PROXY: $NO_PROXY${NC}"
    
    # 注：此更改需要重启Docker守护进程才能生效
    echo -e "${YELLOW}请重启Docker守护进程以使更改生效${NC}"
    echo -e "Mac用户: 右击Docker桌面客户端图标 > Restart"
    echo -e "Linux用户: sudo systemctl restart docker"
}

# 构建并推送Docker镜像
build_and_push_image() {
    echo -e "${YELLOW}准备构建并推送Knowledge Base Service镜像...${NC}"
    
    # 获取版本信息
    VERSION=$(make version | tail -n 1)
    if [ -z "$VERSION" ]; then
        VERSION=$(git describe --tags --always --dirty || echo "dev")
    fi
    
    # 构建完整的镜像名称和标签
    IMAGE_NAME="${REGISTRY_URL}/suoke/knowledge-base-service"
    IMAGE_TAG="${VERSION}"
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
    
    echo -e "${YELLOW}镜像名称: $FULL_IMAGE_NAME${NC}"
    
    # 登录到容器镜像仓库
    echo -e "${YELLOW}登录到容器镜像仓库...${NC}"
    echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY_URL" -u "$REGISTRY_USERNAME" --password-stdin
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}登录失败，请检查凭据${NC}"
        exit 1
    fi
    
    # 设置构建环境变量
    export DOCKER_BUILDKIT=1
    export HTTP_PROXY
    export HTTPS_PROXY
    export NO_PROXY
    
    # 构建Docker镜像
    echo -e "${YELLOW}构建Docker镜像...${NC}"
    docker build --build-arg HTTP_PROXY="$HTTP_PROXY" \
                 --build-arg HTTPS_PROXY="$HTTPS_PROXY" \
                 --build-arg NO_PROXY="$NO_PROXY" \
                 -t "$FULL_IMAGE_NAME" .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}镜像构建失败${NC}"
        exit 1
    fi
    
    # 推送镜像到仓库
    echo -e "${YELLOW}推送镜像到仓库...${NC}"
    docker push "$FULL_IMAGE_NAME"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}镜像推送失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}镜像构建和推送成功: $FULL_IMAGE_NAME${NC}"
    
    # 添加latest标签并推送
    echo -e "${YELLOW}添加latest标签并推送...${NC}"
    docker tag "$FULL_IMAGE_NAME" "${IMAGE_NAME}:latest"
    docker push "${IMAGE_NAME}:latest"
    
    echo -e "${GREEN}所有操作完成！${NC}"
}

# 显示帮助信息
show_help() {
    echo -e "使用方法: $0 [选项]"
    echo -e "选项:"
    echo -e "  -p, --proxy   配置Docker守护进程代理"
    echo -e "  -b, --build   构建并推送Docker镜像"
    echo -e "  -a, --all     执行所有操作(默认)"
    echo -e "  -h, --help    显示此帮助信息"
    echo
    echo -e "环境变量:"
    echo -e "  HTTP_PROXY    设置HTTP代理(默认: http://127.0.0.1:7890)"
    echo -e "  HTTPS_PROXY   设置HTTPS代理(默认: http://127.0.0.1:7890)"
    echo -e "  NO_PROXY      设置不使用代理的地址(默认: localhost,127.0.0.1,internal.domain)"
    echo
    echo -e "示例:"
    echo -e "  $0 --proxy"
    echo -e "  HTTP_PROXY=http://10.0.0.1:1080 $0 --all"
}

# 主函数
main() {
    # 参数为空时执行所有操作
    if [ $# -eq 0 ]; then
        setup_docker_proxy
        build_and_push_image
        exit 0
    fi
    
    # 解析命令行参数
    while [ $# -gt 0 ]; do
        case "$1" in
            -p|--proxy)
                setup_docker_proxy
                shift
                ;;
            -b|--build)
                build_and_push_image
                shift
                ;;
            -a|--all)
                setup_docker_proxy
                build_and_push_image
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}未知选项: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# 执行主函数
main "$@" 