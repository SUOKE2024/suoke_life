#!/bin/bash
echo "🧹 快速清理缓存..."
rm -rf /tmp/metro-*
rm -rf /tmp/react-*
rm -rf node_modules/.cache
rm -rf .metro-cache
watchman watch-del-all 2>/dev/null || true
echo "✅ 清理完成" 