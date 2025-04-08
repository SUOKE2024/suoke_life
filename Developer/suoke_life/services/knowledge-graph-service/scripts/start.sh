#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}      索克生活知识图谱服务启动脚本      ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 检查环境文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: 未找到.env文件，将从.env.example创建${NC}"
    cp .env.example .env
    echo -e "${GREEN}已创建.env文件，请根据需要修改配置${NC}"
fi

# 构建服务
echo -e "${BLUE}正在构建知识图谱服务...${NC}"
go build -o server ./cmd/server

if [ $? -ne 0 ]; then
    echo -e "${RED}构建失败，请检查错误并重试${NC}"
    exit 1
fi

echo -e "${GREEN}构建成功！${NC}"

# 启动服务
echo -e "${BLUE}正在启动知识图谱服务...${NC}"
echo -e "${YELLOW}服务将在http://localhost:3000运行${NC}"
echo -e "${YELLOW}按Ctrl+C停止服务${NC}"

./server

# 脚本不会自然到达这里，除非服务被手动停止
echo -e "${RED}服务已停止${NC}" 