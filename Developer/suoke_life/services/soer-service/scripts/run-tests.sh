#!/bin/bash
# 日常活动模块测试运行脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始运行索儿服务测试...${NC}"

# 检查测试环境变量
if [ -z "$TEST_DB_HOST" ]; then
  echo -e "${YELLOW}未设置数据库测试环境变量，使用默认配置。${NC}"
  echo -e "${YELLOW}如需自定义数据库连接，请设置以下环境变量:${NC}"
  echo -e "${YELLOW}  TEST_DB_HOST, TEST_DB_PORT, TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_NAME${NC}"
fi

# 显示测试类型选项
echo -e "\n${BLUE}请选择要运行的测试类型:${NC}"
echo -e "${BLUE}1) 基础单元测试${NC}"
echo -e "${BLUE}2) 边界条件测试${NC}"
echo -e "${BLUE}3) 集成测试${NC}"
echo -e "${BLUE}4) 端到端测试${NC}"
echo -e "${BLUE}5) 性能测试${NC}"
echo -e "${BLUE}6) 所有测试${NC}"
echo -e "${BLUE}7) 生成覆盖率报告${NC}"

read -p "请选择测试类型 (1-7): " test_type

# 运行基础单元测试
run_basic_unit_tests() {
  echo -e "\n${GREEN}运行基础单元测试...${NC}"
  npx jest --testPathPattern=tests/unit --testPathIgnorePatterns=boundary
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}基础单元测试失败，请修复错误后再继续。${NC}"
    exit 1
  else
    echo -e "${GREEN}基础单元测试通过!${NC}"
  fi
}

# 运行边界条件测试
run_boundary_tests() {
  echo -e "\n${GREEN}运行边界条件测试...${NC}"
  npx jest --testPathPattern=boundary
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}边界条件测试失败，请修复错误后再继续。${NC}"
    exit 1
  else
    echo -e "${GREEN}边界条件测试通过!${NC}"
  fi
}

# 运行集成测试
run_integration_tests() {
  echo -e "\n${GREEN}运行集成测试...${NC}"
  echo -e "${YELLOW}注意: 集成测试需要有可用的MySQL服务器。${NC}"
  npx jest --testPathPattern=tests/integration
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}集成测试失败，请检查数据库连接和配置。${NC}"
    return 1
  else
    echo -e "${GREEN}集成测试通过!${NC}"
    return 0
  fi
}

# 运行端到端测试
run_e2e_tests() {
  echo -e "\n${GREEN}运行端到端测试...${NC}"
  echo -e "${YELLOW}注意: 端到端测试需要有可用的MySQL服务器和完整API服务。${NC}"
  npx jest --testPathPattern=tests/e2e
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}端到端测试失败，请检查应用配置。${NC}"
    return 1
  else
    echo -e "${GREEN}端到端测试通过!${NC}"
    return 0
  fi
}

# 运行性能测试
run_performance_tests() {
  echo -e "\n${GREEN}运行性能测试...${NC}"
  echo -e "${YELLOW}注意: 性能测试可能需要较长时间，并且需要数据库连接。${NC}"
  
  # 设置环境变量以启用性能测试
  RUN_PERF_TESTS=true npx jest --testPathPattern=tests/performance
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}性能测试失败，性能可能不符合预期。${NC}"
    return 1
  else
    echo -e "${GREEN}性能测试通过!${NC}"
    return 0
  fi
}

# 生成覆盖率报告
generate_coverage_report() {
  echo -e "\n${GREEN}生成代码覆盖率报告...${NC}"
  npx jest --coverage
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}覆盖率报告生成失败。${NC}"
    return 1
  else
    echo -e "${GREEN}覆盖率报告生成完成，请查看 coverage/ 目录。${NC}"
    return 0
  fi
}

# 根据选择运行不同类型的测试
case $test_type in
  1)
    run_basic_unit_tests
    ;;
  2)
    run_boundary_tests
    ;;
  3)
    run_integration_tests
    ;;
  4)
    run_e2e_tests
    ;;
  5)
    run_performance_tests
    ;;
  6)
    echo -e "\n${YELLOW}将运行所有类型的测试...${NC}"
    
    run_basic_unit_tests
    run_boundary_tests
    
    read -p "是否继续运行需要数据库的测试? (y/n): " continue_db_tests
    
    if [ "$continue_db_tests" == "y" ] || [ "$continue_db_tests" == "Y" ]; then
      run_integration_tests
      integration_result=$?
      
      run_e2e_tests
      e2e_result=$?
      
      read -p "是否运行性能测试? (y/n): " run_perf
      if [ "$run_perf" == "y" ] || [ "$run_perf" == "Y" ]; then
        run_performance_tests
        perf_result=$?
      fi
      
      # 检查是否所有测试都通过
      if [ $integration_result -eq 0 ] && [ $e2e_result -eq 0 ] && ([ "$run_perf" != "y" ] || [ $perf_result -eq 0 ]); then
        echo -e "\n${GREEN}所有测试通过!${NC}"
      else
        echo -e "\n${YELLOW}部分测试未通过，请查看详细日志。${NC}"
      fi
    else
      echo -e "\n${YELLOW}跳过需要数据库的测试。${NC}"
    fi
    ;;
  7)
    generate_coverage_report
    ;;
  *)
    echo -e "${RED}无效的选择，退出测试。${NC}"
    exit 1
    ;;
esac

echo -e "\n${GREEN}测试运行完成!${NC}"
exit 0 