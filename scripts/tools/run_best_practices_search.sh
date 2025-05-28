#!/bin/bash

# GitHub最佳实践搜索运行脚本
# 用于索克生活项目的最佳实践研究

echo "🔍 开始搜索GitHub最佳实践项目..."
echo "================================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 检查必要的Python包
echo "📦 检查Python依赖..."
python3 -c "import requests, json" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 安装必要的Python包..."
    pip3 install requests
fi

# 设置工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查配置文件
if [ ! -f "best_practices_config.json" ]; then
    echo "❌ 错误: 未找到配置文件 best_practices_config.json"
    exit 1
fi

# 运行搜索脚本
echo "🚀 开始执行搜索..."
python3 github_best_practices_search.py

# 检查结果
if [ -f "github_best_practices_evaluation.json" ]; then
    echo "✅ 搜索完成！结果已保存到 github_best_practices_evaluation.json"
    
    # 显示简要统计
    echo ""
    echo "📊 搜索结果统计:"
    echo "================================================"
    
    # 统计项目数量
    total_projects=$(python3 -c "
import json
with open('github_best_practices_evaluation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'总项目数: {len(data)}')

# 按推荐等级统计
recommendations = {}
for item in data:
    rec = item.get('recommendation', '未知')
    recommendations[rec] = recommendations.get(rec, 0) + 1

for rec, count in recommendations.items():
    print(f'{rec}: {count}个项目')
")
    echo "$total_projects"
    
    echo ""
    echo "📋 查看详细结果:"
    echo "- 完整结果: cat github_best_practices_evaluation.json"
    echo "- 查看指南: cat ../docs/github_best_practices_guide.md"
    echo "- 手动清单: cat ../docs/manual_search_checklist.md"
    
else
    echo "❌ 搜索失败，请检查网络连接和API限制"
    echo ""
    echo "💡 备选方案:"
    echo "1. 检查GitHub API访问限制"
    echo "2. 使用手动搜索清单: ../docs/manual_search_checklist.md"
    echo "3. 设置GitHub Token环境变量: export GITHUB_TOKEN=your_token"
fi

echo ""
echo "🎯 针对索克生活项目的重点关注领域:"
echo "1. 微服务架构优化 (go-kit, istio)"
echo "2. React Native最佳实践 (ignite, react-navigation)"
echo "3. AI多智能体系统 (langchain, autogen)"
echo "4. 健康数据管理 (fhir, healthcare-standards)"
echo "5. 区块链集成 (hyperledger, zero-knowledge)"
echo ""
echo "📚 更多信息请查看: docs/github_best_practices_guide.md" 