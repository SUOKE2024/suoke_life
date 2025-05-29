#!/bin/bash
# soer-service AI依赖安装脚本
echo "🤖 开始安装AI/ML依赖..."
echo "⚠️  这可能需要较长时间，请耐心等待..."

cd "services/agent-services/soer-service"

# 安装ML依赖（可选）
uv sync --extra ml --no-dev

echo "✅ AI/ML依赖安装完成！"
