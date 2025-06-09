#!/bin/bash

# 索克生活项目紧急修复脚本
# 解决Metro缓存和Watchman问题

set -e

echo "🚨 开始紧急修复索克生活项目..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查项目根目录
if [ ! -f "package.json" ]; then
    log_error "请在项目根目录运行此脚本"
    exit 1
fi

log_info "当前目录: $(pwd)"

# 1. 停止所有相关进程
log_info "停止所有相关进程..."
pkill -f "react-native" || true
pkill -f "metro" || true
pkill -f "node" || true

# 2. 清理Watchman
log_info "清理Watchman..."
if command -v watchman &> /dev/null; then
    watchman watch-del-all
    watchman shutdown-server
    log_info "Watchman已清理"
else
    log_warning "Watchman未安装，跳过清理"
fi

# 3. 清理Metro缓存
log_info "清理Metro缓存..."
rm -rf /tmp/metro-*
rm -rf /tmp/react-*
rm -rf /tmp/haste-*
rm -rf ~/.metro
log_info "Metro缓存已清理"

# 4. 清理Node.js缓存
log_info "清理Node.js缓存..."
rm -rf node_modules/.cache
rm -rf .metro-cache
rm -rf /tmp/metro-cache
npm cache clean --force
log_info "Node.js缓存已清理"

# 5. 清理React Native缓存
log_info "清理React Native缓存..."
if command -v npx &> /dev/null; then
    npx react-native-clean-project --remove-iOS-build --remove-android-build
fi

# 6. 清理iOS缓存（如果存在）
if [ -d "ios" ]; then
    log_info "清理iOS缓存..."
    cd ios
    rm -rf build
    rm -rf DerivedData
    rm -rf ~/Library/Developer/Xcode/DerivedData
    if [ -f "Podfile" ]; then
        rm -rf Pods
        rm -f Podfile.lock
    fi
    cd ..
fi

# 7. 清理Android缓存（如果存在）
if [ -d "android" ]; then
    log_info "清理Android缓存..."
    cd android
    ./gradlew clean || true
    rm -rf build
    rm -rf .gradle
    cd ..
fi

# 8. 重新安装依赖
log_info "重新安装依赖..."
rm -rf node_modules
rm -f package-lock.json
rm -f yarn.lock

# 使用npm安装
npm install

# 9. 修复Metro配置
log_info "优化Metro配置..."
cat > metro.config.js << 'EOF'
const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');
const path = require('path');

const config = {
  resolver: {
    blacklistRE: /node_modules\/.*\/node_modules\/react-native\/.*/,
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  transformer: {
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },
  watchFolders: [
    path.resolve(__dirname, 'src'),
  ],
  resetCache: true,
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
EOF

# 10. 创建Watchman配置
log_info "创建Watchman配置..."
cat > .watchmanconfig << 'EOF'
{
  "ignore_dirs": [
    "node_modules",
    ".git",
    "ios/build",
    "android/build",
    "android/.gradle",
    ".metro-cache",
    "coverage",
    "reports"
  ]
}
EOF

# 11. 优化package.json脚本
log_info "优化启动脚本..."
npm pkg set scripts.start="react-native start --reset-cache"
npm pkg set scripts.start:fresh="npm run clean && npm start"
npm pkg set scripts.clean="rm -rf /tmp/metro-* && rm -rf /tmp/react-* && rm -rf node_modules/.cache"

# 12. 创建快速清理脚本
cat > scripts/quick-clean.sh << 'EOF'
#!/bin/bash
echo "🧹 快速清理缓存..."
rm -rf /tmp/metro-*
rm -rf /tmp/react-*
rm -rf node_modules/.cache
rm -rf .metro-cache
watchman watch-del-all 2>/dev/null || true
echo "✅ 清理完成"
EOF

chmod +x scripts/quick-clean.sh

# 13. 重新安装iOS依赖（如果需要）
if [ -d "ios" ] && [ -f "ios/Podfile" ]; then
    log_info "重新安装iOS依赖..."
    cd ios
    pod install --repo-update
    cd ..
fi

# 14. 验证修复
log_info "验证修复结果..."

# 检查关键文件
if [ ! -f "metro.config.js" ]; then
    log_error "Metro配置文件创建失败"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    log_error "依赖安装失败"
    exit 1
fi

log_info "✅ 紧急修复完成！"
echo ""
echo "📋 修复内容："
echo "  ✅ 清理了所有缓存"
echo "  ✅ 重新安装了依赖"
echo "  ✅ 优化了Metro配置"
echo "  ✅ 配置了Watchman"
echo "  ✅ 创建了清理脚本"
echo ""
echo "🚀 现在可以尝试启动项目："
echo "  npm start"
echo ""
echo "💡 如果还有问题，运行："
echo "  ./scripts/quick-clean.sh && npm start"
echo ""
echo "📖 查看完整优化计划："
echo "  cat ARCHITECTURE_OPTIMIZATION_PLAN.md" 