#!/bin/bash

# 激进的项目清理脚本
# 警告：此脚本会删除大量文件，请确保有备份

echo "⚠️  激进清理模式启动..."
echo "当前项目大小: $(du -sh . | cut -f1)"

# 1. 清理重复的大型编译文件
echo "🔥 清理重复的大型编译文件..."

# 删除重复的grpc编译文件（每个约40MB）
echo "删除重复的grpc编译文件..."
GRPC_FILES=$(find services/ -path "*/.venv/*/grpc/_cython/cygrpc.cpython-313-darwin.so" | wc -l)
echo "发现 $GRPC_FILES 个grpc编译文件"
find services/ -path "*/.venv/*/grpc/_cython/cygrpc.cpython-313-darwin.so" -exec rm -f {} \;

# 删除重复的grpc_tools编译文件（每个约28MB）
echo "删除重复的grpc_tools编译文件..."
find services/ -path "*/.venv/*/grpc_tools/_protoc_compiler.cpython-313-darwin.so" -exec rm -f {} \;

# 删除重复的cryptography编译文件（每个约20MB）
echo "删除重复的cryptography编译文件..."
find services/ -path "*/.venv/*/cryptography/hazmat/bindings/_rust.abi3.so" -exec rm -f {} \;

# 删除重复的OpenCV编译文件（每个约33MB）
echo "删除重复的OpenCV编译文件..."
find services/ -path "*/.venv/*/cv2/cv2.abi3.so" -exec rm -f {} \;

# 删除重复的mypy编译文件（每个约25MB）
echo "删除重复的mypy编译文件..."
find services/ -path "*/.venv/*/3204bda914b7f2c6f497__mypyc.cpython-313-darwin.so" -exec rm -f {} \;

# 2. 清理测试和文档文件
echo "📚 清理测试和文档文件..."
find services/ -name ".venv" -type d -exec find {} -name "tests" -type d -exec rm -rf {} + \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "test" -type d -exec rm -rf {} + \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "docs" -type d -exec rm -rf {} + \; 2>/dev/null

# 3. 清理示例和演示文件
echo "🎭 清理示例和演示文件..."
find services/ -name ".venv" -type d -exec find {} -name "examples" -type d -exec rm -rf {} + \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "demo" -type d -exec rm -rf {} + \; 2>/dev/null

# 4. 清理语言包和本地化文件
echo "🌍 清理语言包..."
find services/ -name ".venv" -type d -exec find {} -name "locale" -type d -exec rm -rf {} + \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "locales" -type d -exec rm -rf {} + \; 2>/dev/null

# 5. 清理大型数据文件
echo "💾 清理大型数据文件..."
find services/ -name ".venv" -type d -exec find {} -name "*.dat" -size +1M -delete \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "*.bin" -size +1M -delete \; 2>/dev/null

# 6. 清理编译缓存
echo "🗑️ 清理编译缓存..."
find services/ -name ".venv" -type d -exec find {} -name "*.egg-info" -type d -exec rm -rf {} + \; 2>/dev/null
find services/ -name ".venv" -type d -exec find {} -name "*.dist-info" -type d -exec rm -rf {} + \; 2>/dev/null

echo "✅ 激进清理完成！"
echo "清理后项目大小: $(du -sh . | cut -f1)"

# 计算节省的空间
echo "📊 重新计算虚拟环境大小..."
NEW_VENV_SIZE=$(find services/ -name ".venv" -type d -exec du -s {} \; | awk '{sum+=$1} END {print sum/1024/1024}')
echo "清理后虚拟环境大小: ${NEW_VENV_SIZE} GB" 