#!/bin/bash

# 监控 iOS 构建进度的脚本

echo "📱 监控 iOS 构建进度..."
echo "⏰ 开始时间: $(date)"
echo ""

# 检查构建进程
check_build_process() {
    local process=$(ps aux | grep xcodebuild | grep -v grep)
    if [ -n "$process" ]; then
        echo "🔄 构建正在进行中..."
        echo "$process" | awk '{print "   PID: " $2 ", CPU: " $3 "%, 内存: " $4 "%"}'
        return 0
    else
        echo "✅ 构建已完成或未在运行"
        return 1
    fi
}

# 检查Metro进程
check_metro_process() {
    local metro=$(ps aux | grep "react-native start\|Metro" | grep -v grep)
    if [ -n "$metro" ]; then
        echo "🚀 Metro bundler 正在运行"
        return 0
    else
        echo "⚠️ Metro bundler 未运行"
        return 1
    fi
}

# 检查设备连接
check_device() {
    echo "📱 检查设备连接状态..."
    xcrun devicectl list devices | grep -E "(iPhone|iPad)" | head -5
}

# 主监控循环
monitor_build() {
    local count=0
    local max_checks=60  # 最多检查5分钟
    
    while [ $count -lt $max_checks ]; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 构建状态检查 #$((count + 1))"
        echo "⏰ 当前时间: $(date '+%H:%M:%S')"
        echo ""
        
        if ! check_build_process; then
            echo ""
            echo "🎉 构建完成！"
            break
        fi
        
        echo ""
        check_metro_process
        echo ""
        
        # 每30秒检查一次
        if [ $((count % 6)) -eq 0 ]; then
            check_device
            echo ""
        fi
        
        echo "⏳ 等待5秒后继续检查..."
        sleep 5
        count=$((count + 1))
        echo ""
    done
    
    if [ $count -eq $max_checks ]; then
        echo "⚠️ 监控超时，构建可能需要更长时间"
    fi
}

# 开始监控
monitor_build

echo ""
echo "📋 构建监控完成"
echo "⏰ 结束时间: $(date)" 