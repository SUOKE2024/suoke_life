#!/bin/bash

# 索克生活项目深度清理脚本
# 包括虚拟环境和依赖包的清理

set -e

echo "🧹 索克生活项目深度清理工具"
echo "================================"

# 显示当前项目大小
echo "📊 当前项目大小："
du -sh . 2>/dev/null || echo "无法计算项目大小"
echo ""

# 计算各类文件的大小
echo "📋 文件大小分析："
echo "Node.js依赖: $(du -sh node_modules/ 2>/dev/null | cut -f1 || echo '未找到')"
echo "Python虚拟环境总计: $(find services/ -name '.venv' -exec du -sh {} + 2>/dev/null | awk '{sum+=$1} END {print sum "M"}' || echo '0M')"
echo "iOS Pods: $(du -sh ios/Pods/ 2>/dev/null | cut -f1 || echo '未找到')"
echo ""

# 询问用户要执行的清理操作
echo "请选择要执行的清理操作："
echo "1) 基础清理 (缓存、备份、临时文件)"
echo "2) 清理Node.js依赖 (node_modules)"
echo "3) 清理Python虚拟环境 (services/*/.venv)"
echo "4) 清理iOS依赖 (ios/Pods)"
echo "5) 全部清理 (谨慎使用)"
echo "6) 自定义清理"
echo ""

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo "🧹 执行基础清理..."
        ./scripts/cleanup-project.sh
        ;;
    2)
        echo "🗑️  清理Node.js依赖..."
        if [ -d "node_modules" ]; then
            echo "删除 node_modules/ ($(du -sh node_modules/ 2>/dev/null | cut -f1))"
            rm -rf node_modules/
            echo "✅ Node.js依赖已删除"
            echo "💡 运行 'npm install' 重新安装依赖"
        else
            echo "❌ 未找到 node_modules 目录"
        fi
        ;;
    3)
        echo "🗑️  清理Python虚拟环境..."
        venv_count=0
        total_size=0
        for venv_dir in $(find services/ -name '.venv' -type d 2>/dev/null); do
            size=$(du -sm "$venv_dir" 2>/dev/null | cut -f1)
            echo "删除 $venv_dir (${size}M)"
            rm -rf "$venv_dir"
            venv_count=$((venv_count + 1))
            total_size=$((total_size + size))
        done
        echo "✅ 已删除 $venv_count 个虚拟环境，释放 ${total_size}M 空间"
        echo "💡 运行各服务目录下的 'python -m venv .venv' 重新创建虚拟环境"
        ;;
    4)
        echo "🗑️  清理iOS依赖..."
        if [ -d "ios/Pods" ]; then
            echo "删除 ios/Pods/ ($(du -sh ios/Pods/ 2>/dev/null | cut -f1))"
            rm -rf ios/Pods/
            rm -f ios/Podfile.lock
            echo "✅ iOS依赖已删除"
            echo "💡 运行 'cd ios && pod install' 重新安装依赖"
        else
            echo "❌ 未找到 ios/Pods 目录"
        fi
        ;;
    5)
        echo "⚠️  全部清理 - 这将删除所有依赖和缓存文件"
        read -p "确定要继续吗？(y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo "🧹 执行全部清理..."
            
            # 基础清理
            ./scripts/cleanup-project.sh
            
            # Node.js依赖
            if [ -d "node_modules" ]; then
                echo "🗑️  删除 node_modules/"
                rm -rf node_modules/
            fi
            
            # Python虚拟环境
            echo "🗑️  删除所有Python虚拟环境..."
            find services/ -name '.venv' -type d -exec rm -rf {} + 2>/dev/null || true
            
            # iOS依赖
            if [ -d "ios/Pods" ]; then
                echo "🗑️  删除 ios/Pods/"
                rm -rf ios/Pods/
                rm -f ios/Podfile.lock
            fi
            
            echo "✅ 全部清理完成"
        else
            echo "❌ 取消清理操作"
        fi
        ;;
    6)
        echo "🔧 自定义清理选项："
        echo "请输入要清理的项目 (用空格分隔):"
        echo "  cache    - 清理缓存文件"
        echo "  backup   - 清理备份文件"
        echo "  node     - 清理Node.js依赖"
        echo "  python   - 清理Python虚拟环境"
        echo "  ios      - 清理iOS依赖"
        echo "  temp     - 清理临时文件"
        echo ""
        read -p "输入选项: " custom_options
        
        for option in $custom_options; do
            case $option in
                cache)
                    echo "🗑️  清理缓存文件..."
                    rm -rf .jest-cache/ coverage/
                    ;;
                backup)
                    echo "🗑️  清理备份文件..."
                    rm -rf .backup/
                    find . -name "*.backup.*" -type f -delete
                    ;;
                node)
                    echo "🗑️  清理Node.js依赖..."
                    rm -rf node_modules/
                    ;;
                python)
                    echo "🗑️  清理Python虚拟环境..."
                    find services/ -name '.venv' -type d -exec rm -rf {} + 2>/dev/null || true
                    ;;
                ios)
                    echo "🗑️  清理iOS依赖..."
                    rm -rf ios/Pods/
                    rm -f ios/Podfile.lock
                    ;;
                temp)
                    echo "🗑️  清理临时文件..."
                    rm -f *-report.json test-*.js
                    find . -name ".DS_Store" -delete 2>/dev/null || true
                    ;;
                *)
                    echo "❌ 未知选项: $option"
                    ;;
            esac
        done
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "📊 清理后项目大小："
du -sh . 2>/dev/null || echo "无法计算项目大小"

echo ""
echo "🎉 清理完成！"
echo ""
echo "📝 重建指南："
echo "  Node.js:  npm install"
echo "  Python:   cd services/<service> && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
echo "  iOS:      cd ios && pod install"
echo "  测试:     npm test" 