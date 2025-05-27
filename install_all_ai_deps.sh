#!/bin/bash
# 索克生活项目 - 批量AI依赖安装脚本
echo "🚀 开始批量安装所有智能体服务的AI依赖..."

SERVICES=(
    "services/agent-services/xiaoai-service"
    "services/agent-services/xiaoke-service"
    "services/agent-services/laoke-service"
    "services/agent-services/soer-service"
)

for service in "${SERVICES[@]}"; do
    if [ -d "$service" ]; then
        echo "📦 安装 $service 的AI依赖..."
        cd "$service"
        if [ -f "install_ai_deps.sh" ]; then
            ./install_ai_deps.sh
        else
            echo "⚠️  未找到AI依赖安装脚本"
        fi
        cd - > /dev/null
        echo "✅ $service 完成"
        echo "---"
    else
        echo "❌ 服务不存在: $service"
    fi
done

echo "🎉 所有智能体服务AI依赖安装完成！"
