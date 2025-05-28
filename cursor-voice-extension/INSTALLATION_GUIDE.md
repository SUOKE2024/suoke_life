# Cursor 语音视频交互扩展 - 安装指南

## 🎯 概述

本指南将帮助您在 Cursor IDE 中安装和配置语音、视频交互功能。通过这个扩展，您可以：

- 🎤 使用语音命令控制 IDE
- 📹 通过手势进行视频交互
- 🤖 与 AI 助手进行自然对话
- 💻 提高编程效率和体验

## 📋 系统要求

### 硬件要求
- 麦克风（用于语音识别）
- 摄像头（用于视频交互，可选）
- 至少 4GB RAM
- 现代 CPU（支持实时音视频处理）

### 软件要求
- Cursor IDE 或 VS Code 1.74.0+
- Node.js 16.x 或更高版本
- npm 或 yarn 包管理器
- 现代浏览器内核（支持 Web Speech API）

### 操作系统支持
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 18.04+)

## 🚀 快速安装

### 方法一：从源码安装（推荐）

1. **克隆项目**
```bash
cd /path/to/your/workspace
git clone https://github.com/your-repo/cursor-voice-extension.git
cd cursor-voice-extension
```

2. **安装依赖**
```bash
npm install
```

3. **编译项目**
```bash
npm run compile
```

4. **在 Cursor 中加载扩展**
   - 打开 Cursor IDE
   - 按 `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`)
   - 输入 "Extensions: Install from VSIX"
   - 选择编译后的 `.vsix` 文件

### 方法二：开发模式安装

1. **打开扩展开发环境**
```bash
cd cursor-voice-extension
code .  # 或使用 cursor .
```

2. **启动开发模式**
   - 按 `F5` 启动扩展开发主机
   - 新窗口将自动加载扩展

## ⚙️ 详细配置

### 1. 基础配置

打开 Cursor 设置 (`Ctrl+,`)，搜索 "cursor-voice"：

```json
{
  "cursor-voice.language": "zh-CN",
  "cursor-voice.enableVideoGestures": false,
  "cursor-voice.enableVoiceFeedback": true,
  "cursor-voice.apiKey": ""
}
```

### 2. 语音识别配置

#### 支持的语言
- `zh-CN`: 中文（简体）
- `en-US`: 英语（美国）
- `en-GB`: 英语（英国）
- `ja-JP`: 日语
- `ko-KR`: 韩语

#### 配置示例
```json
{
  "cursor-voice.language": "zh-CN",
  "cursor-voice.voiceCommands": {
    "sensitivity": 0.8,
    "timeout": 5000,
    "continuous": true
  }
}
```

### 3. AI 功能配置

#### 获取 OpenAI API 密钥
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册并登录账户
3. 导航到 API Keys 页面
4. 创建新的 API 密钥
5. 复制密钥到配置中

#### 配置 API 密钥
```json
{
  "cursor-voice.apiKey": "sk-your-openai-api-key-here",
  "cursor-voice.aiModel": "gpt-3.5-turbo",
  "cursor-voice.maxTokens": 1000
}
```

### 4. 视频交互配置

#### 启用摄像头权限
1. 确保浏览器允许摄像头访问
2. 在系统设置中允许 Cursor 访问摄像头

#### 手势配置
```json
{
  "cursor-voice.enableVideoGestures": true,
  "cursor-voice.gestureSettings": {
    "sensitivity": 0.7,
    "detectionInterval": 100,
    "gestureMappings": {
      "thumbs_up": "editor.action.formatDocument",
      "peace_sign": "workbench.action.files.save",
      "swipe_left": "workbench.action.previousEditor",
      "swipe_right": "workbench.action.nextEditor"
    }
  }
}
```

## 🎮 使用教程

### 语音命令入门

1. **激活语音模式**
   - 快捷键：`Ctrl+Shift+V` (Mac: `Cmd+Shift+V`)
   - 或点击状态栏的 🎤 图标

2. **基础命令**
```
"你好" - 激活助手
"打开文件" - 打开文件对话框
"保存文件" - 保存当前文件
"新建文件" - 创建新文件
"查找文本" - 打开搜索框
```

3. **代码生成命令**
```
"生成代码：创建一个 React 组件"
"写一个计算斐波那契数列的函数"
"生成一个 API 请求函数"
```

### 手势控制入门

1. **启用视频交互**
```bash
# 在命令面板中执行
Cursor Voice: Start Video Interaction
```

2. **基础手势**
- 👍 **点赞**：格式化代码
- ✌️ **胜利手势**：保存文件
- 👊 **握拳**：关闭标签
- 👈 **向左**：上一个标签
- 👉 **向右**：下一个标签

## 🔧 故障排除

### 常见问题

#### 1. 语音识别不工作
**症状**：点击语音按钮后没有反应

**解决方案**：
```bash
# 检查麦克风权限
# Chrome: 设置 > 隐私和安全 > 网站设置 > 麦克风
# 确保允许 Cursor 访问麦克风
```

#### 2. AI 功能无法使用
**症状**：AI 对话返回错误

**解决方案**：
1. 检查 API 密钥是否正确
2. 验证网络连接
3. 检查 OpenAI 账户余额

#### 3. 视频手势识别不准确
**症状**：手势无法正确识别

**解决方案**：
```json
{
  "cursor-voice.gestureSettings": {
    "sensitivity": 0.5,  // 降低敏感度
    "detectionInterval": 200  // 增加检测间隔
  }
}
```

### 性能优化

#### 1. 减少 CPU 使用
```json
{
  "cursor-voice.performance": {
    "videoFrameRate": 15,  // 降低帧率
    "audioSampleRate": 16000,  // 降低音频采样率
    "enableGPUAcceleration": true
  }
}
```

#### 2. 内存优化
```json
{
  "cursor-voice.memory": {
    "maxCacheSize": "100MB",
    "enableMemoryCleanup": true,
    "cleanupInterval": 30000
  }
}
```

## 🔒 隐私和安全

### 数据处理原则
- ✅ 语音数据仅在本地处理
- ✅ 视频流不会上传到服务器
- ✅ AI 对话通过加密连接传输
- ✅ 不存储个人敏感信息

### 安全配置
```json
{
  "cursor-voice.security": {
    "enableLocalProcessing": true,
    "encryptApiCalls": true,
    "disableDataLogging": true
  }
}
```

## 📞 支持和反馈

### 获取帮助
- 📧 邮箱：song.xu@icloud.com
- 💬 GitHub Issues：[项目地址](https://github.com/your-repo/cursor-voice-extension/issues)
- 📖 文档：[在线文档](https://docs.cursor-voice.com)

### 反馈渠道
- 🐛 Bug 报告：GitHub Issues
- 💡 功能建议：GitHub Discussions
- ⭐ 评价：VS Code Marketplace

## 🎉 完成！

恭喜！您已经成功安装并配置了 Cursor 语音视频交互扩展。现在您可以：

1. 🎤 使用语音命令控制 IDE
2. 📹 通过手势进行交互
3. 🤖 与 AI 助手对话
4. 💻 享受更高效的编程体验

开始您的智能编程之旅吧！🚀 