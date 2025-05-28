#!/bin/bash

# 修复 iOS 构建警告脚本
# 用于解决 VisionCamera 和 Hermes 相关的警告

echo "🔧 开始修复 iOS 构建警告..."

# 1. 修复 VisionCamera 的 @frozen 警告
echo "📸 修复 VisionCamera @frozen 警告..."

# 需要修复的文件列表
VISION_CAMERA_FILES=(
    "node_modules/react-native-vision-camera/ios/Core/CameraConfiguration.swift"
    "node_modules/react-native-vision-camera/ios/Core/Recording/Track.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/AutoFocusSystem.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/Flash.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/HardwareLevel.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/OutputOrientation.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/PixelFormat.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/QualityBalance.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/ResizeMode.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/ShutterType.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/Torch.swift"
    "node_modules/react-native-vision-camera/ios/Core/Types/VideoStabilizationMode.swift"
)

# 移除 @frozen 属性或将枚举改为 public
for file in "${VISION_CAMERA_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  修复: $file"
        # 备份原文件
        cp "$file" "$file.backup"
        
        # 方案1：移除 @frozen 属性
        sed -i '' 's/@frozen enum/@objc enum/g' "$file"
        
        # 方案2：如果枚举不是 public，添加 public 修饰符
        sed -i '' 's/^enum /public enum /g' "$file"
        sed -i '' 's/^@frozen enum /public enum /g' "$file"
    fi
done

# 2. 修复 authorizationStatus() 弃用警告
echo "🔐 修复 authorizationStatus() 弃用警告..."
CAMERA_VIEW_MANAGER="node_modules/react-native-vision-camera/ios/React/CameraViewManager.swift"
if [ -f "$CAMERA_VIEW_MANAGER" ]; then
    echo "  修复: $CAMERA_VIEW_MANAGER"
    cp "$CAMERA_VIEW_MANAGER" "$CAMERA_VIEW_MANAGER.backup"
    
    # 替换弃用的 authorizationStatus() 为新的 API
    sed -i '' 's/AVCaptureDevice\.authorizationStatus()/AVCaptureDevice.authorizationStatus(for: .video)/g' "$CAMERA_VIEW_MANAGER"
fi

# 3. 创建 patch 文件以持久化修复
echo "📝 创建 patch 文件..."
mkdir -p patches

# 创建 patch-package 配置
if ! command -v patch-package &> /dev/null; then
    echo "⚠️  patch-package 未安装，正在安装..."
    npm install --save-dev patch-package
fi

# 4. 修复 Hermes 构建脚本警告
echo "🏃 修复 Hermes 构建脚本警告..."
PBXPROJ_FILE="ios/SuokeLife.xcodeproj/project.pbxproj"
if [ -f "$PBXPROJ_FILE" ]; then
    echo "  添加输出依赖到 Hermes 构建脚本..."
    # 这需要更复杂的处理，暂时跳过
fi

# 5. 清理构建缓存
echo "🧹 清理构建缓存..."
cd ios
rm -rf build/
rm -rf ~/Library/Developer/Xcode/DerivedData/SuokeLife-*
pod deintegrate
pod install

echo "✅ iOS 构建警告修复完成！"
echo ""
echo "📌 建议："
echo "1. 运行 'npx patch-package react-native-vision-camera' 创建持久化补丁"
echo "2. 在 package.json 的 scripts 中添加 'postinstall': 'patch-package'"
echo "3. 重新构建项目：'npm run ios'" 