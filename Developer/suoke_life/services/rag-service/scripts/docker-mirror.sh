#!/bin/bash

# 定义彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}配置Docker镜像加速...${NC}"

# 检查操作系统类型
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS系统
    echo -e "${YELLOW}检测到macOS系统${NC}"
    
    # 创建Docker配置目录
    mkdir -p ~/.docker
    
    # 检查配置文件是否存在
    if [ -f ~/.docker/config.json ]; then
        echo -e "${YELLOW}配置文件已存在，将合并配置...${NC}"
        # 备份现有配置
        cp ~/.docker/config.json ~/.docker/config.json.bak
    fi
    
    # 写入新配置
    cat > ~/.docker/config.json <<EOF
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
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
    
    # 重启Docker
    echo -e "${YELLOW}正在重启Docker Desktop...${NC}"
    osascript -e 'quit app "Docker Desktop"'
    open -a "Docker Desktop"
    echo -e "${GREEN}已发送重启Docker Desktop命令，请等待服务重新启动完成${NC}"

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux系统
    echo -e "${YELLOW}检测到Linux系统${NC}"
    
    # 创建配置目录
    sudo mkdir -p /etc/docker
    
    # 写入配置
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "experimental": true
}
EOF
    
    # 重启Docker服务
    echo -e "${YELLOW}正在重启Docker服务...${NC}"
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    echo -e "${GREEN}Docker服务已重启${NC}"
else
    echo -e "${RED}不支持的操作系统类型: $OSTYPE${NC}"
    exit 1
fi

echo -e "${GREEN}Docker镜像加速配置完成!${NC}"
echo -e "${YELLOW}提示: 如果Docker仍在启动中，请等待一些时间再执行Docker命令${NC}" 