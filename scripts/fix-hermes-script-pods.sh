#!/bin/bash

# 修复 Pods 项目中 Hermes 脚本阶段警告的脚本
# 这个脚本会修改 Pods 项目配置，为 Hermes 脚本阶段添加输出依赖

set -e

echo "🔧 修复 Pods 项目中的 Hermes 脚本阶段警告..."

# 检查是否在正确的目录
if [ ! -f "ios/Pods/Pods.xcodeproj/project.pbxproj" ]; then
    echo "❌ 错误：未找到 Pods 项目文件"
    exit 1
fi

# 备份原始项目文件
echo "📦 备份原始 Pods 项目文件..."
cp ios/Pods/Pods.xcodeproj/project.pbxproj ios/Pods/Pods.xcodeproj/project.pbxproj.backup

# 查看当前的Hermes脚本配置
echo "🔍 当前 Hermes 脚本配置："
grep -A 10 -B 5 "Replace Hermes for the right configuration" ios/Pods/Pods.xcodeproj/project.pbxproj || true

# 使用 sed 修改项目文件，为 Hermes 脚本添加输出依赖
echo "🛠️ 修改 Pods 项目配置..."

# 查找 Hermes 脚本阶段并添加输出文件
sed -i '' '/\[CP-User\] \[Hermes\] Replace Hermes for the right configuration, if needed/,/shellScript = / {
    /shellScript = /i\
			outputPaths = (\
				"$(DERIVED_FILE_DIR)/hermes-configured",\
			);
}' ios/Pods/Pods.xcodeproj/project.pbxproj

# 检查修改是否成功
if grep -A 15 "Replace Hermes for the right configuration" ios/Pods/Pods.xcodeproj/project.pbxproj | grep -q "outputPaths"; then
    echo "✅ 成功添加输出依赖到 Hermes 脚本阶段"
    echo "🔍 修改后的配置："
    grep -A 15 "Replace Hermes for the right configuration" ios/Pods/Pods.xcodeproj/project.pbxproj
else
    echo "⚠️ 修改可能未成功，让我们尝试另一种方法..."
    
    # 恢复备份
    cp ios/Pods/Pods.xcodeproj/project.pbxproj.backup ios/Pods/Pods.xcodeproj/project.pbxproj
    
    # 使用更精确的方法
    awk '
    /\[CP-User\] \[Hermes\] Replace Hermes for the right configuration, if needed/ {
        in_hermes_section = 1
    }
    in_hermes_section && /shellScript = / {
        print "\t\t\toutputPaths = ("
        print "\t\t\t\t\"$(DERIVED_FILE_DIR)/hermes-configured\","
        print "\t\t\t);"
        in_hermes_section = 0
    }
    { print }
    ' ios/Pods/Pods.xcodeproj/project.pbxproj.backup > ios/Pods/Pods.xcodeproj/project.pbxproj
    
    if grep -A 15 "Replace Hermes for the right configuration" ios/Pods/Pods.xcodeproj/project.pbxproj | grep -q "outputPaths"; then
        echo "✅ 使用备用方法成功添加输出依赖"
    else
        echo "❌ 自动修改失败，需要手动处理"
        echo "💡 请在 Xcode 中打开 Pods 项目，找到 Hermes 脚本阶段，并添加输出文件："
        echo "   $(DERIVED_FILE_DIR)/hermes-configured"
    fi
fi

# 清理 Xcode 缓存
echo "🧹 清理 Xcode 缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/SuokeLife-*

echo "✅ Hermes 脚本阶段警告修复完成！"
echo "📝 下次构建时应该不会再看到这个警告"
echo "💡 注意：这个修改会在下次 'pod install' 时被重置" 