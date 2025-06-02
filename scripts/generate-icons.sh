#!/bin/bash

# 索克生活 - 图标生成脚本
# 自动生成iOS、Android和桌面应用的所有图标尺寸

set -e

echo "🎨 索克生活 - 图标生成脚本"
echo "================================"

# 检查源文件是否存在
SOURCE_ICON="src/assets/images/logo_1024.png"
if [ ! -f "$SOURCE_ICON" ]; then
    echo "❌ 错误: 源图标文件不存在: $SOURCE_ICON"
    exit 1
fi

echo "📱 生成iOS图标..."

# iOS图标目录
IOS_ICON_DIR="ios/SuokeLife/Images.xcassets/AppIcon.appiconset"
mkdir -p "$IOS_ICON_DIR"

# 复制1024x1024源文件
cp "$SOURCE_ICON" "$IOS_ICON_DIR/AppIcon-1024.png"

# 生成iOS各种尺寸
cd "$IOS_ICON_DIR"
sips -z 40 40 AppIcon-1024.png --out AppIcon-20@2x.png
sips -z 60 60 AppIcon-1024.png --out AppIcon-20@3x.png
sips -z 58 58 AppIcon-1024.png --out AppIcon-29@2x.png
sips -z 87 87 AppIcon-1024.png --out AppIcon-29@3x.png
sips -z 80 80 AppIcon-1024.png --out AppIcon-40@2x.png
sips -z 120 120 AppIcon-1024.png --out AppIcon-40@3x.png
sips -z 120 120 AppIcon-1024.png --out AppIcon-60@2x.png
sips -z 180 180 AppIcon-1024.png --out AppIcon-60@3x.png

cd - > /dev/null

echo "✅ iOS图标生成完成"

echo "🤖 生成Android图标..."

# Android图标
sips -z 48 48 "$SOURCE_ICON" --out android/app/src/main/res/mipmap-mdpi/ic_launcher.png
sips -z 72 72 "$SOURCE_ICON" --out android/app/src/main/res/mipmap-hdpi/ic_launcher.png
sips -z 96 96 "$SOURCE_ICON" --out android/app/src/main/res/mipmap-xhdpi/ic_launcher.png
sips -z 144 144 "$SOURCE_ICON" --out android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png
sips -z 192 192 "$SOURCE_ICON" --out android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png

echo "✅ Android图标生成完成"

echo "🖥️ 生成桌面图标..."

# 桌面图标目录
DESKTOP_ICON_DIR="src/assets/images/icons/desktop"
mkdir -p "$DESKTOP_ICON_DIR"

# 生成桌面各种尺寸
cp "$SOURCE_ICON" "$DESKTOP_ICON_DIR/app-icon-1024.png"
sips -z 512 512 "$SOURCE_ICON" --out "$DESKTOP_ICON_DIR/app-icon-512.png"
cp src/assets/images/logo_256.png "$DESKTOP_ICON_DIR/app-icon-256.png"
cp src/assets/images/logo_128.png "$DESKTOP_ICON_DIR/app-icon-128.png"
cp src/assets/images/logo_64.png "$DESKTOP_ICON_DIR/app-icon-64.png"

echo "✅ 桌面图标生成完成"

echo ""
echo "🎉 所有图标生成完成！"
echo ""
echo "📊 生成的图标统计:"
echo "  iOS: 9个图标文件"
echo "  Android: 5个密度图标"
echo "  桌面: 5个尺寸图标"
echo ""
echo "📝 下一步:"
echo "  1. 检查生成的图标质量"
echo "  2. 构建并测试应用"
echo "  3. 提交代码到版本控制"
echo ""
echo "✨ 索克生活 - AI驱动的智慧健康管理平台" 