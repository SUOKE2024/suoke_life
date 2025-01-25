#!/bin/bash

echo "Starting project cleanup..."

# 1. 首先备份重要文件
echo "Backing up important files..."
mkdir -p .backup
cp -f pubspec.yaml .backup/
cp -f analysis_options.yaml .backup/
cp -f .env .backup/ 2>/dev/null || :
cp -rf lib/app/core/router .backup/router 2>/dev/null || :
cp -rf lib/app/presentation/pages .backup/pages 2>/dev/null || :
cp -rf test/navigation .backup/navigation_tests 2>/dev/null || :

# 2. 清理根目录多余文件
echo "Cleaning root directory..."
rm -rf ios/android ios/ios ios/linux ios/macos ios/web ios/windows
rm -rf ios_backup
rm -rf android/app/src/main/kotlin/life/suoke/suoke_app
rm -rf android/app/src/main/kotlin/life/suoke/suoke_life
rm -f suoke_app.iml suoke_app_android.iml suoke_life_android.iml

# 3. 清理生成的文件和缓存
echo "Cleaning generated files and caches..."
find . -name "*.g.dart" -type f -delete
find . -name "*.gr.dart" -type f -delete
find . -name "*.freezed.dart" -type f -delete
find . -name "*.mocks.dart" -type f -delete
find . -name ".DS_Store" -type f -delete
rm -rf build/ .dart_tool/ .flutter-plugins .flutter-plugins-dependencies

# 4. 重组项目结构
echo "Restructuring project..."
mkdir -p lib/app/{core,data,domain,features,presentation}
mkdir -p lib/app/core/{config,router,env,di}
mkdir -p lib/app/presentation/{pages,widgets}
mkdir -p lib/app/features/{ai,chat,explore,home,life,profile,suoke}
mkdir -p test/{unit,widget,integration,navigation}
mkdir -p assets/{images,config,animations}
mkdir -p docs/{api,database,deployment}

# 5. 恢复备份的文件
echo "Restoring important files..."
cp -f .backup/pubspec.yaml ./
cp -f .backup/analysis_options.yaml ./
cp -f .backup/.env ./ 2>/dev/null || :
cp -rf .backup/router lib/app/core/ 2>/dev/null || :
cp -rf .backup/pages lib/app/presentation/ 2>/dev/null || :
cp -rf .backup/navigation_tests test/navigation/ 2>/dev/null || :

# 6. 清理备份
echo "Cleaning up backup..."
rm -rf .backup

# 7. 创建必要的基础文件
echo "Creating base files..."
touch lib/app/core/config/app_config.dart
touch lib/app/core/env/env_config.dart
touch lib/app/features/ai/services/ai_service.dart
touch lib/app/presentation/pages/main/main_page.dart

# 8. 更新权限
echo "Updating permissions..."
chmod +x scripts/*.sh

echo "Cleanup complete!"

# 9. 提示下一步操作
echo "
Next steps:
1. Run 'flutter pub get'
2. Run 'flutter pub run build_runner build --delete-conflicting-outputs'
3. Check if all important files are in place
4. Run tests to verify everything works
" 