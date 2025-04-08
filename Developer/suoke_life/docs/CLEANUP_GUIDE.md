# 索克生活APP项目清理指南

## 项目清理概述

索克生活APP项目是一个复杂的Flutter项目，包含了多个服务组件和大量资源文件。为了保持项目的整洁性和可维护性，我们需要定期进行项目清理，避免不必要的文件积累导致项目膨胀。

## 清理脚本使用说明

我们提供了一个自动化清理脚本 `scripts/clean_project.sh`，可以帮助您快速清理项目中的临时文件、构建文件和缓存文件。

### 使用方法

```bash
# 确保脚本有执行权限
chmod +x scripts/clean_project.sh

# 运行清理脚本
./scripts/clean_project.sh
```

### 脚本功能说明

该脚本会清理以下内容：

1. Flutter编译和缓存文件（build目录、.dart_tool目录等）
2. 日志文件（*.log）
3. 临时文件（*.tmp, *.temp, .DS_Store等）
4. iOS构建文件（DerivedData, Debug/Release构建目录）
5. Android构建文件（build目录, .gradle目录, *.apk, *.aab文件）
6. macOS构建文件（build目录, DerivedData）
7. Windows和Linux构建文件（build目录）
8. IDE缓存文件（.vscode, .cursor等目录中的日志文件）

**注意**：为了安全起见，脚本默认不会清理node_modules目录。如果您确定需要清理node_modules，请编辑脚本，取消相关命令的注释。

## 项目清理最佳实践

为了保持项目的整洁和高效，建议遵循以下最佳实践：

### 1. 定期清理

- 每周至少进行一次项目清理
- 在大型合并前进行清理
- 在遇到IDE或编译性能问题时进行清理

### 2. .gitignore配置

确保项目的.gitignore文件正确配置，避免将以下文件提交到代码库：

- 编译产物（build/目录, .dart_tool/目录）
- 依赖管理文件（node_modules/, .pub-cache/）
- IDE配置文件（.idea/, .vscode/）
- 平台特定的构建文件（ios/Pods/, android/.gradle/）
- 临时文件和日志文件（*.log, *.tmp）
- 环境配置文件（.env, *.env.local）

### 3. 依赖管理

- 定期更新和清理过时的依赖
- 使用`flutter pub cache clean`清理Flutter包缓存
- 使用`npm prune`清理不必要的npm包
- 在package.json和pubspec.yaml中指定精确的依赖版本

### 4. 资源文件管理

- 压缩图片和多媒体文件后再添加到项目
- 删除未使用的资源文件
- 考虑使用CDN或远程存储大型资源文件

### 5. 日志管理

- 在生产环境禁用详细日志
- 配置日志轮转（log rotation）机制
- 定期清理旧的日志文件

### 6. 大型二进制文件管理

- 使用Git LFS管理大型文件
- 考虑将大型二进制文件（如ML模型）托管在单独的存储库
- 对大型文件进行版本控制，避免频繁更改

## 特殊清理说明

### iOS Pods清理

如果需要彻底清理iOS的Pods：

```bash
cd ios
pod cache clean --all
rm -rf Pods
rm -rf Podfile.lock
pod install
```

### Android清理

彻底清理Android构建文件：

```bash
cd android
./gradlew clean
rm -rf .gradle
rm -rf build
rm -rf app/build
```

### Flutter全面清理

彻底清理Flutter项目：

```bash
flutter clean
flutter pub cache clean
flutter pub get
```

### Node.js服务清理

对于services目录中的Node.js服务，可以执行：

```bash
cd services/[service-name]
rm -rf node_modules
npm ci  # 比npm install更适合CI环境，会严格按照package-lock.json重新安装
```

## 项目结构优化建议

为了长期保持项目的整洁性，建议按照以下结构组织项目：

```
suoke_life/
├── assets/               # 静态资源
│   ├── datasets/         # 数据集（按领域分类）
│   ├── fonts/           # 字体
│   └── images/          # 图片
├── docs/                # 项目文档
├── lib/                 # Flutter代码
│   ├── ai_agents/       # AI代理相关功能
│   ├── core/            # 核心功能
│   ├── data/            # 数据层
│   ├── di/              # 依赖注入
│   ├── domain/          # 领域层
│   └── presentation/    # 表现层
├── scripts/             # 工具脚本
├── services/            # 后端服务
│   ├── auth-service/    # 认证服务
│   ├── rag-service/     # RAG服务
│   └── ...
├── test/                # 测试代码
└── [平台目录]/           # 各平台特定代码
```

## 常见问题及解决方案

### 项目编译速度变慢

可能的解决方案：
- 运行清理脚本
- 重新启动IDE
- 检查并删除未使用的依赖

### 磁盘空间不足

可能的解决方案：
- 清理iOS Pods目录
- 清理服务中的node_modules
- 检查并删除大型日志文件

### Git操作变慢

可能的解决方案：
- 检查是否有大文件未使用Git LFS
- 考虑Git历史清理（谨慎操作）
- 重新克隆仓库

## 定期维护计划

为确保项目长期健康，建议实施以下定期维护计划：

- **每日**: 开发人员本地清理临时文件
- **每周**: 运行清理脚本
- **每月**: 全面依赖更新和清理
- **每季度**: 代码和资源审查，删除未使用的代码和资源

## 联系与支持

如果您在清理过程中遇到任何问题，或者有改进清理流程的建议，请联系项目管理员或在项目Issue中提出。 