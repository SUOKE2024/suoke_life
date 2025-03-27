#!/bin/bash
set -e

# 更新GitHub Actions版本
# 这个脚本会更新所有工作流文件中的actions/checkout和actions/upload-artifact到最新版本

echo "开始更新GitHub Actions..."

# 更新actions/checkout@v3到v4
for file in $(find .github/workflows -type f -name "*.yml" | xargs grep -l "actions/checkout@v3"); do
  echo "更新 $file 中的 actions/checkout@v3 到 v4..."
  sed -i '' 's/actions\/checkout@v3/actions\/checkout@v4/g' "$file"
  
  # 检查是否有权限设置，如果没有则添加
  if ! grep -q "permissions:" "$file"; then
    # 在runs-on行后添加权限设置
    sed -i '' '/runs-on:/a\
    permissions:\
      contents: read' "$file"
  fi
done

# 更新actions/upload-artifact@v2或v3到v4
for file in $(find .github/workflows -type f -name "*.yml" | xargs grep -l "actions/upload-artifact@v[23]"); do
  echo "更新 $file 中的 actions/upload-artifact 到 v4..."
  sed -i '' 's/actions\/upload-artifact@v[23]/actions\/upload-artifact@v4/g' "$file"
done

echo "GitHub Actions更新完成!"
echo "请检查更新的文件并提交更改。" 