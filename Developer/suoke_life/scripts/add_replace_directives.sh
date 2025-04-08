#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 恢复默认颜色

# 打印信息
echo -e "${BLUE}开始为服务添加replace指令...${NC}"

# 定义要处理的服务列表
SERVICES=(
  "api-gateway"
  "auth-service"
  "user-service"
  "rag-service"
  "knowledge-graph-service"
  "inquiry-diagnosis-service"
  "agent-coordinator-service"
  "xiaoke-service"
)

# 项目根目录
ROOT_DIR="/Users/songxu/Developer/suoke_life"

# 为每个服务添加replace指令
for SERVICE in "${SERVICES[@]}"; do
  SERVICE_DIR="$ROOT_DIR/services/$SERVICE"
  
  if [ -d "$SERVICE_DIR" ]; then
    echo -e "${GREEN}处理服务: $SERVICE${NC}"
    
    # 检查go.mod文件是否存在
    if [ -f "$SERVICE_DIR/go.mod" ]; then
      # 检查是否需要添加replace指令
      if grep -q "github.com/suoke-life/shared" "$SERVICE_DIR/go.mod"; then
        echo -e "  ${YELLOW}需要添加replace指令${NC}"
        
        # 检查是否已经有replace指令
        if ! grep -q "replace github.com/suoke-life/shared" "$SERVICE_DIR/go.mod"; then
          # 添加replace指令
          echo -e "  ${GREEN}添加replace指令${NC}"
          echo -e "\n// 使用本地共享库\nreplace github.com/suoke-life/shared => $ROOT_DIR/services/shared" >> "$SERVICE_DIR/go.mod"
        else
          echo -e "  ${YELLOW}已有replace指令，进行更新${NC}"
          # 使用sed更新现有的replace指令
          sed -i '' 's|replace github.com/suoke-life/shared.*|replace github.com/suoke-life/shared => '"$ROOT_DIR"'/services/shared|g' "$SERVICE_DIR/go.mod"
        fi
      else
        echo -e "  ${YELLOW}不需要添加replace指令${NC}"
      fi
    else
      echo -e "  ${RED}go.mod文件不存在${NC}"
    fi
  else
    echo -e "${RED}跳过不存在的服务: $SERVICE${NC}"
  fi
done

echo -e "${BLUE}replace指令添加完成！${NC}"
echo -e "${YELLOW}请在各服务目录中执行 go mod tidy 以更新依赖${NC}" 