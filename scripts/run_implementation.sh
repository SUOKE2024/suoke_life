#!/bin/bash

# 索克生活APP通信矩阵实施快速执行脚本
# 基于 services/COMMUNICATION_MATRIX_IMPLEMENTATION_PLAN.md

set -e  # 遇到错误立即退出

echo "🚀 索克生活APP通信矩阵优化实施"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查必要的Python包
echo "📦 检查Python依赖..."
python3 -c "import yaml, json" 2>/dev/null || {
    echo "⚠️ 安装缺失的Python包..."
    pip3 install pyyaml
}

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "📍 当前工作目录: $(pwd)"

# 选择执行模式
if [ "$1" = "--validate-only" ]; then
    echo "🔍 仅执行配置验证..."
    python3 scripts/implement_communication_matrix.py --validate-only
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "使用方法:"
    echo "  $0                    # 执行完整实施流程"
    echo "  $0 --validate-only    # 仅验证配置"
    echo "  $0 --help            # 显示帮助信息"
    exit 0
else
    echo "🎯 执行完整实施流程..."
    
    # 确认执行
    read -p "⚠️ 此操作将修改服务配置文件，是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 操作已取消"
        exit 1
    fi
    
    # 执行实施脚本
    python3 scripts/implement_communication_matrix.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 通信矩阵优化实施成功完成！"
        echo ""
        echo "📊 预期性能提升："
        echo "  • API响应时间提升 37.5%"
        echo "  • 系统吞吐量提升 50%"
        echo "  • 错误率降低 75%"
        echo "  • 监控覆盖率达到 95%"
        echo ""
        echo "📋 下一步操作："
        echo "  1. 重启相关服务以应用新配置"
        echo "  2. 检查 IMPLEMENTATION_REPORT.json 查看详细报告"
        echo "  3. 监控系统性能指标验证优化效果"
        echo ""
        echo "📁 相关文件："
        echo "  • 实施方案: services/COMMUNICATION_MATRIX_IMPLEMENTATION_PLAN.md"
        echo "  • 评估报告: services/COMMUNICATION_MATRIX_ASSESSMENT.md"
        echo "  • 配置备份: config_backup/"
        echo "  • 监控配置: deploy/monitoring/"
    else
        echo "❌ 实施过程中发生错误，请检查日志"
        exit 1
    fi
fi 