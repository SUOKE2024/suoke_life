#!/bin/bash

# build_check.sh - 构建检查脚本
#
# 此脚本在构建后执行，主要用于：
# 1. 验证构建产物是否符合要求
# 2. 检查资源文件和配置是否正确
# 3. 进行其他必要的构建后检查

set -e  # 遇到错误立即退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 检查目标平台
PLATFORM=${1:-"all"}
echo -e "${YELLOW}检查平台: $PLATFORM${NC}"

# 检查Android APK
check_android_apk() {
  echo -e "${YELLOW}检查Android APK...${NC}"
  
  APK_PATH="build/app/outputs/flutter-apk/app-release.apk"
  
  if [ ! -f "$APK_PATH" ]; then
    echo -e "${RED}错误: APK文件不存在: $APK_PATH${NC}"
    return 1
  fi
  
  # 检查APK大小
  APK_SIZE=$(stat -f%z "$APK_PATH")
  APK_SIZE_MB=$(echo "scale=2; $APK_SIZE/1048576" | bc)
  
  echo "APK大小: ${APK_SIZE_MB}MB"
  
  if (( $(echo "$APK_SIZE_MB > 100" | bc -l) )); then
    echo -e "${YELLOW}警告: APK文件较大 (>100MB)${NC}"
  fi
  
  # 使用aapt检查APK信息(如果安装了)
  if command -v aapt &> /dev/null; then
    echo "APK包信息:"
    aapt dump badging "$APK_PATH" | grep -E "package:|version"
  fi
  
  echo -e "${GREEN}Android APK检查完成${NC}"
}

# 检查iOS构建
check_ios_build() {
  echo -e "${YELLOW}检查iOS构建...${NC}"
  
  IOS_BUILD_PATH="build/ios/iphoneos"
  
  if [ ! -d "$IOS_BUILD_PATH" ]; then
    echo -e "${RED}错误: iOS构建目录不存在: $IOS_BUILD_PATH${NC}"
    return 1
  fi
  
  # 检查Info.plist文件
  if [ -f "$IOS_BUILD_PATH/Runner.app/Info.plist" ]; then
    echo "检查Info.plist文件:"
    plutil -p "$IOS_BUILD_PATH/Runner.app/Info.plist" | grep -E "CFBundleVersion|CFBundleShortVersionString"
  else
    echo -e "${YELLOW}警告: Info.plist文件不存在${NC}"
  fi
  
  echo -e "${GREEN}iOS构建检查完成${NC}"
}

# 检查Web构建
check_web_build() {
  echo -e "${YELLOW}检查Web构建...${NC}"
  
  WEB_BUILD_PATH="build/web"
  
  if [ ! -d "$WEB_BUILD_PATH" ]; then
    echo -e "${RED}错误: Web构建目录不存在: $WEB_BUILD_PATH${NC}"
    return 1
  fi
  
  # 检查关键文件
  for file in "index.html" "main.dart.js" "flutter_service_worker.js"; do
    if [ ! -f "$WEB_BUILD_PATH/$file" ]; then
      echo -e "${RED}错误: 关键文件不存在: $file${NC}"
      return 1
    fi
  done
  
  # 检查main.dart.js大小
  JS_SIZE=$(stat -f%z "$WEB_BUILD_PATH/main.dart.js")
  JS_SIZE_MB=$(echo "scale=2; $JS_SIZE/1048576" | bc)
  
  echo "main.dart.js大小: ${JS_SIZE_MB}MB"
  
  if (( $(echo "$JS_SIZE_MB > 5" | bc -l) )); then
    echo -e "${YELLOW}警告: JavaScript文件较大 (>5MB)，可能影响加载速度${NC}"
  fi
  
  echo -e "${GREEN}Web构建检查完成${NC}"
}

# 主函数
main() {
  echo -e "${YELLOW}开始构建检查...${NC}"
  
  EXIT_CODE=0
  
  if [ "$PLATFORM" = "android" ] || [ "$PLATFORM" = "all" ]; then
    check_android_apk || EXIT_CODE=$?
  fi
  
  if [ "$PLATFORM" = "ios" ] || [ "$PLATFORM" = "all" ]; then
    check_ios_build || EXIT_CODE=$?
  fi
  
  if [ "$PLATFORM" = "web" ] || [ "$PLATFORM" = "all" ]; then
    check_web_build || EXIT_CODE=$?
  fi
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}构建检查完成，未发现严重问题${NC}"
  else
    echo -e "${RED}构建检查失败，请查看上面的错误信息${NC}"
  fi
  
  return $EXIT_CODE
}

# 执行主函数
main 