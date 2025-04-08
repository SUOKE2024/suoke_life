#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  推送镜像到阿里云仓库  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 登录到阿里云容器镜像服务
echo -e "\n${BLUE}登录到阿里云容器镜像服务...${NC}"
docker login --username=netsong@sina.com suoke-registry.cn-hangzhou.cr.aliyuncs.com

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 登录失败!${NC}"
    exit 1
fi

# 推送镜像
echo -e "\n${BLUE}推送镜像...${NC}"
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service:local

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 推送失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ 镜像已推送成功!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "${YELLOW}标签: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service:local${NC}"
echo -e "${BLUE}=========================================${NC}" 