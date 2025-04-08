#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务Docker环境启动脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装或不在PATH中${NC}"
    echo -e "${YELLOW}请安装Docker后再试：https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装或不在PATH中${NC}"
    echo -e "${YELLOW}请安装Docker Compose后再试：https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# 构建并启动服务
echo -e "${BLUE}正在构建并启动Docker环境...${NC}"
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo -e "${RED}启动Docker环境失败，请检查错误并重试${NC}"
    exit 1
fi

echo -e "${GREEN}Docker环境已成功启动！${NC}"
echo -e "${YELLOW}知识图谱服务: http://localhost:3000${NC}"
echo -e "${YELLOW}Neo4j浏览器: http://localhost:7474${NC}"
echo -e "${YELLOW}默认Neo4j凭据: neo4j/suokeneo4j${NC}"

echo -e "${BLUE}查看服务日志:${NC}"
echo -e "${GREEN}docker-compose logs -f knowledge-graph-service${NC}"

echo -e "${BLUE}停止服务:${NC}"
echo -e "${GREEN}docker-compose down${NC}" 