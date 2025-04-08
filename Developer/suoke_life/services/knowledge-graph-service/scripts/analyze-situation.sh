#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}   索克生活知识图谱服务部署问题分析脚本   ${NC}"
echo -e "${BLUE}==============================================${NC}"

# 获取本地信息
echo -e "\n${BLUE}本地环境信息:${NC}"
echo -e "${YELLOW}操作系统: $(uname -a)${NC}"
echo -e "${YELLOW}Docker版本: $(docker --version 2>/dev/null || echo '未安装')${NC}"
echo -e "${YELLOW}本地架构: $(uname -m)${NC}"

# 获取集群信息
echo -e "\n${BLUE}Kubernetes集群信息:${NC}"
CLUSTER_INFO=$(kubectl cluster-info 2>/dev/null)
if [ $? -ne 0 ]; then
    echo -e "${RED}无法连接到Kubernetes集群${NC}"
else
    echo -e "${YELLOW}$(echo "$CLUSTER_INFO" | head -n 2)${NC}"
    echo -e "${YELLOW}Kubernetes版本: $(kubectl version --short 2>/dev/null | grep 'Server Version' || echo '未知')${NC}"
fi

# 获取节点信息
echo -e "\n${BLUE}集群节点架构信息:${NC}"
NODE_INFO=$(kubectl get nodes -o wide 2>/dev/null)
if [ $? -ne 0 ]; then
    echo -e "${RED}无法获取节点信息${NC}"
else
    echo -e "${YELLOW}$(echo "$NODE_INFO" | head -n 1)${NC}"
    echo -e "${YELLOW}$(echo "$NODE_INFO" | grep -v 'NAME' | cut -d' ' -f1,12 | sed 's/containerd.*//')${NC}"
    NODE_ARCH=$(echo "$NODE_INFO" | grep -v 'NAME' | grep 'x86_64' > /dev/null && echo "x86_64 (AMD64)" || echo "非AMD64")
    echo -e "${YELLOW}节点架构: ${NODE_ARCH}${NC}"
fi

# 检查Pod状态
echo -e "\n${BLUE}当前Pod状态:${NC}"
POD_INFO=$(kubectl get pods -n suoke-prod -l app.kubernetes.io/name=knowledge-graph-service 2>/dev/null)
if [ $? -ne 0 ]; then
    echo -e "${RED}无法获取Pod信息${NC}"
else
    echo -e "${YELLOW}$(echo "$POD_INFO")${NC}"
    POD_NAME=$(echo "$POD_INFO" | grep -v NAME | awk '{print $1}')
    if [ -n "$POD_NAME" ]; then
        POD_LOGS=$(kubectl logs -n suoke-prod $POD_NAME 2>/dev/null)
        echo -e "\n${BLUE}Pod日志:${NC}"
        echo -e "${YELLOW}$(echo "$POD_LOGS" | head -n 10)${NC}"
        
        if echo "$POD_LOGS" | grep -q "exec format error"; then
            echo -e "\n${RED}发现架构不匹配问题: exec format error${NC}"
            ARCH_MISMATCH="是"
        else
            ARCH_MISMATCH="否"
        fi
    fi
fi

# 检查镜像
echo -e "\n${BLUE}本地镜像信息:${NC}"
IMAGE_INFO=$(docker images | grep knowledge-graph-service)
if [ $? -ne 0 ]; then
    echo -e "${RED}未找到相关镜像${NC}"
else
    echo -e "${YELLOW}$(echo "$IMAGE_INFO" | head -n 5)${NC}"
fi

# 问题分析和解决方案
echo -e "\n${BLUE}==============================================${NC}"
echo -e "${GREEN}               问题分析               ${NC}"
echo -e "${BLUE}==============================================${NC}"

if [ "$ARCH_MISMATCH" = "是" ]; then
    echo -e "\n${RED}1. 架构不匹配问题${NC}"
    echo -e "   本地架构: $(uname -m)"
    echo -e "   集群节点架构: ${NODE_ARCH}"
    echo -e "   问题: 在ARM64架构上构建的镜像无法在AMD64节点上运行"
    
    echo -e "\n${GREEN}解决方案:${NC}"
    echo -e "1. 使用支持多架构构建的Docker功能:"
    echo -e "   - 安装并设置docker buildx"
    echo -e "   - 使用buildx创建多平台镜像"
    
    echo -e "\n2. 在AMD64机器上构建镜像:"
    echo -e "   - 使用CI/CD系统在AMD64环境中构建"
    echo -e "   - 在AMD64虚拟机或云实例上构建"
    
    echo -e "\n3. 使用我们准备的AMD64专用Dockerfile:"
    echo -e "   - 在Dockerfile.amd64中明确指定平台为linux/amd64"
    echo -e "   - 使用--platform=linux/amd64参数进行构建"
fi

echo -e "\n${BLUE}==============================================${NC}"
echo -e "${GREEN}             推荐执行步骤             ${NC}"
echo -e "${BLUE}==============================================${NC}"

echo -e "\n1. 在本地ARM64环境中使用buildx创建多架构镜像:"
echo -e "   ${YELLOW}docker buildx create --name multiarch-builder --use${NC}"
echo -e "   ${YELLOW}docker buildx inspect --bootstrap${NC}"
echo -e "   ${YELLOW}docker buildx build --platform linux/amd64,linux/arm64 -t your-image:tag --push .${NC}"

echo -e "\n2. 或者使用CI/CD流水线在AMD64环境中构建:"
echo -e "   - 设置GitHub Actions或其他CI/CD系统"
echo -e "   - 选择AMD64运行环境"
echo -e "   - 使用Dockerfile.amd64构建"

echo -e "\n3. 最简单的临时解决方案 - 使用已验证可用的其他镜像:"
echo -e "   - 如有其他运行正常的服务，可以临时使用其镜像"
echo -e "   - 修改deployment配置使用公共仓库的镜像"

echo -e "\n${BLUE}==============================================${NC}"
echo -e "${GREEN}如有进一步问题，请联系开发团队获取帮助${NC}"
echo -e "${BLUE}==============================================${NC}" 