#!/bin/bash

echo "🚀 启动 Cursor 语音视频交互扩展..."

# 检查扩展是否已安装
if code --list-extensions | grep -q "cursor-voice-interaction"; then
    echo "✅ 扩展已安装"
else
    echo "📦 正在安装扩展..."
    code --install-extension cursor-voice-interaction-0.1.0.vsix
fi

# 启动 Cursor IDE
echo "🎤 启动 Cursor IDE..."
code .

echo "🎉 扩展已启动！"
echo ""
echo "📋 快速使用指南:"
echo "• 按 Cmd+Shift+V 切换语音模式"
echo "• 点击状态栏 🎤 图标开始语音识别"
echo "• 说出命令如：'你好'、'保存文件'、'生成代码'"
echo "• 启用摄像头进行手势控制"
echo ""
echo "🔧 配置 AI 功能:"
echo "• 在设置中搜索 'cursor-voice'"
echo "• 配置 OpenAI API 密钥"
echo "• 启用视频手势识别" 