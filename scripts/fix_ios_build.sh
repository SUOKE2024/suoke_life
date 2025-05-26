#!/bin/bash

# SuokeLife iOS 构建问题修复脚本
# 解决 "Could not compute dependency graph" 错误

set -e

echo "🔧 开始修复 SuokeLife iOS 构建问题..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}📍 当前目录: $(pwd)${NC}"

# 步骤 1: 关闭所有 Xcode 实例
echo -e "\n${YELLOW}步骤 1: 关闭所有 Xcode 实例...${NC}"
pkill -f Xcode || true
pkill -f Simulator || true
sleep 2

# 步骤 2: 清理 Xcode 派生数据
echo -e "\n${YELLOW}步骤 2: 清理 Xcode 派生数据...${NC}"
rm -rf ~/Library/Developer/Xcode/DerivedData/*
echo -e "${GREEN}✅ Xcode 派生数据已清理${NC}"

# 步骤 3: 清理 Xcode 缓存
echo -e "\n${YELLOW}步骤 3: 清理 Xcode 缓存...${NC}"
rm -rf ~/Library/Caches/com.apple.dt.Xcode
rm -rf ~/Library/Caches/org.llvm.clang
echo -e "${GREEN}✅ Xcode 缓存已清理${NC}"

# 步骤 4: 清理项目构建文件
echo -e "\n${YELLOW}步骤 4: 清理项目构建文件...${NC}"
cd ios
rm -rf build/
rm -rf Pods/
rm -f Podfile.lock
echo -e "${GREEN}✅ 项目构建文件已清理${NC}"

# 步骤 5: 清理 React Native 缓存
echo -e "\n${YELLOW}步骤 5: 清理 React Native 缓存...${NC}"
cd ..
npx react-native clean || true
rm -rf node_modules/
rm -f package-lock.json
echo -e "${GREEN}✅ React Native 缓存已清理${NC}"

# 步骤 6: 重新安装 Node.js 依赖
echo -e "\n${YELLOW}步骤 6: 重新安装 Node.js 依赖...${NC}"
npm install
echo -e "${GREEN}✅ Node.js 依赖已重新安装${NC}"

# 步骤 7: 重新安装 CocoaPods 依赖
echo -e "\n${YELLOW}步骤 7: 重新安装 CocoaPods 依赖...${NC}"
cd ios

# 检查 CocoaPods 是否安装
if ! command -v pod &> /dev/null; then
    echo -e "${RED}❌ CocoaPods 未安装，正在安装...${NC}"
    sudo gem install cocoapods
fi

# 更新 CocoaPods 仓库
echo -e "${BLUE}📦 更新 CocoaPods 仓库...${NC}"
pod repo update

# 安装依赖
echo -e "${BLUE}📦 安装 CocoaPods 依赖...${NC}"
pod install --clean-install
echo -e "${GREEN}✅ CocoaPods 依赖已重新安装${NC}"

# 步骤 8: 验证项目结构
echo -e "\n${YELLOW}步骤 8: 验证项目结构...${NC}"
if [ -f "SuokeLife.xcworkspace" ]; then
    echo -e "${GREEN}✅ Xcode workspace 文件存在${NC}"
else
    echo -e "${RED}❌ Xcode workspace 文件不存在${NC}"
    exit 1
fi

if [ -d "Pods" ]; then
    echo -e "${GREEN}✅ Pods 目录存在${NC}"
else
    echo -e "${RED}❌ Pods 目录不存在${NC}"
    exit 1
fi

cd ..

# 步骤 9: 重置 Metro 缓存
echo -e "\n${YELLOW}步骤 9: 重置 Metro 缓存...${NC}"
npx react-native start --reset-cache &
METRO_PID=$!
sleep 5
kill $METRO_PID || true
echo -e "${GREEN}✅ Metro 缓存已重置${NC}"

echo -e "\n${GREEN}🎉 修复完成！${NC}"
echo -e "\n${BLUE}📋 接下来的步骤：${NC}"
echo -e "1. 打开 Xcode"
echo -e "2. 打开 ${YELLOW}ios/SuokeLife.xcworkspace${NC} (不是 .xcodeproj)"
echo -e "3. 选择目标设备或模拟器"
echo -e "4. 点击 Build 或 Run"
echo -e "\n${BLUE}💡 提示：${NC}"
echo -e "- 始终使用 .xcworkspace 文件而不是 .xcodeproj"
echo -e "- 如果问题仍然存在，请重启 Mac"
echo -e "- 确保 Xcode 版本与 React Native 版本兼容"

echo -e "\n${GREEN}✨ SuokeLife iOS 构建问题修复完成！${NC}" 