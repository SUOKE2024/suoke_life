#!/bin/bash

# Android环境配置脚本
echo "🔧 配置Android开发环境..."

# 检查Android Studio是否安装
if [ ! -d "/Applications/Android Studio.app" ]; then
    echo "❌ 请先安装Android Studio"
    echo "下载地址: https://developer.android.com/studio"
    exit 1
fi

# 设置ANDROID_HOME环境变量
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin

# 添加到shell配置文件
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
fi

if [ ! -z "$SHELL_CONFIG" ]; then
    echo "📝 添加环境变量到 $SHELL_CONFIG"
    
    # 检查是否已经配置
    if ! grep -q "ANDROID_HOME" "$SHELL_CONFIG"; then
        echo "" >> "$SHELL_CONFIG"
        echo "# Android SDK" >> "$SHELL_CONFIG"
        echo "export ANDROID_HOME=\$HOME/Library/Android/sdk" >> "$SHELL_CONFIG"
        echo "export PATH=\$PATH:\$ANDROID_HOME/emulator" >> "$SHELL_CONFIG"
        echo "export PATH=\$PATH:\$ANDROID_HOME/platform-tools" >> "$SHELL_CONFIG"
        echo "export PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin" >> "$SHELL_CONFIG"
        echo "✅ 环境变量已添加到 $SHELL_CONFIG"
        echo "请运行: source $SHELL_CONFIG"
    else
        echo "✅ Android环境变量已配置"
    fi
fi

# 检查SDK是否安装
if [ -d "$ANDROID_HOME" ]; then
    echo "✅ Android SDK 已安装: $ANDROID_HOME"
else
    echo "⚠️  请在Android Studio中安装SDK"
    echo "路径: Android Studio > Preferences > Appearance & Behavior > System Settings > Android SDK"
fi

echo "🎉 Android环境配置完成！" 