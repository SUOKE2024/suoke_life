#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 显示帮助信息
show_help() {
  echo -e "${BLUE}小艾服务测试运行脚本${NC}"
  echo "使用方法: $0 [选项]"
  echo ""
  echo "选项:"
  echo "  -a, --all         运行所有测试"
  echo "  -u, --unit        仅运行单元测试"
  echo "  -i, --integration 仅运行集成测试"
  echo "  -r, --repositories 仅运行仓库测试"
  echo "  -s, --services    仅运行服务测试"
  echo "  -c, --controllers 仅运行控制器测试"
  echo "  -w, --watch       观察模式运行测试"
  echo "  -h, --help        显示此帮助信息"
  echo ""
  echo "示例:"
  echo "  $0 --all          运行所有测试"
  echo "  $0 -u -w          观察模式运行单元测试"
  echo "  $0 -r             运行仓库测试"
}

# 参数解析
if [ $# -eq 0 ]; then
  show_help
  exit 1
fi

ALL=false
UNIT=false
INTEGRATION=false
REPOSITORIES=false
SERVICES=false
CONTROLLERS=false
WATCH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--all)
      ALL=true
      shift
      ;;
    -u|--unit)
      UNIT=true
      shift
      ;;
    -i|--integration)
      INTEGRATION=true
      shift
      ;;
    -r|--repositories)
      REPOSITORIES=true
      shift
      ;;
    -s|--services)
      SERVICES=true
      shift
      ;;
    -c|--controllers)
      CONTROLLERS=true
      shift
      ;;
    -w|--watch)
      WATCH=true
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo -e "${RED}错误：未知选项 $1${NC}"
      show_help
      exit 1
      ;;
  esac
done

# 确保我们在项目根目录
cd "$(dirname "$0")/.." || exit 1

# 检查Jest配置是否存在
if [ ! -f "tests/jest.config.js" ]; then
  echo -e "${RED}错误：找不到测试配置文件 'tests/jest.config.js'${NC}"
  exit 1
fi

# 准备命令
COMMAND="npm test --"

# 添加观察模式参数
if [ "$WATCH" = true ]; then
  COMMAND="$COMMAND --watch"
fi

# 根据选项运行对应测试
if [ "$ALL" = true ]; then
  echo -e "${GREEN}运行所有测试...${NC}"
  eval "$COMMAND"
elif [ "$UNIT" = true ]; then
  echo -e "${GREEN}运行单元测试...${NC}"
  eval "$COMMAND --testPathIgnorePatterns=integration"
elif [ "$INTEGRATION" = true ]; then
  echo -e "${GREEN}运行集成测试...${NC}"
  eval "$COMMAND tests/unit/integration"
elif [ "$REPOSITORIES" = true ]; then
  echo -e "${GREEN}运行仓库测试...${NC}"
  eval "$COMMAND repositories"
elif [ "$SERVICES" = true ]; then
  echo -e "${GREEN}运行服务测试...${NC}"
  eval "$COMMAND services"
elif [ "$CONTROLLERS" = true ]; then
  echo -e "${GREEN}运行控制器测试...${NC}"
  eval "$COMMAND controllers"
else
  echo -e "${YELLOW}未指定测试类型，运行默认测试...${NC}"
  eval "$COMMAND"
fi

exit 0 