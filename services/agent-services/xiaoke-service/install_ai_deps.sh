#!/bin/bash
# xiaoke-service AI依赖安装脚本
echo "🤖 开始安装AI/ML依赖..."
echo "⚠️  这可能需要较长时间，请耐心等待..."

cd "services/agent-services/xiaoke-service"

# 安装AI依赖（可选）
uv sync --extra ai --no-dev

echo "✅ AI依赖安装完成！"
