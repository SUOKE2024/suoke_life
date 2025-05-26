#!/bin/bash

# 修复 react-native-sqlite-storage 配置警告的脚本

set -e

echo "🔧 修复 react-native-sqlite-storage 配置警告..."

# 检查是否在正确的目录
if [ ! -f "react-native.config.js" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 备份原始配置文件
echo "📦 备份原始配置文件..."
cp react-native.config.js react-native.config.js.backup

# 创建新的配置文件，移除有问题的sqlite-storage配置
echo "🛠️ 更新 react-native.config.js..."

cat > react-native.config.js << 'EOF'
module.exports = {
  dependencies: {
    // 移除有问题的 sqlite-storage 配置
    // 'react-native-sqlite-storage': {
    //   platforms: {
    //     android: {
    //       sourceDir: '../node_modules/react-native-sqlite-storage/platforms/android',
    //       packageImportPath: 'import org.pgsqlite.SQLitePluginPackage;',
    //       packageInstance: 'new SQLitePluginPackage()',
    //     },
    //   },
    // },
  },
  assets: ['./src/assets/fonts/'],
  project: {
    ios: {},
    android: {},
  },
};
EOF

echo "✅ 成功更新配置文件"

# 检查是否需要重新安装依赖
echo "🔍 检查是否需要重新链接原生依赖..."

# 如果项目实际上不使用SQLite，我们可以考虑移除这个依赖
echo "⚠️ 注意：如果项目不使用SQLite数据库，建议移除 react-native-sqlite-storage 依赖"
echo "   可以运行：npm uninstall react-native-sqlite-storage @types/react-native-sqlite-storage"

echo "🎉 配置修复完成！"
echo "💡 提示：如果仍有警告，请重新运行 pod install" 