#!/bin/bash

# 算诊微服务快速启动脚本

echo "=========================================="
echo "算诊微服务 (Calculation Service)"
echo "索克生活 - 传统中医算诊分析服务"
echo "=========================================="

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 检查UV包管理器
echo "检查UV包管理器..."
if ! command -v uv &> /dev/null; then
    echo "❌ UV包管理器未安装，请先安装UV"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV包管理器已安装"

# 安装依赖
echo "安装项目依赖..."
uv sync

# 激活虚拟环境并运行测试
echo "运行功能测试..."
source .venv/bin/activate && python simple_test.py

if [ $? -eq 0 ]; then
    echo "✅ 功能测试通过"
else
    echo "❌ 功能测试失败"
    exit 1
fi

# 运行API测试
echo "运行API测试..."
source .venv/bin/activate && python api_test.py

if [ $? -eq 0 ]; then
    echo "✅ API测试通过"
else
    echo "❌ API测试失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 算诊微服务启动成功！"
echo "=========================================="
echo ""
echo "📋 功能特性："
echo "  ✅ 五运六气分析"
echo "  ✅ 八字体质分析"
echo "  ✅ 八卦体质分析"
echo "  ✅ 子午流注分析"
echo "  ✅ 综合算诊分析"
echo ""
echo "🔧 可用命令："
echo "  测试功能: python simple_test.py"
echo "  测试API:  python api_test.py"
echo "  启动服务: python simple_server.py"
echo ""
echo "📖 文档："
echo "  项目说明: README.md"
echo "  项目总结: PROJECT_SUMMARY.md"
echo "  测试结果: api_test_results.json"
echo ""
echo "🌐 服务地址："
echo "  健康检查: http://localhost:8005/health"
echo "  API文档:  http://localhost:8005/docs"
echo ""
echo "==========================================" 