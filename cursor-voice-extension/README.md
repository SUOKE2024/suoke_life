# Cursor Voice Interaction Extension

为 Cursor IDE 添加语音和视频交互功能的扩展。

## 🚀 功能特性

### 语音交互
- **语音识别**：支持中文和英文语音命令
- **语音合成**：AI 回复可通过语音播放
- **自然语言处理**：智能解析语音命令并执行相应操作

### 视频交互
- **手势识别**：通过摄像头识别手势控制 IDE
- **实时处理**：低延迟的视频流处理
- **可配置手势**：支持自定义手势映射

### AI 集成
- **智能命令解析**：使用 AI 理解复杂的自然语言指令
- **代码生成**：通过语音描述生成代码
- **智能对话**：与 AI 助手进行编程相关的对话

## 📦 安装

1. 克隆或下载此扩展到本地
2. 在终端中进入扩展目录
3. 运行安装命令：

```bash
npm install
```

4. 编译 TypeScript：

```bash
npm run compile
```

5. 在 VS Code 中按 `F5` 启动扩展开发模式

## ⚙️ 配置

在 VS Code 设置中配置以下选项：

- `cursor-voice.language`: 语音识别语言（默认：zh-CN）
- `cursor-voice.apiKey`: OpenAI API 密钥（用于 AI 功能）
- `cursor-voice.enableVideoGestures`: 启用视频手势识别

## 🎯 使用方法

### 语音命令

1. 按 `Ctrl+Shift+V` (Mac: `Cmd+Shift+V`) 切换语音模式
2. 或点击状态栏的 🎤 图标
3. 说出以下命令：

#### 文件操作
- "打开文件 'path/to/file.js'"
- "保存文件"
- "新建文件"

#### 代码生成
- "生成代码：创建一个计算斐波那契数列的函数"
- "写一个 React 组件"

#### 导航
- "查找 function"
- "跳转到第 50 行"
- "替换 old 为 new"

#### AI 对话
- "这段代码有什么问题？"
- "如何优化这个算法？"

### 手势控制

启用视频手势后，可使用以下手势：

- **👍 点赞**：格式化当前文档
- **✌️ 胜利手势**：保存文件
- **👊 握拳**：关闭当前标签
- **👈 向左滑动**：切换到上一个标签
- **👉 向右滑动**：切换到下一个标签

## 🛠️ 开发

### 项目结构

```
cursor-voice-extension/
├── src/
│   ├── extension.ts              # 主入口文件
│   └── services/
│       ├── voiceRecognitionService.ts    # 语音识别服务
│       ├── videoInteractionService.ts    # 视频交互服务
│       └── aiAssistantService.ts         # AI 助手服务
├── package.json                  # 扩展配置
├── tsconfig.json                # TypeScript 配置
└── README.md                    # 说明文档
```

### 构建命令

```bash
# 安装依赖
npm install

# 编译 TypeScript
npm run compile

# 监听文件变化并自动编译
npm run watch

# 打包扩展
vsce package
```

## 🔧 技术栈

- **TypeScript**: 主要开发语言
- **VS Code Extension API**: 扩展开发框架
- **Web Speech API**: 浏览器原生语音识别
- **MediaDevices API**: 摄像头访问
- **Canvas API**: 视频帧处理
- **OpenAI API**: AI 功能支持

## 🚨 注意事项

1. **隐私保护**：语音和视频数据仅在本地处理，不会上传到服务器
2. **浏览器兼容性**：需要支持 Web Speech API 的现代浏览器
3. **权限要求**：需要麦克风和摄像头权限
4. **API 密钥**：使用 AI 功能需要配置 OpenAI API 密钥

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [OpenAI API](https://platform.openai.com/docs) 