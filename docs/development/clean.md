# 索克生活（Suoke Life）项目缓存清理指南

在开发过程中，缓存文件可能会影响应用的正常运行或导致不可预见的问题。本文档提供了清理项目缓存的方法和说明。

## 清理工具

项目提供了两种清理缓存的工具：

1. **JavaScript 清理脚本**: 一个功能丰富的 Node.js 脚本，支持各种选项和定制清理
2. **Shell 清理脚本**: 一个简单直接的 Shell 脚本，一次性清理所有常见缓存

## 使用方法

### 使用 NPM 脚本

在项目根目录下执行以下命令：

```bash
# 显示帮助信息
npm run clean

# 清理所有缓存
npm run clean:all

# 仅清理 React Native 缓存
npm run clean:rn

# 仅清理 iOS 构建缓存
npm run clean:ios

# 仅清理 Android 构建缓存
npm run clean:android

# 使用 Shell 脚本清理（一次性清理所有缓存）
npm run clean:sh
```

### 直接使用 JavaScript 脚本

JavaScript 清理脚本提供了更多灵活性：

```bash
# 显示帮助信息
node scripts/clean.js --help

# 清理 React Native 缓存和 iOS 缓存
node scripts/clean.js --react-native --ios

# 清理 Python 缓存和虚拟环境
node scripts/clean.js --python-cache --python-venv

# 清理 Docker 相关缓存
node scripts/clean.js --docker

# 清理所有缓存并自动确认提示
node scripts/clean.js --all --yes
```

### 可用选项

JavaScript 清理脚本支持以下选项：

| 选项 | 说明 |
|------|------|
| `--react-native` | 清理 React Native 相关缓存（Metro, Watchman, ESLint 等） |
| `--node-modules` | 清理 Node 模块缓存（删除 node_modules 目录和锁文件） |
| `--ios` | 清理 iOS 构建缓存（Pods, build 目录等） |
| `--android` | 清理 Android 构建缓存（.gradle, build 目录等） |
| `--temp` | 清理项目临时文件 |
| `--python-venv` | 清理 Python 虚拟环境 |
| `--python-cache` | 清理 Python 缓存文件（__pycache__, .pyc 文件） |
| `--docker` | 清理 Docker 镜像和容器（需要确认） |
| `--all` | 清理所有缓存 |
| `--yes` | 自动确认所有操作（跳过交互式提示） |
| `--help` | 显示帮助信息 |

## 清理内容说明

### React Native 缓存

- Metro 捆绑器缓存（/tmp/metro-*）
- React Native 临时文件（/tmp/react-*）
- Haste 模块映射缓存（/tmp/haste-*）
- Watchman 缓存（.watchman-cookie-*）
- ESLint 缓存（.eslintcache）

### Node 模块

- node_modules 目录
- package-lock.json 文件
- yarn.lock 文件

### iOS 缓存

- iOS build 目录
- Pods 目录
- Podfile.lock 文件
- Xcode 用户数据
- 打包的 JavaScript 包文件

### Android 缓存

- Android build 目录
- .gradle 缓存
- 打包的资源和 bundle 文件

### Python 缓存

- 虚拟环境目录（venv）
- Python 编译缓存（__pycache__ 目录）
- 编译的 Python 文件（.pyc）

### Docker 缓存

- 项目相关 Docker 容器
- 未使用的 Docker 镜像
- 悬空镜像

## 注意事项

1. 清理 Node 模块后，需要重新运行 `npm install` 安装依赖。
2. 清理 iOS 缓存后，需要运行 `cd ios && pod install` 重新安装 Pod 依赖。
3. 清理所有缓存可能需要较长时间，特别是在重新安装依赖时。
4. Docker 缓存清理可能会影响其他项目的容器和镜像，请谨慎使用。 