#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 恢复默认颜色

# 打印信息
echo -e "${BLUE}开始修复导入路径...${NC}"
echo -e "${YELLOW}从 github.com/suoke-life 修改为 github.com/suoke-life${NC}"

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
  "avatar-service"
)

# 项目根目录
ROOT_DIR="/Users/songxu/Developer/suoke_life"

# 查找并替换所有服务中的Go文件
for SERVICE in "${SERVICES[@]}"; do
  SERVICE_DIR="$ROOT_DIR/services/$SERVICE"
  
  if [ -d "$SERVICE_DIR" ]; then
    echo -e "${GREEN}处理服务: $SERVICE${NC}"
    
    # 查找所有Go文件
    GO_FILES=$(find "$SERVICE_DIR" -name "*.go" -type f)
    
    # 对每个文件进行替换
    for FILE in $GO_FILES; do
      # 检查文件是否包含旧的导入路径
      if grep -q "github.com/suoke-life" "$FILE"; then
        echo -e "  修复文件: ${YELLOW}$(basename $FILE)${NC}"
        
        # 执行替换
        sed -i '' 's|github.com/suoke-life|github.com/suoke-life|g' "$FILE"
      fi
    done
    
    # 检查go.mod文件并更新
    if [ -f "$SERVICE_DIR/go.mod" ]; then
      if grep -q "github.com/suoke-life" "$SERVICE_DIR/go.mod"; then
        echo -e "  修复文件: ${YELLOW}go.mod${NC}"
        sed -i '' 's|github.com/suoke-life|github.com/suoke-life|g' "$SERVICE_DIR/go.mod"
      fi
    fi
    
    # 处理replace指令
    if [ -f "$SERVICE_DIR/go.mod" ]; then
      if grep -q "replace github.com/suoke-life/shared" "$SERVICE_DIR/go.mod"; then
        echo -e "  更新replace指令: ${YELLOW}go.mod${NC}"
        sed -i '' 's|replace github.com/suoke-life/shared|replace github.com/suoke-life/shared|g' "$SERVICE_DIR/go.mod"
      fi
    fi
  else
    echo -e "${RED}跳过不存在的服务: $SERVICE${NC}"
  fi
done

# 修复共享库
SHARED_DIR="$ROOT_DIR/services/shared"
if [ -d "$SHARED_DIR" ]; then
  echo -e "${GREEN}处理共享库${NC}"
  
  # 查找共享库中的所有Go文件
  GO_FILES=$(find "$SHARED_DIR" -name "*.go" -type f)
  
  # 对每个文件进行替换
  for FILE in $GO_FILES; do
    # 检查文件是否包含旧的导入路径
    if grep -q "github.com/suoke-life" "$FILE"; then
      echo -e "  修复文件: ${YELLOW}$(basename $FILE)${NC}"
      
      # 执行替换
      sed -i '' 's|github.com/suoke-life|github.com/suoke-life|g' "$FILE"
    fi
  done
  
  # 处理go.mod文件
  if [ -f "$SHARED_DIR/go.mod" ]; then
    if grep -q "github.com/suoke-life" "$SHARED_DIR/go.mod"; then
      echo -e "  修复文件: ${YELLOW}go.mod${NC}"
      sed -i '' 's|github.com/suoke-life|github.com/suoke-life|g' "$SHARED_DIR/go.mod"
    fi
  fi
fi

# 修复部署脚本
SCRIPTS_DIR="$ROOT_DIR/scripts"
if [ -d "$SCRIPTS_DIR" ]; then
  echo -e "${GREEN}处理部署脚本${NC}"
  
  # 查找部署脚本
  SCRIPT_FILES=$(find "$SCRIPTS_DIR" -name "*.sh" -type f)
  
  # 对每个文件进行替换
  for FILE in $SCRIPT_FILES; do
    # 检查文件是否包含旧的导入路径
    if grep -q "github.com/suoke-life" "$FILE"; then
      echo -e "  修复文件: ${YELLOW}$(basename $FILE)${NC}"
      
      # 执行替换
      sed -i '' 's|github.com/suoke-life|github.com/suoke-life|g' "$FILE"
    fi
  done
fi

echo -e "${BLUE}导入路径修复完成！${NC}"
echo -e "${YELLOW}请在各服务目录中执行 go mod tidy 以更新依赖${NC}" 