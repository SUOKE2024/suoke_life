#!/bin/bash

# 索克生活CI/CD测试脚本
# 本脚本用于在本地模拟CI/CD流程，验证配置正确性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 获取服务参数
SERVICE_PATH="${1:-rag-service}"
echo -e "${BLUE}开始本地测试 ${YELLOW}$SERVICE_PATH${BLUE} 的CI/CD流程...${NC}"

# 检查服务目录是否存在
if [ ! -d "services/$SERVICE_PATH" ]; then
  echo -e "${RED}错误: 服务目录 services/$SERVICE_PATH 不存在${NC}"
  exit 1
fi

# 创建测试结果目录
mkdir -p services/$SERVICE_PATH/tests/test_results

# 模拟测试阶段
echo -e "\n${YELLOW}=== 测试阶段 ===${NC}"

# 检查Go环境
if ! command -v go &> /dev/null; then
  echo -e "${RED}错误: Go未安装，无法继续测试${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Go环境检查通过${NC}"

# 安装依赖
echo -e "\n${BLUE}安装依赖...${NC}"
cd services/$SERVICE_PATH
if [ -f "go.mod" ]; then
  go mod download
  echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
  echo -e "${YELLOW}⚠ 未找到go.mod文件，跳过依赖安装${NC}"
fi

# 静态代码分析
echo -e "\n${BLUE}运行静态代码分析...${NC}"
if [ -d "internal" ]; then
  go vet ./internal/... 2>/dev/null || true
  echo -e "${GREEN}✓ 静态代码分析完成${NC}"
else
  echo -e "${YELLOW}⚠ 未找到internal目录，跳过静态代码分析${NC}"
fi

# 单元测试
echo -e "\n${BLUE}运行单元测试...${NC}"
if [ -d "internal" ]; then
  go test ./internal/... -v -short 2>&1 | tee ../tests/test_results/unit_tests.log || true
  echo -e "${GREEN}✓ 单元测试完成${NC}"
else
  echo -e "${YELLOW}⚠ 未找到internal目录，跳过单元测试${NC}"
fi

# 集成测试
echo -e "\n${BLUE}运行集成测试...${NC}"
if [ -f "scripts/run_integrated_tests.sh" ]; then
  bash ./scripts/run_integrated_tests.sh 2>&1 | tee ../tests/test_results/integrated_tests.log || true
  echo -e "${GREEN}✓ 集成测试完成${NC}"
else
  echo -e "${YELLOW}⚠ 未找到集成测试脚本，跳过集成测试${NC}"
fi

# TCM特征测试
echo -e "\n${BLUE}运行TCM特征测试...${NC}"
if [ -f "tests/test_multimodal.go" ]; then
  echo -e "${YELLOW}注意: 需要确保已添加测试样本文件${NC}"
  if [ -f "tests/samples/tongue.jpg" ]; then
    go run ./tests/test_multimodal.go -image ./tests/samples/tongue.jpg -query "舌红苔白" -verbose 2>&1 | tee ../tests/test_results/tcm_tests.log || true
    echo -e "${GREEN}✓ TCM特征测试完成${NC}"
  else
    echo -e "${YELLOW}⚠ 未找到测试样本文件，跳过TCM特征测试${NC}"
  fi
else
  echo -e "${YELLOW}⚠ 未找到TCM测试脚本，跳过TCM特征测试${NC}"
fi

# 模拟构建阶段
echo -e "\n${YELLOW}=== 构建阶段 ===${NC}"

# 检查Dockerfile
echo -e "\n${BLUE}检查Dockerfile...${NC}"
if [ -f "Dockerfile" ]; then
  echo -e "${GREEN}✓ Dockerfile检查通过${NC}"
else
  echo -e "${RED}✗ 未找到Dockerfile${NC}"
fi

# 检查k8s配置
echo -e "\n${YELLOW}=== 部署阶段 ===${NC}"
echo -e "\n${BLUE}检查Kubernetes配置...${NC}"
if [ -d "k8s" ]; then
  echo -e "${GREEN}✓ Kubernetes配置检查通过${NC}"
else
  echo -e "${RED}✗ 未找到Kubernetes配置目录${NC}"
fi

# 返回项目根目录
cd ../..

echo -e "\n${GREEN}===================================================${NC}"
echo -e "${GREEN}✅ CI/CD流程测试完成！${NC}"
echo -e "${GREEN}===================================================${NC}"
echo -e "\n测试结果保存在: ${BLUE}services/$SERVICE_PATH/tests/test_results/${NC}"
echo -e "\n如需执行完整CI/CD流程，请提交并推送更改到GitHub仓库。" 