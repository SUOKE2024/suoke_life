# 索克生活项目开发指南

本指南提供了索克生活项目的开发环境配置、架构概述、开发流程和最佳实践等信息，帮助开发者快速上手项目开发。

## 目录

- [开发环境设置](#开发环境设置)
- [架构概述](#架构概述)
- [开发工作流](#开发工作流)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [常见问题(FAQ)](#常见问题)

## 开发环境设置

### 系统要求

- **操作系统**: macOS 10.15+, Windows 10+, Linux
- **IDE**: 推荐使用Visual Studio Code
- **Node.js**: 16.x或更高版本
- **npm**: 8.x或更高版本
- **Git**: 2.25.0或更高版本
- **Docker**: 最新稳定版
- **Docker Compose**: 最新稳定版

### 安装步骤

#### 1. Node.js和npm

**macOS**:
```bash
# 使用Homebrew
brew install node

# 或使用nvm(推荐)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 16
nvm use 16
```

**Windows**:
- 下载并安装Node.js: https://nodejs.org/
- 或使用nvm-windows: https://github.com/coreybutler/nvm-windows

**Linux**:
```bash
# 使用nvm(推荐)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 16
nvm use 16
```

#### 2. React Native CLI

```bash
npm install -g react-native-cli
```

#### 3. Xcode (仅macOS, 用于iOS开发)

从Mac App Store安装Xcode 14或更高版本，然后安装iOS模拟器和命令行工具:

```bash
xcode-select --install
```

#### 4. Android Studio (用于Android开发)

1. 下载并安装Android Studio: https://developer.android.com/studio
2. 通过SDK Manager安装以下组件:
   - Android SDK Platform 30 (或更高版本)
   - Android SDK Build-Tools
   - Android Emulator
   - Android SDK Platform-Tools

#### 5. Docker和Docker Compose

**macOS**:
- 下载Docker Desktop: https://www.docker.com/products/docker-desktop

**Windows**:
- 下载Docker Desktop: https://www.docker.com/products/docker-desktop

**Linux**:
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 克隆和设置项目

1. **克隆仓库**:

```bash
git clone git@github.com:SUOKE2024/suoke_life.git
cd suoke_life
```

2. **安装依赖**:

```bash
npm install
```

3. **设置环境变量**:

```bash
cp .env.example .env.development
# 编辑.env.development文件，填入必要的环境变量
```

### 启动开发环境

#### 启动前端服务

```bash
# iOS
npx react-native run-ios

# Android
npx react-native run-android
```

#### 启动后端服务

```bash
cd services
docker-compose -f docker-compose.dev.yml up -d
```

## 架构概述

索克生活项目采用微服务架构和React Native前端，主要包括以下部分:

### 前端架构

索克生活前端采用React Native框架，主要技术栈包括:

- **React Native**: 跨平台移动应用框架
- **TypeScript**: 静态类型检查
- **Redux Toolkit**: 状态管理
- **React Navigation**: 导航管理
- **React Native Paper**: UI组件库
- **SQLite**: 本地数据存储
- **Jest & React Native Testing Library**: 测试工具

前端架构采用特性驱动的模块化结构，主要目录包括:

- `/src/api`: API服务接口
- `/src/components`: 可复用UI组件
- `/src/features`: 功能模块，按业务域组织
- `/src/navigation`: 导航配置
- `/src/screens`: 页面组件
- `/src/services`: 业务逻辑服务
- `/src/store`: Redux状态管理
- `/src/utils`: 工具函数

### 后端架构

索克生活后端采用微服务架构，主要包括:

- **API网关**: 统一接入层，处理路由和认证
- **业务微服务**: 按领域划分的微服务，如用户服务、诊断服务等
- **AI智能体服务**: 四大智能体的后端服务
- **数据存储服务**: 包括关系型数据库、NoSQL数据库和向量数据库
- **消息队列**: 用于服务间异步通信
- **事件总线**: 处理领域事件
- **监控与日志**: 收集和分析运行数据

各微服务采用Kubernetes进行容器编排，使用Docker进行容器化部署。

### 数据流

索克生活项目的数据流遵循以下原则:

1. **前端**: 
   - 用户交互触发Action
   - Reducer处理State更新
   - 组件通过Selector获取State

2. **前后端交互**:
   - API服务负责与后端通信
   - 使用RESTful API和WebSocket进行通信
   - 支持JWT认证

3. **后端**:
   - API网关接收请求并路由到相应微服务
   - 微服务处理业务逻辑
   - 领域事件通过事件总线传播
   - 服务间通过gRPC或消息队列通信

## 开发工作流

### 分支策略

项目使用GitFlow工作流，主要分支包括:

- `main`: 生产环境代码，稳定版本
- `develop`: 开发环境代码，最新特性
- `feature/*`: 特性分支，用于开发新功能
- `fix/*`: 修复分支，用于修复Bug
- `release/*`: 发布分支，用于准备发布新版本

### 开发流程

1. **特性开发**:
   - 从`develop`分支创建特性分支
   - 完成开发和测试
   - 提交Pull Request到`develop`分支
   - 代码审查通过后合并

2. **缺陷修复**:
   - 从`develop`分支创建修复分支
   - 完成修复和测试
   - 提交Pull Request到`develop`分支
   - 代码审查通过后合并

3. **版本发布**:
   - 从`develop`分支创建发布分支
   - 完成最终测试和文档更新
   - 更新版本号和变更日志
   - 合并到`main`分支并打标签
   - 同时合并回`develop`分支

### 版本控制

项目使用语义化版本控制(SemVer)，版本号格式为`X.Y.Z`:

- `X`: 主版本号，不兼容的API变更
- `Y`: 次版本号，向后兼容的功能新增
- `Z`: 修订号，向后兼容的问题修复

### 提交规范

遵循约定式提交(Conventional Commits)规范，提交消息格式为:

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

详细规范请参考[贡献指南](CONTRIBUTING.md)。

## 代码规范

### JavaScript/TypeScript规范

- 使用ESLint和Prettier进行代码质量控制和格式化
- 项目根目录下的`.eslintrc.js`和`.prettierrc.js`定义了具体规则
- 使用TypeScript进行静态类型检查
- 使用ES6+语法特性

主要规则:

- 使用2个空格进行缩进
- 行末不留分号
- 字符串使用单引号
- 每行最大长度为100个字符
- 函数和类必须有JSDoc注释

### React/React Native规范

- 使用函数组件和React Hooks，避免使用类组件
- 组件文件采用PascalCase命名，如`ProfileScreen.tsx`
- 非组件文件采用camelCase命名，如`apiService.ts`
- 样式使用StyleSheet API定义
- 避免内联样式
- 组件props必须有TypeScript类型定义

### 命名规范

- **组件命名**: PascalCase，如`UserProfile`
- **函数命名**: camelCase，如`getUserData`
- **变量命名**: camelCase，如`userData`
- **常量命名**: 全大写下划线分隔，如`API_URL`
- **文件命名**:
  - 组件文件: PascalCase，如`UserProfile.tsx`
  - 非组件文件: camelCase，如`apiService.ts`
  - 测试文件: 原文件名加`.test`，如`UserProfile.test.tsx`
- **目录命名**: camelCase，如`userAuth`

## 测试指南

### 测试策略

项目采用多层次测试策略，包括:

- **单元测试**: 测试独立的函数和组件
- **集成测试**: 测试组件间的交互
- **端到端测试**: 测试完整的用户流程

### 单元测试

使用Jest和React Native Testing Library进行单元测试。

示例:

```typescript
// src/components/Button.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import Button from './Button';

describe('Button', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Button title="Press me" onPress={() => {}} />);
    expect(getByText('Press me')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPress = jest.fn();
    const { getByText } = render(<Button title="Press me" onPress={onPress} />);
    fireEvent.press(getByText('Press me'));
    expect(onPress).toHaveBeenCalledTimes(1);
  });
});
```

### 集成测试

使用Jest和React Native Testing Library进行集成测试，测试组件间的交互。

### 端到端测试

使用Detox进行端到端测试，测试完整的用户流程。

## 调试技巧

### React Native调试

1. **Dev Menu**:
   - iOS: 摇动设备或按`Cmd + D`(模拟器)
   - Android: 摇动设备或按`Cmd + M`(模拟器)

2. **Chrome DevTools**:
   - 通过Dev Menu打开"Debug JS Remotely"
   - 使用Chrome DevTools调试JavaScript

3. **React Native Debugger**:
   - 一个独立的调试工具，集成了Redux DevTools和React DevTools
   - 安装: `brew install --cask react-native-debugger`

4. **Flipper**:
   - Facebook官方调试工具，支持布局检查、网络监控等
   - 下载: https://fbflipper.com/

### 常用调试命令

```bash
# 清除缓存并重启
npx react-native start --reset-cache

# 运行特定测试
npm test -- Button.test.tsx

# 调试测试
npm test -- --debug

# 查看测试覆盖率
npm test -- --coverage
```

### 日志和异常处理

- 使用`console.log`、`console.warn`和`console.error`进行日志输出
- 使用`try/catch`捕获异常
- 对于异步代码，使用`try/catch`结合`async/await`

```typescript
try {
  const result = await apiService.fetchData();
  // 处理结果
} catch (error) {
  console.error('Failed to fetch data:', error);
  // 显示错误提示
}
```

## 常见问题

### 项目启动问题

1. **问题**: `The engine "node" is incompatible with this module`
   **解决方案**: 使用`nvm`安装并切换到匹配的Node.js版本

2. **问题**: iOS构建失败，提示`Pod not found`
   **解决方案**:
   ```bash
   cd ios
   pod install --repo-update
   ```

3. **问题**: Android构建失败，提示`SDK location not found`
   **解决方案**: 创建`android/local.properties`文件，添加SDK路径
   ```
   sdk.dir=/path/to/your/android/sdk
   ```

### 性能优化问题

1. **问题**: 列表滚动卡顿
   **解决方案**:
   - 使用`FlatList`或`SectionList`替代`ScrollView`
   - 实现`getItemLayout`提高性能
   - 使用`PureComponent`或`React.memo`减少不必要的重渲染

2. **问题**: 图片加载慢或内存占用高
   **解决方案**:
   - 使用`FastImage`库替代原生`Image`组件
   - 使用适当的图片尺寸和格式
   - 实现图片懒加载

### 常见错误和调试技巧

1. **问题**: `undefined is not an object`
   **解决方案**: 检查对象是否存在再访问属性，使用可选链操作符`?.`

2. **问题**: 组件没有渲染或渲染不正确
   **解决方案**:
   - 检查组件props
   - 检查条件渲染逻辑
   - 使用React DevTools检查组件树

3. **问题**: 网络请求失败
   **解决方案**:
   - 检查网络连接
   - 检查API端点URL
   - 检查请求头和参数
   - 使用网络调试工具检查请求和响应

4. **问题**: Redux状态更新但组件没有重新渲染
   **解决方案**:
   - 检查组件是否正确连接到Redux store
   - 检查selector是否正确提取状态
   - 检查Redux action是否正确分发和处理

---

如有任何问题或需要进一步的帮助，请参考[项目文档](../README.md)或联系开发团队。
