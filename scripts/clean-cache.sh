#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}开始清理 Suoke Life 项目缓存...${NC}"

# 清理 React Native 缓存
echo -e "${YELLOW}清理 React Native 缓存...${NC}"
rm -rf $TMPDIR/react-* || true
rm -rf $TMPDIR/metro-* || true
rm -rf $TMPDIR/haste-* || true
watchman watch-del-all || true
echo -e "${GREEN}✓ React Native 缓存已清理${NC}"

# 清理 Node 模块缓存
echo -e "${YELLOW}清理 Node 模块缓存...${NC}"
rm -rf node_modules
rm -rf package-lock.json
echo -e "${GREEN}✓ Node 模块缓存已清理${NC}"

# 清理 iOS 缓存
echo -e "${YELLOW}清理 iOS 缓存...${NC}"
rm -rf ios/build
rm -rf ios/Pods
rm -rf ios/Podfile.lock
rm -rf ios/*.xcworkspace/xcuserdata
rm -rf ios/*.xcodeproj/xcuserdata
rm -rf ios/*.xcodeproj/project.xcworkspace/xcuserdata
rm -rf ios/SuokeLife/main.jsbundle*
echo -e "${GREEN}✓ iOS 缓存已清理${NC}"

# 清理 Android 缓存
echo -e "${YELLOW}清理 Android 缓存...${NC}"
rm -rf android/app/build
rm -rf android/build
rm -rf android/.gradle
rm -rf android/app/src/main/assets/index.android.bundle
rm -rf android/app/src/main/res/drawable-*
rm -rf android/app/src/main/res/raw
echo -e "${GREEN}✓ Android 缓存已清理${NC}"

# 清理 Temp 文件夹
echo -e "${YELLOW}清理临时文件...${NC}"
rm -rf temp/*
echo -e "${GREEN}✓ 临时文件已清理${NC}"

# 清理 Metro bundler 缓存
echo -e "${YELLOW}清理 Metro bundler 缓存...${NC}"
rm -rf $TMPDIR/metro-bundler-cache-*
echo -e "${GREEN}✓ Metro bundler 缓存已清理${NC}"

# 清理其他临时缓存
echo -e "${YELLOW}清理其他临时缓存...${NC}"
rm -rf .watchman-cookie-*
rm -rf .eslintcache
echo -e "${GREEN}✓ 其他临时缓存已清理${NC}"

echo -e "${BLUE}缓存清理完成！${NC}"
echo -e "${YELLOW}提示: 请运行 'npm install' 重新安装依赖${NC}" 