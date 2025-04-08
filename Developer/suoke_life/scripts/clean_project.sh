#!/bin/bash

# 索克生活APP项目清理脚本
echo "开始清理索克生活APP项目..."

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 记录初始大小
INITIAL_SIZE=$(du -sh . | cut -f1)
echo -e "${YELLOW}项目初始大小: ${INITIAL_SIZE}${NC}"

# 1. 清理Flutter编译和缓存文件
echo -e "${GREEN}正在清理Flutter编译和缓存文件...${NC}"
find . -name "build" -type d -not -path "*/node_modules/*" -exec rm -rf {} \; 2>/dev/null || true
find . -name ".dart_tool" -type d -exec rm -rf {} \; 2>/dev/null || true
find . -name ".flutter-plugins-dependencies" -type f -exec rm {} \; 2>/dev/null || true
find . -name ".flutter-plugins" -type f -exec rm {} \; 2>/dev/null || true
find . -name "*.iml" -type f -exec rm {} \; 2>/dev/null || true
find . -name "Generated.xcconfig" -type f -exec rm {} \; 2>/dev/null || true

# 2. 清理日志文件
echo -e "${GREEN}正在清理日志文件...${NC}"
find ./services -name "*.log" -type f -exec rm {} \; 2>/dev/null || true

# 3. 清理临时文件
echo -e "${GREEN}正在清理临时文件...${NC}"
find . -name "*.tmp" -o -name "*.temp" -type f -exec rm {} \; 2>/dev/null || true
find . -name ".DS_Store" -type f -exec rm {} \; 2>/dev/null || true

# 4. 如果确认没问题，可以清理node_modules（取消注释下面的命令）
echo -e "${YELLOW}注意: node_modules目录保留，如需清理请取消注释脚本中的相关命令${NC}"
# find ./services -name "node_modules" -type d -exec rm -rf {} \; 2>/dev/null || true
# find . -name "node_modules" -type d -maxdepth 1 -exec rm -rf {} \; 2>/dev/null || true

# 5. 清理iOS构建文件
echo -e "${GREEN}正在清理iOS构建文件...${NC}"
find ./ios -name "DerivedData" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./ios -path "*/Debug-iphonesimulator" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./ios -path "*/Debug-iphoneos" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./ios -path "*/Release-iphonesimulator" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./ios -path "*/Release-iphoneos" -type d -exec rm -rf {} \; 2>/dev/null || true

# 6. 清理Android构建文件
echo -e "${GREEN}正在清理Android构建文件...${NC}"
find ./android -name "build" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./android -name ".gradle" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./android -name "*.apk" -type f -exec rm {} \; 2>/dev/null || true
find ./android -name "*.aab" -type f -exec rm {} \; 2>/dev/null || true

# 7. 清理macOS构建文件
echo -e "${GREEN}正在清理macOS构建文件...${NC}"
find ./macos -name "build" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./macos -name "DerivedData" -type d -exec rm -rf {} \; 2>/dev/null || true

# 8. 清理windows和linux构建文件
echo -e "${GREEN}正在清理Windows和Linux构建文件...${NC}"
find ./windows -name "build" -type d -exec rm -rf {} \; 2>/dev/null || true
find ./linux -name "build" -type d -exec rm -rf {} \; 2>/dev/null || true

# 9. 清理VSCode缓存
echo -e "${GREEN}正在清理VSCode缓存...${NC}"
find ./.vscode -name "*.log" -type f -exec rm {} \; 2>/dev/null || true

# 10. 清理Cursor缓存
echo -e "${GREEN}正在清理Cursor缓存...${NC}"
find ./.cursor -name "*.log" -type f -exec rm {} \; 2>/dev/null || true

# 运行Flutter清理命令
if command -v flutter &> /dev/null; then
    echo -e "${GREEN}运行Flutter清理命令...${NC}"
    flutter clean
else
    echo -e "${YELLOW}Flutter命令不可用，跳过Flutter清理命令${NC}"
fi

# 记录清理后大小
FINAL_SIZE=$(du -sh . | cut -f1)
echo -e "${GREEN}项目清理完成!${NC}"
echo -e "${YELLOW}清理前项目大小: ${INITIAL_SIZE}${NC}"
echo -e "${YELLOW}清理后项目大小: ${FINAL_SIZE}${NC}" 