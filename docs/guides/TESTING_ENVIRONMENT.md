# 索克生活 - 测试环境设置指南

## 概述

本文档详细说明如何为"索克生活"项目设置Android和iOS的模拟器及真机测试环境。

## 🤖 Android 测试环境

### 1. Android Studio 安装与配置

#### 安装 Android Studio
1. 下载并安装 [Android Studio](https://developer.android.com/studio)
2. 启动 Android Studio，完成初始设置向导
3. 安装推荐的 SDK 组件

#### 配置环境变量
```bash
# 添加到 ~/.zshrc 或 ~/.bash_profile
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin

# 重新加载配置
source ~/.zshrc
```

#### 验证安装
```bash
# 检查 Android SDK
android --version

# 检查 ADB
adb version

# 检查环境变量
echo $ANDROID_HOME
```

### 2. Android 模拟器设置

#### 创建 AVD (Android Virtual Device)
1. 打开 Android Studio
2. 点击 "Tools" → "AVD Manager"
3. 点击 "Create Virtual Device"
4. 推荐配置：

**推荐的模拟器配置：**
- **设备**: Pixel 6 Pro (6.7", 1440 × 3120, 512 ppi)
- **系统镜像**: Android 13 (API 33) - Google APIs
- **RAM**: 4GB
- **存储**: 8GB
- **图形**: Hardware - GLES 2.0

#### 启动模拟器
```bash
# 列出可用的 AVD
emulator -list-avds

# 启动指定的 AVD
emulator -avd Pixel_6_Pro_API_33

# 或者通过 Android Studio 启动
```

### 3. Android 真机测试

#### 启用开发者选项
1. 打开手机"设置"
2. 找到"关于手机"
3. 连续点击"版本号" 7次
4. 返回设置，找到"开发者选项"

#### 配置调试选项
1. 开启"USB调试"
2. 开启"USB安装"
3. 开启"USB调试(安全设置)"

#### 连接设备
```bash
# 连接设备后检查
adb devices

# 应该显示类似：
# List of devices attached
# ABC123DEF456    device
```

## 🍎 iOS 测试环境 (仅限 macOS)

### 1. Xcode 安装与配置

#### 安装 Xcode
1. 从 App Store 安装 Xcode (最新版本)
2. 启动 Xcode，同意许可协议
3. 安装额外组件

#### 安装 Xcode Command Line Tools
```bash
xcode-select --install
```

#### 验证安装
```bash
# 检查 Xcode 版本
xcodebuild -version

# 检查可用的模拟器
xcrun simctl list devices
```

### 2. iOS 模拟器设置

#### 推荐的模拟器配置
- **iPhone 14 Pro** (iOS 16.0+)
- **iPhone 15** (iOS 17.0+)
- **iPad Pro 12.9-inch** (iPadOS 16.0+)

#### 创建和管理模拟器
```bash
# 列出可用的设备类型
xcrun simctl list devicetypes

# 列出可用的运行时
xcrun simctl list runtimes

# 创建新的模拟器
xcrun simctl create "iPhone 14 Pro Test" "iPhone 14 Pro" "iOS16.0"

# 启动模拟器
xcrun simctl boot "iPhone 14 Pro Test"
open -a Simulator
```

### 3. iOS 真机测试

#### 开发者账号配置
1. 注册 [Apple Developer Account](https://developer.apple.com)
2. 在 Xcode 中添加 Apple ID：
   - Xcode → Preferences → Accounts
   - 点击 "+" 添加 Apple ID

#### 设备配置
1. 连接 iOS 设备到 Mac
2. 在设备上信任此电脑
3. 在 Xcode 中：
   - Window → Devices and Simulators
   - 选择连接的设备
   - 点击 "Use for Development"

#### 证书和配置文件
```bash
# 自动管理签名（推荐用于开发）
# 在 Xcode 项目设置中启用 "Automatically manage signing"
```

## 🚀 运行测试

### 检查设备连接状态
```bash
# 检查所有连接的设备
npm run test:devices
```

让我创建这个检查脚本：

### Android 测试命令
```bash
# 启动 Metro bundler
npm start

# 在新终端运行 Android 应用
npm run android

# 指定特定设备运行
npm run android -- --deviceId=DEVICE_ID

# 运行在模拟器上
npm run android -- --simulator
```

### iOS 测试命令
```bash
# 启动 Metro bundler
npm start

# 在新终端运行 iOS 应用
npm run ios

# 指定特定模拟器
npm run ios -- --simulator="iPhone 14 Pro"

# 运行在真机上
npm run ios -- --device
```

## 🛠️ 调试工具

### React Native Debugger
```bash
# 安装 React Native Debugger
brew install --cask react-native-debugger

# 启动调试器
open "rndebugger://set-debugger-loc?host=localhost&port=8081"
```

### Flipper (Meta 官方调试工具)
```bash
# 安装 Flipper
brew install --cask flipper

# 在应用中启用 Flipper (已在项目中配置)
```

### Chrome DevTools
1. 在模拟器/设备上摇晃设备
2. 选择 "Debug"
3. 在 Chrome 中打开 http://localhost:8081/debugger-ui

## 📱 设备特定配置

### Android 性能优化
```bash
# 启用硬件加速
emulator -avd YOUR_AVD -gpu host

# 增加 RAM
emulator -avd YOUR_AVD -memory 4096

# 启用快照
emulator -avd YOUR_AVD -no-snapshot-save
```

### iOS 性能优化
```bash
# 重置模拟器
xcrun simctl erase all

# 清理派生数据
rm -rf ~/Library/Developer/Xcode/DerivedData
```

## 🔧 故障排除

### 常见 Android 问题

1. **ADB 连接问题**
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```

2. **模拟器启动慢**
   ```bash
   # 启用硬件加速
   emulator -avd YOUR_AVD -gpu host -no-boot-anim
   ```

3. **Gradle 构建失败**
   ```bash
   cd android
   ./gradlew clean
   ./gradlew assembleDebug
   ```

### 常见 iOS 问题

1. **Pod 安装问题**
   ```bash
   cd ios
   pod deintegrate
   pod install
   ```

2. **模拟器问题**
   ```bash
   xcrun simctl shutdown all
   xcrun simctl erase all
   ```

3. **签名问题**
   - 检查 Bundle Identifier 是否唯一
   - 确保开发者账号有效
   - 重新生成证书

## 📊 性能监控

### Metro 性能监控
```bash
# 启动带性能监控的 Metro
npm start -- --verbose
```

### 应用性能分析
```bash
# Android 性能分析
npm run android -- --variant=release

# iOS 性能分析
npm run ios -- --configuration Release
```

## 🧪 自动化测试

### 单元测试
```bash
# 运行所有测试
npm test

# 监听模式
npm test -- --watch
```

### E2E 测试 (Detox)
```bash
# 安装 Detox
npm install -g detox-cli

# 构建测试应用
detox build --configuration ios.sim.debug

# 运行 E2E 测试
detox test --configuration ios.sim.debug
```

## 📋 测试清单

### 发布前测试清单
- [ ] Android 模拟器测试通过
- [ ] iOS 模拟器测试通过
- [ ] Android 真机测试通过
- [ ] iOS 真机测试通过
- [ ] 所有核心功能正常
- [ ] 性能测试通过
- [ ] 内存泄漏检查
- [ ] 网络连接测试
- [ ] 权限请求测试

---

*最后更新: 2025-05-27 15:51:51* 