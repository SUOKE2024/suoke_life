#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}     索克生活APP 测试覆盖率检查脚本     ${NC}"
echo -e "${YELLOW}============================================${NC}"

# 检查依赖并安装
echo -e "\n${GREEN}检查依赖...${NC}"
npm list jest > /dev/null 2>&1 || { echo -e "${YELLOW}安装缺少的依赖...${NC}"; npm install; }

# 清理之前的测试覆盖率报告
echo -e "\n${GREEN}清理旧的测试报告...${NC}"
rm -rf coverage

# 清理Jest缓存以确保干净运行
echo -e "\n${GREEN}清理Jest缓存...${NC}"
npx jest --clearCache

# 运行测试
echo -e "\n${GREEN}运行单元测试...${NC}"
npm run test

# 检查测试结果
TEST_RESULT=$?
if [ $TEST_RESULT -ne 0 ]; then
  echo -e "\n${RED}测试失败! 请修复上述错误。${NC}"
  exit 1
fi

# 分析覆盖率
echo -e "\n${GREEN}分析测试覆盖率...${NC}"
COVERAGE=$(grep -A 5 "All files" coverage/lcov-report/index.html | grep "%</span>" | awk -F'>' '{print $2}' | awk -F'%' '{print $1}')

echo -e "\n${YELLOW}总体覆盖率: ${COVERAGE}%${NC}"

if (( $(echo "$COVERAGE < 70" | bc -l) )); then
  echo -e "\n${RED}警告: 测试覆盖率低于70%目标!${NC}"
  echo -e "${YELLOW}请增加测试以提高覆盖率。${NC}"
  
  # 找出覆盖率最低的文件
  echo -e "\n${YELLOW}覆盖率最低的五个文件:${NC}"
  grep -r -A 1 "<div class='fl pad1y space-right2'>" coverage/lcov-report/src/ | grep "%" | sort -t ">" -k2,2n | head -5
  
  echo -e "\n${YELLOW}建议:${NC}"
  echo -e "1. 优先为上述低覆盖率文件添加测试"
  echo -e "2. 关注缺少测试的服务和控制器"
  echo -e "3. 运行 'npm run test -- --coverage' 查看详细报告"
else
  echo -e "\n${GREEN}恭喜! 测试覆盖率达到目标。${NC}"
fi

# 打开HTML覆盖率报告
echo -e "\n${GREEN}生成HTML测试覆盖率报告在 ./coverage/lcov-report/index.html${NC}"

echo -e "\n${YELLOW}============================================${NC}"
echo -e "${YELLOW}               测试检查完成                ${NC}"
echo -e "${YELLOW}============================================${NC}"

exit 0