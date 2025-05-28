#!/bin/bash

# 修复 Hermes 脚本阶段警告的脚本
# 这个脚本会修改 Xcode 项目配置，为 Hermes 脚本阶段添加输出依赖

set -e

echo "🔧 修复 Hermes 脚本阶段警告..."

# 检查是否在正确的目录
if [ ! -f "ios/SuokeLife.xcworkspace/contents.xcworkspacedata" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 备份原始项目文件
echo "📦 备份原始项目文件..."
cp ios/SuokeLife.xcodeproj/project.pbxproj ios/SuokeLife.xcodeproj/project.pbxproj.backup

# 使用 sed 修改项目文件，为 Hermes 脚本添加输出依赖
echo "🛠️ 修改项目配置..."

# 查找 Hermes 脚本阶段并添加输出文件
sed -i '' '/\[CP-User\] \[Hermes\] Replace Hermes for the right configuration, if needed/,/shellScript = / {
    /shellScript = /i\
			outputPaths = (\
				"$(DERIVED_FILE_DIR)/hermes-configured",\
			);
}' ios/SuokeLife.xcodeproj/project.pbxproj

# 检查修改是否成功
if grep -q "outputPaths" ios/SuokeLife.xcodeproj/project.pbxproj; then
    echo "✅ 成功添加输出依赖到 Hermes 脚本阶段"
else
    echo "⚠️ 未找到 Hermes 脚本阶段，可能已经修复或配置不同"
fi

# 清理 Xcode 缓存
echo "🧹 清理 Xcode 缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/SuokeLife-*

echo "✅ Hermes 脚本阶段警告修复完成！"
echo "📝 下次构建时应该不会再看到这个警告"
echo "💡 如果问题仍然存在，请在 Xcode 中手动检查脚本阶段配置" 