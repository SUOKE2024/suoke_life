#!/bin/bash

# run_cicd.sh - CI/CD快速启动脚本
#
# 此脚本用于帮助开发者快速运行CI/CD流程

set -e  # 遇到错误立即退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 环境设置
ENV=${ENV:-"staging"}
SKIP_TESTS=${SKIP_TESTS:-"false"}
SKIP_LINT=${SKIP_LINT:-"false"}
SKIP_BUILD=${SKIP_BUILD:-"false"}
SKIP_DEPLOY=${SKIP_DEPLOY:-"false"}

# 显示帮助信息
show_help() {
  echo -e "${BLUE}索克生活 CI/CD 快速启动脚本${NC}"
  echo -e "${YELLOW}使用方法:${NC}"
  echo -e "  ./scripts/run_cicd.sh [选项]"
  echo
  echo -e "${YELLOW}选项:${NC}"
  echo -e "  -h, --help         显示帮助信息"
  echo -e "  -e, --env ENV      设置环境 (development|staging|production)"
  echo -e "  --skip-tests       跳过测试"
  echo -e "  --skip-lint        跳过代码检查"
  echo -e "  --skip-build       跳过构建"
  echo -e "  --skip-deploy      跳过部署"
  echo -e "  --lint-only        只运行代码检查"
  echo -e "  --test-only        只运行测试"
  echo -e "  --build-only       只运行构建"
  echo -e "  --deploy-only      只运行部署"
  echo -e "  --web              只构建Web应用"
  echo -e "  --ios              只构建iOS应用"
  echo -e "  --android          只构建Android应用"
  echo
  echo -e "${YELLOW}环境变量:${NC}"
  echo -e "  ENV                部署环境 (默认: staging)"
  echo -e "  SKIP_TESTS         是否跳过测试 (默认: false)"
  echo -e "  SKIP_LINT          是否跳过代码检查 (默认: false)"
  echo -e "  SKIP_BUILD         是否跳过构建 (默认: false)"
  echo -e "  SKIP_DEPLOY        是否跳过部署 (默认: false)"
  echo
  echo -e "${YELLOW}示例:${NC}"
  echo -e "  ./scripts/run_cicd.sh --env production --skip-tests"
  echo -e "  ./scripts/run_cicd.sh --deploy-only --web"
  echo -e "  ENV=production ./scripts/run_cicd.sh"
}

# 解析命令行参数
parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      -h|--help)
        show_help
        exit 0
        ;;
      -e|--env)
        ENV="$2"
        shift 2
        ;;
      --skip-tests)
        SKIP_TESTS="true"
        shift
        ;;
      --skip-lint)
        SKIP_LINT="true"
        shift
        ;;
      --skip-build)
        SKIP_BUILD="true"
        shift
        ;;
      --skip-deploy)
        SKIP_DEPLOY="true"
        shift
        ;;
      --lint-only)
        SKIP_TESTS="true"
        SKIP_BUILD="true"
        SKIP_DEPLOY="true"
        shift
        ;;
      --test-only)
        SKIP_LINT="true"
        SKIP_BUILD="true"
        SKIP_DEPLOY="true"
        shift
        ;;
      --build-only)
        SKIP_LINT="true"
        SKIP_TESTS="true"
        SKIP_DEPLOY="true"
        shift
        ;;
      --deploy-only)
        SKIP_LINT="true"
        SKIP_TESTS="true"
        SKIP_BUILD="true"
        shift
        ;;
      --web)
        PLATFORM="web"
        shift
        ;;
      --ios)
        PLATFORM="ios"
        shift
        ;;
      --android)
        PLATFORM="android"
        shift
        ;;
      *)
        echo -e "${RED}未知选项: $1${NC}"
        show_help
        exit 1
        ;;
    esac
  done
}

# 运行代码检查
run_lint() {
  if [ "$SKIP_LINT" == "true" ]; then
    echo -e "${YELLOW}跳过代码检查${NC}"
    return 0
  fi
  
  echo -e "${YELLOW}运行代码检查...${NC}"
  
  # 运行Flutter分析
  flutter analyze
  
  echo -e "${GREEN}代码检查完成${NC}"
}

# 运行测试
run_tests() {
  if [ "$SKIP_TESTS" == "true" ]; then
    echo -e "${YELLOW}跳过测试${NC}"
    return 0
  fi
  
  echo -e "${YELLOW}运行测试...${NC}"
  
  # 如果存在test目录且包含测试文件，则运行测试
  if [ -d "test" ] && [ "$(find test -name "*_test.dart" | wc -l)" -gt 0 ]; then
    flutter test
  else
    echo -e "${YELLOW}未找到测试文件，跳过测试${NC}"
  fi
  
  echo -e "${GREEN}测试完成${NC}"
}

# 运行构建
run_build() {
  if [ "$SKIP_BUILD" == "true" ]; then
    echo -e "${YELLOW}跳过构建${NC}"
    return 0
  fi
  
  echo -e "${YELLOW}运行构建...${NC}"
  
  # 运行prebuild脚本
  if [ -f "./scripts/prebuild.sh" ]; then
    chmod +x ./scripts/prebuild.sh
    ./scripts/prebuild.sh "$ENV"
  fi
  
  # 根据平台选择构建目标
  case $PLATFORM in
    "web")
      echo -e "${YELLOW}构建Web应用...${NC}"
      flutter build web --release
      ;;
    "ios")
      echo -e "${YELLOW}构建iOS应用...${NC}"
      flutter build ios --release --no-codesign
      ;;
    "android")
      echo -e "${YELLOW}构建Android应用...${NC}"
      flutter build apk --release
      ;;
    *)
      # 构建所有平台
      echo -e "${YELLOW}构建Web应用...${NC}"
      flutter build web --release || true
      
      if [ "$(uname)" == "Darwin" ]; then
        echo -e "${YELLOW}构建iOS应用...${NC}"
        flutter build ios --release --no-codesign || true
      fi
      
      echo -e "${YELLOW}构建Android应用...${NC}"
      flutter build apk --release || true
      ;;
  esac
  
  echo -e "${GREEN}构建完成${NC}"
}

# 运行部署
run_deploy() {
  if [ "$SKIP_DEPLOY" == "true" ]; then
    echo -e "${YELLOW}跳过部署${NC}"
    return 0
  fi
  
  echo -e "${YELLOW}运行部署...${NC}"
  
  # 根据平台选择部署目标
  case $PLATFORM in
    "web")
      echo -e "${YELLOW}部署Web应用...${NC}"
      if [ -f "./scripts/real_deploy.sh" ]; then
        chmod +x ./scripts/real_deploy.sh
        ./scripts/real_deploy.sh "$ENV"
      else
        echo -e "${RED}错误: 未找到部署脚本 './scripts/real_deploy.sh'${NC}"
        exit 1
      fi
      ;;
    "ios")
      echo -e "${YELLOW}iOS应用部署需要手动上传到App Store Connect${NC}"
      echo -e "${YELLOW}请使用Xcode打开项目并上传到App Store Connect${NC}"
      ;;
    "android")
      echo -e "${YELLOW}Android应用部署需要手动上传到Google Play Console${NC}"
      echo -e "${YELLOW}请访问Google Play Console上传APK文件${NC}"
      ;;
    *)
      # 默认部署Web应用
      echo -e "${YELLOW}部署Web应用...${NC}"
      if [ -f "./scripts/real_deploy.sh" ]; then
        chmod +x ./scripts/real_deploy.sh
        ./scripts/real_deploy.sh "$ENV"
      else
        echo -e "${RED}错误: 未找到部署脚本 './scripts/real_deploy.sh'${NC}"
        exit 1
      fi
      ;;
  esac
  
  echo -e "${GREEN}部署完成${NC}"
}

# 主函数
main() {
  echo -e "${BLUE}=============================================${NC}"
  echo -e "${BLUE}          索克生活 CI/CD 流程启动          ${NC}"
  echo -e "${BLUE}=============================================${NC}"
  echo -e "${YELLOW}环境: $ENV${NC}"
  
  # 执行CI/CD流程
  run_lint
  run_tests
  run_build
  run_deploy
  
  echo -e "${BLUE}=============================================${NC}"
  echo -e "${GREEN}          CI/CD 流程执行完成          ${NC}"
  echo -e "${BLUE}=============================================${NC}"
}

# 解析命令行参数
parse_args "$@"

# 执行主函数
main