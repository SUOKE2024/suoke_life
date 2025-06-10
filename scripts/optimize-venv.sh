#!/bin/bash

# 虚拟环境优化脚本
# 用于清理和优化Python虚拟环境，减少项目大小

echo "🚀 开始虚拟环境优化..."
echo "优化前项目大小: $(du -sh . | cut -f1)"

# 1. 备份当前虚拟环境列表
echo "📝 记录当前虚拟环境..."
find services/ -name ".venv" -type d > venv_backup_list.txt
echo "发现 $(wc -l < venv_backup_list.txt) 个虚拟环境"

# 2. 计算虚拟环境总大小
echo "📊 计算虚拟环境大小..."
VENV_SIZE=$(find services/ -name ".venv" -type d -exec du -s {} \; | awk '{sum+=$1} END {print sum/1024/1024}')
echo "虚拟环境总大小: ${VENV_SIZE} GB"

# 3. 清理虚拟环境缓存
echo "🧹 清理虚拟环境缓存..."
find services/ -name ".venv" -type d -exec find {} -name "__pycache__" -type d -exec rm -rf {} + \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "*.pyc" -delete \; 2>/dev/null

# 4. 清理pip缓存
echo "🗑️ 清理pip缓存..."
find services/ -name ".venv" -type d -exec find {} -name ".cache" -type d -exec rm -rf {} + \; 2>/dev/null

# 5. 检查优化效果
echo "📈 检查优化效果..."
NEW_VENV_SIZE=$(find services/ -name ".venv" -type d -exec du -s {} \; | awk '{sum+=$1} END {print sum/1024/1024}')
SAVED_SIZE=$(echo "$VENV_SIZE - $NEW_VENV_SIZE" | bc)
echo "优化后虚拟环境大小: ${NEW_VENV_SIZE} GB"
echo "节省空间: ${SAVED_SIZE} GB"

echo "✅ 虚拟环境优化完成！"
echo "优化后项目大小: $(du -sh . | cut -f1)" 