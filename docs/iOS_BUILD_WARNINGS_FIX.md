# iOS 构建警告修复指南

## 问题描述

在构建 iOS 项目时，您可能会遇到以下警告：

### 1. VisionCamera 警告

```
@frozen has no effect on non-public enums
```

这些警告出现在 `react-native-vision-camera` 库的多个 Swift 文件中。

### 2. authorizationStatus() 弃用警告

```
'authorizationStatus()' was deprecated in iOS 14.0
```

### 3. Hermes 构建脚本警告

```
Run script build phase '[CP-User] [Hermes] Replace Hermes for the right configuration, if needed' will be run during every build
```

## 解决方案

### 方案一：快速修复（推荐）

1. **安装 patch-package**
   ```bash
   npm install --save-dev patch-package
   ```

2. **运行修复脚本**
   ```bash
   node scripts/fix-vision-camera-warnings.js
   ```

3. **创建补丁**
   ```bash
   npx patch-package react-native-vision-camera
   ```

4. **确保补丁在安装后自动应用**
   
   package.json 已经配置了 postinstall 脚本：
   ```json
   {
     "scripts": {
       "postinstall": "patch-package"
     }
   }
   ```

### 方案二：手动修复

如果自动修复脚本不起作用，可以手动修改文件：

1. **修复 @frozen 警告**
   
   在所有提到的 Swift 文件中，将：
   ```swift
   @frozen enum SomeEnum {
   ```
   
   改为：
   ```swift
   public enum SomeEnum {
   ```

2. **修复 authorizationStatus() 警告**
   
   在 `CameraViewManager.swift` 中，将：
   ```swift
   AVCaptureDevice.authorizationStatus()
   ```
   
   改为：
   ```swift
   AVCaptureDevice.authorizationStatus(for: .video)
   ```

### 方案三：忽略警告

如果这些警告不影响功能，可以在 Podfile 中添加配置来忽略它们：

```ruby
post_install do |installer|
  installer.pods_project.targets.each do |target|
    if target.name == 'VisionCamera'
      target.build_configurations.each do |config|
        config.build_settings['SWIFT_SUPPRESS_WARNINGS'] = 'YES'
        config.build_settings['GCC_WARN_INHIBIT_ALL_WARNINGS'] = 'YES'
      end
    end
  end
end
```

## Hermes 警告处理

Hermes 构建脚本警告通常不影响功能，但如果想要消除它：

1. 在 Xcode 中打开项目
2. 选择项目 -> Build Phases
3. 找到 "[CP-User] [Hermes] Replace Hermes..." 脚本
4. 取消勾选 "Based on dependency analysis"

## 清理和重建

修复后，建议清理并重建项目：

```bash
# 清理缓存
cd ios
rm -rf build/
rm -rf ~/Library/Developer/Xcode/DerivedData/SuokeLife-*
pod deintegrate
pod install

# 重新构建
cd ..
npm run ios
```

## 注意事项

1. 这些警告通常不会影响应用的功能
2. 每次更新 `react-native-vision-camera` 后可能需要重新应用补丁
3. 建议定期检查库的更新，看是否已经官方修复了这些问题

## 相关链接

- [react-native-vision-camera GitHub Issues](https://github.com/mrousavy/react-native-vision-camera/issues)
- [patch-package 文档](https://github.com/ds300/patch-package) 