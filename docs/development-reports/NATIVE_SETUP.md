# 索克生活 - 原生项目设置

## 概述

本文档记录了为"索克生活"(Suoke Life)项目添加React Native原生支持的过程。

## 已完成的工作

### 1. 项目结构重组
- ✅ 将 `src/screens/health` 重命名为 `src/screens/life`
- ✅ 将 `src/screens/diagnosis` 重命名为 `src/screens/suoke`
- ✅ 新增 `src/screens/explore` 目录
- ✅ 删除 `src/screens/agents` 目录
- ✅ 更新底部导航栏配置

### 2. 新屏幕组件
- ✅ 创建 `ExploreScreen.tsx` - 探索健康内容界面
- ✅ 创建新的 `LifeScreen.tsx` - 生活健康管理界面
- ✅ 创建新的 `SuokeScreen.tsx` - SUOKE诊断界面
- ✅ 修复所有组件的主题和样式引用

### 3. 导航配置更新
- ✅ 更新 `MainNavigator.tsx` 中的导入路径
- ✅ 移除对已删除组件的引用
- ✅ 精简堆栈导航器配置

### 4. 原生项目初始化

#### Android 配置
- ✅ 创建 `android/` 目录结构
- ✅ 配置 `build.gradle` (项目级和应用级)
- ✅ 创建 `settings.gradle`
- ✅ 配置 `gradle.properties`
- ✅ 创建 `MainActivity.java` 和 `MainApplication.java`
- ✅ 配置 `AndroidManifest.xml`
- ✅ 创建资源文件 (`strings.xml`, `styles.xml`)
- ✅ 配置 Proguard 规则

#### iOS 配置
- ✅ 创建 `ios/` 目录结构
- ✅ 配置 `Info.plist`
- ✅ 创建 `Podfile` 用于依赖管理
- ✅ 配置应用权限 (相机、麦克风、相册)

#### 通用配置
- ✅ 创建 `app.json` 应用配置
- ✅ 更新 `index.js` 入口文件
- ✅ 配置 `react-native.config.js`
- ✅ 创建测试脚本 `scripts/test-native-setup.js`

## 应用配置

### 应用信息
- **应用名称**: SuokeLife
- **显示名称**: 索克生活
- **Android包名**: life.suoke
- **iOS Bundle ID**: 待配置

### 权限配置
- 📷 相机权限 - 用于健康检测和拍照
- 🎤 麦克风权限 - 用于语音交互
- 📱 相册权限 - 用于保存和选择图片
- 🌐 网络权限 - 用于API通信

## 下一步操作

### 对于开发者

1. **安装iOS依赖** (仅限macOS):
   ```bash
   cd ios
   pod install
   cd ..
   ```

2. **验证设置**:
   ```bash
   npm run test:native
   ```

3. **启动开发服务器**:
   ```bash
   npm start
   ```

4. **运行应用**:
   ```bash
   # Android (需要模拟器或设备)
   npm run android
   
   # iOS (需要模拟器，仅限macOS)
   npm run ios
   ```

### 环境要求

#### Android 开发
- Android Studio
- Android SDK
- ANDROID_HOME 环境变量
- Java 11+

#### iOS 开发 (仅限macOS)
- Xcode 12+
- CocoaPods
- iOS Simulator

## 故障排除

### 常见问题

1. **Metro bundler 启动失败**
   ```bash
   npx react-native start --reset-cache
   ```

2. **Android 构建失败**
   - 检查 ANDROID_HOME 环境变量
   - 确保 Android SDK 已正确安装
   - 清理项目: `cd android && ./gradlew clean`

3. **iOS 构建失败**
   - 运行 `cd ios && pod install`
   - 清理 Xcode 缓存: `cd ios && xcodebuild clean`

4. **依赖问题**
   ```bash
   npm run clean:all
   npm install
   ```

## 技术栈

- **React Native**: 0.73.2
- **TypeScript**: 5.0.4
- **Android**: API 21+ (Android 5.0+)
- **iOS**: iOS 12.0+
- **构建工具**: Gradle 8.0.1, Xcode Build System

## 项目状态

✅ **完成**: 基础原生项目结构已创建
🔄 **进行中**: 原生模块集成和优化
📋 **待办**: 应用图标、启动画面、发布配置

---

*最后更新: 2025-05-27 15:51:51* 