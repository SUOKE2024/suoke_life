#!/bin/bash

# 定义颜色输出
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}等待Docker启动...${NC}"

# 最大等待时间(秒)
MAX_WAIT=120
START_TIME=$(date +%s)

# 循环检查Docker状态
while true; do
    # 计算已等待时间
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    
    # 如果超过最大等待时间，退出
    if [ $ELAPSED_TIME -gt $MAX_WAIT ]; then
        echo -e "${RED}等待超时!${NC} Docker未在 $MAX_WAIT 秒内启动。"
        echo -e "请手动检查Docker Desktop是否正在运行。"
        exit 1
    fi
    
    # 尝试运行docker info命令
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}Docker已成功启动!${NC} (等待了 $ELAPSED_TIME 秒)"
        break
    else
        # 每5秒显示一次等待信息
        if [ $((ELAPSED_TIME % 5)) -eq 0 ]; then
            echo -e "仍在等待Docker启动... (已等待 $ELAPSED_TIME 秒)"
        fi
        sleep 1
    fi
done

# Docker已启动，显示版本信息
echo -e "${GREEN}Docker版本信息:${NC}"
docker --version

echo -e "${GREEN}Docker准备就绪，可以继续构建和部署。${NC}"
exit 0 