#!/bin/bash

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

echo -e "${YELLOW}索克生活微服务生产环境部署脚本${NC}"

# 加载生产环境配置
if [ ! -f ".env.production" ]; then
    echo -e "${RED}错误: 未找到生产环境配置文件 .env.production${NC}"
    exit 1
fi

# 导出环境变量
export $(grep -v '^#' .env.production | xargs)

# 检查必要参数
if [ -z "$PROD_SERVER" ] || [ -z "$SSH_USER" ] || [ -z "$SSH_KEY" ]; then
    echo -e "${RED}错误: 生产服务器配置不完整${NC}"
    echo "请检查 .env.production 中的 PROD_SERVER, SSH_USER, SSH_KEY 配置"
    exit 1
fi

# 检查SSH密钥
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}错误: SSH密钥文件不存在: $SSH_KEY${NC}"
    exit 1
fi

# 构建服务镜像
build_and_push_images() {
    echo -e "${YELLOW}构建并推送服务镜像...${NC}"
    
    # 登录到阿里云容器镜像仓库
    echo -e "${YELLOW}登录到阿里云容器镜像仓库...${NC}"
    docker login --username "$ALIYUN_USERNAME" --password "$ALIYUN_PASSWORD" "$ALIYUN_REGISTRY"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}登录阿里云失败${NC}"
        exit 1
    fi
    
    # 构建API网关服务
    echo -e "${YELLOW}构建API网关服务...${NC}"
    cd api-gateway
    docker build -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/api-gateway:$VERSION .
    docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/api-gateway:$VERSION
    cd ..
    
    # 构建认证服务
    echo -e "${YELLOW}构建认证服务...${NC}"
    cd auth-service
    docker build -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/auth-service:$VERSION .
    docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/auth-service:$VERSION
    cd ..
    
    # 构建用户服务
    echo -e "${YELLOW}构建用户服务...${NC}"
    cd user-service
    docker build -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/user-service:$VERSION .
    docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/user-service:$VERSION
    cd ..
    
    echo -e "${GREEN}镜像构建并推送完成${NC}"
}

# 部署到生产服务器
deploy_to_server() {
    echo -e "${YELLOW}部署到生产服务器 $PROD_SERVER...${NC}"
    
    # 测试SSH连接
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$PROD_SERVER" "echo 连接成功"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}无法连接到生产服务器${NC}"
        exit 1
    fi
    
    # 创建目录结构
    echo -e "${YELLOW}准备服务器目录...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "mkdir -p /var/www/suoke.life/logs/{api-gateway,auth-service,user-service}"
    
    # 复制配置文件
    echo -e "${YELLOW}复制配置文件...${NC}"
    scp -i "$SSH_KEY" docker-compose.prod.yml "$SSH_USER@$PROD_SERVER:/var/www/suoke.life/docker-compose.yml"
    scp -i "$SSH_KEY" .env.production "$SSH_USER@$PROD_SERVER:/var/www/suoke.life/.env"
    
    # 复制服务配置
    for service in api-gateway auth-service user-service; do
        if [ -d "./$service/configs" ]; then
            ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "mkdir -p /var/www/suoke.life/$service/configs"
            scp -i "$SSH_KEY" ./$service/configs/* "$SSH_USER@$PROD_SERVER:/var/www/suoke.life/$service/configs/"
        fi
    done
    
    # 登录到阿里云容器镜像仓库并部署
    echo -e "${YELLOW}在服务器上登录到阿里云并部署服务...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "cd /var/www/suoke.life && \
        docker login --username $ALIYUN_USERNAME --password $ALIYUN_PASSWORD $ALIYUN_REGISTRY && \
        docker-compose pull && \
        docker-compose up -d"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}部署失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}部署完成${NC}"
}

# 检查服务状态
check_service_status() {
    echo -e "${YELLOW}检查服务状态...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "cd /var/www/suoke.life && docker-compose ps"
    
    echo -e "\n${YELLOW}服务日志 (最新10行)${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "cd /var/www/suoke.life && docker-compose logs --tail=10"
}

# 执行主流程
main() {
    echo -e "${YELLOW}开始生产环境部署流程...${NC}"
    
    # 询问是否构建镜像
    read -p "是否构建并推送镜像? [y/N] " BUILD_IMAGES
    if [[ "$BUILD_IMAGES" =~ ^[Yy]$ ]]; then
        build_and_push_images
    fi
    
    # 确认部署
    echo -e "${YELLOW}准备部署到生产服务器 $PROD_SERVER${NC}"
    read -p "确认部署? [y/N] " CONFIRM_DEPLOY
    if [[ ! "$CONFIRM_DEPLOY" =~ ^[Yy]$ ]]; then
        echo -e "${RED}部署已取消${NC}"
        exit 0
    fi
    
    deploy_to_server
    check_service_status
    
    echo -e "\n${GREEN}生产环境部署完成!${NC}"
    echo -e "${YELLOW}API网关地址: http://$PROD_SERVER:$API_GATEWAY_PORT${NC}"
}

# 执行主函数
main