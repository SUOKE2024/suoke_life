#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始重置仓库...${NC}"

# 检查是否在项目根目录
if [ ! -f "pubspec.yaml" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 清理 git
echo "清理 git 历史..."
rm -rf .git

# 初始化新的 git 仓库
echo "初始化新的 git 仓库..."
git init

# 添加 .gitignore
echo "更新 .gitignore..."
cat > .gitignore << EOL
# Miscellaneous
*.class
*.log
*.pyc
*.swp
.DS_Store
.atom/
.buildlog/
.history
.svn/
migrate_working_dir/

# IntelliJ related
*.iml
*.ipr
*.iws
.idea/

# VS Code related
.vscode/

# Flutter/Dart/Pub related
**/doc/api/
**/ios/Flutter/.last_build_id
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
/build/
.fvm/

# Web related
lib/generated_plugin_registrant.dart

# Symbolication related
app.*.symbols

# Obfuscation related
app.*.map.json

# Android Studio will place build artifacts here
/android/app/debug
/android/app/profile
/android/app/release

# iOS related
**/ios/**/DerivedData/
**/ios/**/Icon?
**/ios/**/Pods/
**/ios/**/.symlinks/
**/ios/**/profile
**/ios/**/xcuserdata
**/ios/.generated/
**/ios/Flutter/.last_build_id
**/ios/Flutter/App.framework
**/ios/Flutter/Flutter.framework
**/ios/Flutter/Flutter.podspec
**/ios/Flutter/Generated.xcconfig
**/ios/Flutter/ephemeral
**/ios/Flutter/app.flx
**/ios/Flutter/app.zip
**/ios/Flutter/flutter_assets/
**/ios/Flutter/flutter_export_environment.sh
**/ios/ServiceDefinitions.json
**/ios/Runner/GeneratedPluginRegistrant.*

# macOS related
**/macos/Flutter/GeneratedPluginRegistrant.*
**/macos/Flutter/ephemeral

# Environment files
.env
.env.*
!.env.example

# Firebase config
google-services.json
GoogleService-Info.plist

# Coverage
coverage/
EOL

# 添加文件
echo "添加文件到 git..."
git add .

# 创建初始提交
echo "创建初始提交..."
git commit -m "Initial commit: Project structure setup"

# 添加远程仓库
echo "添加远程仓库..."
git remote add origin https://github.com/SUOKE2024/suoke_life.git

echo -e "${GREEN}仓库重置完成!${NC}"
echo -e "${YELLOW}请运行以下命令推送到 GitHub:${NC}"
echo "git push -f origin main" 