#!/bin/bash

echo "Updating project dependencies..."

# 1. 备份当前的 pubspec.yaml
cp pubspec.yaml pubspec.yaml.backup

# 2. 更新特定版本约束
echo "Updating version constraints..."
sed -i '' 's/analyzer: .*/analyzer: ^6.11.0/g' pubspec.yaml
sed -i '' 's/auto_route: .*/auto_route: ^9.2.2/g' pubspec.yaml
sed -i '' 's/auto_route_generator: .*/auto_route_generator: ^9.0.0/g' pubspec.yaml
sed -i '' 's/envied: .*/envied: ^1.0.0/g' pubspec.yaml
sed -i '' 's/envied_generator: .*/envied_generator: ^1.0.0/g' pubspec.yaml
sed -i '' 's/uni_links: .*/app_links: ^3.4.5/g' pubspec.yaml

# 3. 清理并重新获取依赖
echo "Cleaning and getting dependencies..."
flutter clean
flutter pub get

# 4. 如果获取依赖失败，还原备份
if [ $? -ne 0 ]; then
    echo "Dependency resolution failed, restoring backup..."
    mv pubspec.yaml.backup pubspec.yaml
    flutter pub get
    exit 1
fi

# 5. 删除备份
rm pubspec.yaml.backup

# 6. 重新生成代码
echo "Regenerating code..."
dart run build_runner clean
dart run build_runner build --delete-conflicting-outputs

echo "Dependencies update complete!"

# 7. 提示下一步操作
echo "
Next steps:
1. Check pubspec.yaml for any conflicts
2. Run tests to verify everything works
3. Check if auto_route navigation still works correctly
4. Update any deprecated code usage
" 