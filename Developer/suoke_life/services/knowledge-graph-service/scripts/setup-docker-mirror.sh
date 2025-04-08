#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}  Docker镜像加速器配置脚本  ${NC}"
echo -e "${BLUE}==============================================${NC}"

# 检测操作系统
OS=$(uname -s)
echo -e "${BLUE}检测到操作系统: ${OS}${NC}"

# 阿里云镜像加速地址
ALIYUN_MIRROR="https://xsl7dpc7.mirror.aliyuncs.com"

case "$OS" in
  Darwin)
    # macOS配置
    echo -e "${BLUE}为macOS配置Docker镜像加速...${NC}"
    
    # 检查Docker Desktop是否存在
    if [ -f ~/Library/Group\ Containers/group.com.docker/settings.json ]; then
      # 备份当前配置
      cp ~/Library/Group\ Containers/group.com.docker/settings.json ~/Library/Group\ Containers/group.com.docker/settings.json.bak
      
      # 更新配置
      cat > ~/Library/Group\ Containers/group.com.docker/settings.json << EOF
{
  "registry-mirrors": [
    "${ALIYUN_MIRROR}",
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "experimental": true,
  "builder": {
    "gc": {
      "enabled": true,
      "defaultKeepStorage": "20GB"
    }
  }
}
EOF
      echo -e "${GREEN}✅ Docker Desktop 镜像加速配置已更新${NC}"
      echo -e "${YELLOW}请重启Docker Desktop应用使配置生效${NC}"
    else
      echo -e "${RED}未找到Docker Desktop配置文件，请手动配置镜像加速器${NC}"
      echo -e "${YELLOW}在Docker Desktop -> Settings -> Docker Engine中添加:${NC}"
      echo -e '  "registry-mirrors": ['
      echo -e "    \"${ALIYUN_MIRROR}\","
      echo -e '    "https://registry.cn-hangzhou.aliyuncs.com",'
      echo -e '    "https://docker.mirrors.ustc.edu.cn",'
      echo -e '    "https://hub-mirror.c.163.com"'
      echo -e '  ]'
    fi
    ;;
    
  Linux)
    # Linux配置
    echo -e "${BLUE}为Linux配置Docker镜像加速...${NC}"
    
    # 检查是否为root用户
    if [ "$(id -u)" != "0" ]; then
      echo -e "${RED}请使用root权限运行此脚本${NC}"
      exit 1
    fi
    
    # 创建daemon.json配置
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "${ALIYUN_MIRROR}",
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn", 
    "https://hub-mirror.c.163.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "experimental": true
}
EOF
    
    # 重启Docker服务
    echo -e "${BLUE}重启Docker服务...${NC}"
    if command -v systemctl > /dev/null; then
      systemctl daemon-reload
      systemctl restart docker
      echo -e "${GREEN}✅ Docker服务已重启${NC}"
    else
      service docker restart
      echo -e "${GREEN}✅ Docker服务已重启${NC}"
    fi
    ;;
    
  *)
    echo -e "${RED}不支持的操作系统: ${OS}${NC}"
    echo -e "${YELLOW}请手动配置Docker镜像加速器${NC}"
    exit 1
    ;;
esac

echo -e "\n${BLUE}配置Kubernetes镜像拉取密钥...${NC}"
echo -e "${YELLOW}创建Docker Registry密钥:${NC}"
echo -e "kubectl create secret docker-registry aliyun-registry-secret \\"
echo -e "  --namespace=suoke-prod \\"
echo -e "  --docker-server=registry.cn-hangzhou.aliyuncs.com \\"
echo -e "  --docker-username=<用户名> \\"
echo -e "  --docker-password=<密码> \\"
echo -e "  --docker-email=<邮箱>"

echo -e "\n${BLUE}修改Kubernetes服务账户使用镜像拉取密钥:${NC}"
echo -e "kubectl patch serviceaccount knowledge-graph-service \\"
echo -e "  -n suoke-prod \\"
echo -e "  -p '{\"imagePullSecrets\": [{\"name\": \"aliyun-registry-secret\"}]}'"

echo -e "\n${GREEN}✅ 配置完成!${NC}"
echo -e "${BLUE}==============================================${NC}"