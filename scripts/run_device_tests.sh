#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 检查可用设备..."

# 创建临时文件存储设备列表
TEMP_FILE=$(mktemp)
flutter devices > "$TEMP_FILE"

# 提取实际设备行
DEVICE_LIST=()
while IFS= read -r line; do
    # 检查是否包含设备标识符 (mobile/desktop/web)
    if [[ $line =~ "(mobile)" || $line =~ "(desktop)" || $line =~ "(web)" ]]; then
        # 提取设备信息
        device_name=$(echo "$line" | cut -d'•' -f1 | xargs)
        device_id=$(echo "$line" | cut -d'•' -f2 | xargs)
        device_platform=$(echo "$line" | cut -d'•' -f3 | xargs)
        DEVICE_LIST+=("$device_id|$device_name|$device_platform")
    fi
done < "$TEMP_FILE"

# 清理临时文件
rm "$TEMP_FILE"

if [ ${#DEVICE_LIST[@]} -eq 0 ]; then
    echo -e "${RED}错误: 未找到可用设备${NC}"
    echo "请确保设备已连接并运行 'flutter doctor' 检查环境配置"
    exit 1
fi

# 显示设备列表供选择
echo -e "\n${YELLOW}可用设备:${NC}"
for i in "${!DEVICE_LIST[@]}"; do
    IFS='|' read -r id name platform <<< "${DEVICE_LIST[$i]}"
    echo "$((i+1)). $name [$platform]"
done

read -p "输入设备编号 (1-${#DEVICE_LIST[@]}): " CHOICE

if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#DEVICE_LIST[@]}" ]; then
    echo -e "${RED}错误: 无效的选择${NC}"
    exit 1
fi

# 获取选中设备的信息
IFS='|' read -r DEVICE_ID DEVICE_NAME PLATFORM <<< "${DEVICE_LIST[$((CHOICE-1))]}"

echo -e "\n${GREEN}正在使用设备: $DEVICE_NAME [$PLATFORM]${NC}"

# 清理项目
echo -e "\n${YELLOW}清理项目...${NC}"
flutter clean
flutter pub get

# 根据平台构建
echo -e "\n${YELLOW}构建应用...${NC}"
case $PLATFORM in
    *"ios"*)
        # 确保 iOS 开发环境
        echo "检查 iOS 开发环境..."
        if ! command -v xcodebuild &> /dev/null; then
            echo -e "${RED}错误: 未找到 Xcode${NC}"
            exit 1
        fi
        
        # 清理 iOS 构建
        echo "清理 iOS 构建..."
        cd ios
        rm -rf Pods Podfile.lock .symlinks Flutter/Flutter.podspec
        pod cache clean --all
        pod repo update
        cd ..
        
        # 重新获取依赖
        flutter pub get
        
        # 构建 iOS 应用
        flutter build ios --debug --no-codesign --verbose
        
        # 检查构建是否成功
        if [ ! -d "build/ios/iphoneos/Runner.app" ]; then
            echo -e "${RED}错误: iOS 构建失败${NC}"
            exit 1
        fi
        ;;
    *"android"*)
        flutter build apk --debug
        ;;
    *)
        echo -e "${RED}错误: 不支持的平台 - $PLATFORM${NC}"
        exit 1
        ;;
esac

# 安装应用
echo -e "\n${YELLOW}安装应用...${NC}"
flutter install -d "$DEVICE_ID"

# 运行集成测试
echo -e "\n${YELLOW}运行测试...${NC}"
flutter test integration_test/navigation_test.dart -d "$DEVICE_ID"

echo -e "\n${GREEN}测试完成!${NC}" 