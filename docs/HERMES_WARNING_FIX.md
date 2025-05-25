# Hermes 构建脚本警告修复指南

## 问题描述

```
Run script build phase '[CP-User] [Hermes] Replace Hermes for the right configuration, if needed' will be run during every build because it does not specify any outputs.
```

这个警告表示 Hermes 构建脚本没有指定输出文件，导致每次构建都会运行该脚本。

## 解决方案

### 在 Xcode 中手动修复（推荐）

1. **打开 Xcode 项目**
   ```bash
   open ios/SuokeLife.xcworkspace
   ```

2. **导航到 Pods 项目的 Build Phases**
   - 在左侧项目导航器中选择 `Pods` 项目（不是 SuokeLife 项目）
   - 选择 `hermes-engine` 目标（Target）
   - 点击顶部的 `Build Phases` 标签

3. **找到 Hermes 脚本**
   - 展开所有的 "Run Script" 阶段
   - 找到名为 `[CP-User] [Hermes] Replace Hermes for the right configuration, if needed` 的脚本

4. **修复警告**
   
   有两种方法：

   **方法一：取消依赖分析（最简单）**
   - 在该脚本阶段，取消勾选 "Based on dependency analysis"
   - 这将使脚本在每次构建时都运行，但不会显示警告

   **方法二：添加输出文件（更优雅）**
   - 在脚本阶段的 "Output Files" 部分，点击 "+" 按钮
   - 添加以下输出路径：
     ```
     $(PODS_ROOT)/hermes-engine/destroot/Library/Frameworks/universal/hermes.xcframework
     ```

5. **保存并重新构建**
   - Command + S 保存更改
   - Command + Shift + K 清理构建
   - Command + B 重新构建

### 自动化修复脚本

我们也可以通过脚本自动修复这个问题：

```bash
node scripts/fix-hermes-script.js
```

## 详细步骤说明

### 在 Xcode 中的具体位置：

1. **项目导航器** → `Pods` 项目
2. **TARGETS** → `hermes-engine`
3. **Build Phases** 标签
4. **Run Script** 部分 → `[CP-User] [Hermes] Replace Hermes...`

### 脚本内容：
该脚本的作用是根据构建配置（Debug/Release）替换正确版本的 Hermes 引擎。

## 其他警告说明

### 1. 重复库警告
```
Ignoring duplicate libraries: '-lc++'
```
这是一个无害的警告，表示 C++ 标准库被多次链接。这不会影响应用功能。

### 2. Swift 标准库警告
```
Not running swift-stdlib-tool: ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES is enabled, but the product type 'com.apple.product-type.library.static' is not a wrapper type.
```
这个警告已经通过 Podfile 配置修复，但可能需要清理构建后才能生效。

## 验证修复

修复后重新构建项目：

```bash
npm run ios
```

如果警告消失，说明修复成功。

## 注意事项

- 这些警告不会影响应用的功能或性能
- Hermes 是 React Native 的 JavaScript 引擎，用于提升性能
- 每次运行 `pod install` 后，可能需要重新应用这些修复
- 建议使用方法一（取消依赖分析），因为它更简单且不会被 CocoaPods 覆盖 