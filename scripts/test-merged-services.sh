#!/bin/bash

echo "🚀 测试合并后的服务Docker构建"
echo "================================"

# 定义要测试的服务
services=(
    "user-management-service"
    "unified-health-data-service" 
    "communication-service"
    "utility-services"
)

success_count=0
total_count=${#services[@]}

for service in "${services[@]}"; do
    echo ""
    echo "📦 测试服务: $service"
    echo "------------------------"
    
    if [ -d "services/$service" ]; then
        cd "services/$service"
        
        # 检查Dockerfile是否存在
        if [ -f "Dockerfile" ]; then
            echo "✅ 发现Dockerfile"
            
            # 尝试构建（只显示前几行输出）
            echo "🔨 开始构建..."
            if timeout 60s docker build -t "test-$service" . > build.log 2>&1; then
                echo "✅ 构建成功: $service"
                success_count=$((success_count + 1))
                
                # 清理测试镜像
                docker rmi "test-$service" > /dev/null 2>&1
            else
                echo "❌ 构建失败: $service"
                echo "错误日志 (最后10行):"
                tail -10 build.log
            fi
            
            # 清理日志文件
            rm -f build.log
        else
            echo "❌ 未找到Dockerfile"
        fi
        
        cd - > /dev/null
    else
        echo "❌ 服务目录不存在: services/$service"
    fi
done

echo ""
echo "📊 测试结果总结"
echo "================"
echo "成功: $success_count/$total_count"
echo "失败: $((total_count - success_count))/$total_count"

if [ $success_count -eq $total_count ]; then
    echo "🎉 所有服务构建成功！"
    exit 0
else
    echo "⚠️ 部分服务构建失败，需要修复"
    exit 1
fi 