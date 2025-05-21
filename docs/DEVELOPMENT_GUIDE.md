# 索克生活APP开发指南

本文档提供索克生活APP项目的开发指南，包括环境配置、开发流程、测试流程和发布流程等内容。

## 目录

- [开发环境配置](#开发环境配置)
- [项目架构](#项目架构)
- [开发流程](#开发流程)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [发布流程](#发布流程)
- [常见问题](#常见问题)

## 开发环境配置

### 必要工具

- Node.js 16.x 或更高版本
- npm 8.x 或更高版本
- React Native CLI
- Android Studio (Android开发)
- Xcode (iOS开发)
- Visual Studio Code 或 WebStorm
- Git

### 环境安装步骤

1. **安装Node.js和npm**

   ```bash
   # macOS (使用Homebrew)
   brew install node

   # Windows (使用Chocolatey)
   choco install nodejs
   ```

2. **安装React Native CLI**

   ```bash
   npm install -g react-native-cli
   ```

3. **设置Android开发环境**

   - 安装Android Studio
   - 安装Android SDK (推荐API级别33)
   - 配置环境变量:
     - ANDROID_HOME: Android SDK路径
     - PATH: 添加platform-tools和tools目录

4. **设置iOS开发环境 (仅macOS)**

   - 安装Xcode (通过App Store)
   - 安装CocoaPods: `sudo gem install cocoapods`

5. **克隆项目**

   ```bash
   git clone https://github.com/SUOKE2024/suoke_life.git
   cd suoke_life
   ```

6. **安装项目依赖**

   ```bash
   npm install
   ```

7. **配置环境变量**

   复制`.env.example`文件到`.env.development`，并根据本地开发环境修改配置项。

### IDE配置

推荐使用Visual Studio Code，安装以下插件:

- ESLint
- Prettier - Code formatter
- React Native Tools
- GitLens
- Todo Tree
- Jest

VSCode配置建议:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "javascript.updateImportsOnFileMove.enabled": "always",
  "typescript.updateImportsOnFileMove.enabled": "always"
}
```

## 项目架构

### 前端架构

索克生活APP采用React Native开发，以下是主要技术栈:

- **UI框架**: React Native 0.73+
- **状态管理**: Redux Toolkit
- **路由导航**: React Navigation 6
- **本地存储**: SQLite (禁止使用Hive)
- **API通信**: Axios
- **样式组件**: React Native Paper
- **动画效果**: React Native Reanimated

### 目录结构

```
suoke_life/
├── android/                     # Android原生代码
├── ios/                         # iOS原生代码
├── src/                         # 源代码目录
│   ├── api/                     # API服务
│   │   ├── agents/              # 智能代理API
│   │   ├── medical/             # 医疗服务API  
│   │   └── user/                # 用户服务API
│   ├── assets/                  # 静态资源
│   ├── components/              # 共享UI组件
│   ├── config/                  # 配置文件
│   ├── context/                 # React上下文
│   ├── features/                # 功能模块
│   ├── hooks/                   # 自定义钩子
│   ├── navigation/              # 导航管理
│   ├── screens/                 # 页面组件
│   ├── services/                # 业务服务
│   ├── store/                   # Redux状态管理
│   ├── types/                   # TypeScript类型定义
│   ├── utils/                   # 工具函数
│   └── App.tsx                  # 应用程序入口
├── .env.development             # 开发环境变量
├── .env.production              # 生产环境变量
└── ...
```

### 后端架构

后端采用微服务架构，主要技术栈:

- **API网关**: Kong
- **服务框架**: FastAPI/gRPC
- **数据库**: PostgreSQL, Redis, MongoDB
- **消息队列**: Kafka
- **容器化**: Docker, Kubernetes

后端微服务结构:

```
services/
├── api-gateway/                # API网关
├── auth-service/               # 认证服务
├── user-service/               # 用户服务
├── diagnostic-services/        # 诊断微服务组
│   ├── look-service/           # 望诊服务
│   ├── listen-service/         # 闻诊服务
│   ├── inquiry-service/        # 问诊服务
│   └── palpation-service/      # 切诊服务
├── agent-services/             # 智能代理微服务组
│   ├── xiaoai-service/         # 小艾服务
│   ├── xiaoke-service/         # 小克服务
│   ├── laoke-service/          # 老克服务
│   └── soer-service/           # 索儿服务
└── ...
```

## 开发流程

### 分支管理策略

项目采用GitFlow工作流:

- `main`: 生产环境分支，稳定版本
- `develop`: 开发环境分支，最新开发版本
- `feature/xxx`: 功能分支，从develop分支创建
- `bugfix/xxx`: 缺陷修复分支，从develop分支创建
- `release/x.x.x`: 发布分支，从develop分支创建
- `hotfix/xxx`: 紧急修复分支，从main分支创建

### 开发步骤

1. **创建功能分支**

   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. **开发功能**

   遵循项目规范进行开发，确保代码符合ESLint和TypeScript类型检查。

3. **单元测试**

   为新功能编写单元测试，确保测试覆盖率达到要求。

4. **提交代码**

   ```bash
   git add .
   git commit -m "feat(module): add new feature"
   ```

   提交信息必须遵循Angular Commit Message格式。

5. **推送代码**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request**

   在GitHub上创建PR，指定develop分支为目标分支。

7. **代码审查**

   至少一名团队成员审查代码，确保代码质量。

8. **合并代码**

   通过CI/CD检查和代码审查后，合并到develop分支。

### 版本管理

项目使用语义化版本(Semantic Versioning)，格式为`X.Y.Z`:

- `X`: 主版本号，不兼容的API修改
- `Y`: 次版本号，向后兼容的功能性新增
- `Z`: 修订号，向后兼容的问题修正

## 测试指南

### 单元测试

使用Jest进行单元测试:

```bash
# 运行所有测试
npm test

# 运行特定测试文件
npm test -- src/components/MyComponent.test.tsx

# 生成测试覆盖率报告
npm test -- --coverage
```

单元测试文件应与被测试的源文件放在同一目录下，并使用`.test.tsx`或`.spec.tsx`后缀。

### 组件测试

使用React Native Testing Library测试组件:

```jsx
import { render, fireEvent } from '@testing-library/react-native';
import MyComponent from './MyComponent';

test('renders correctly', () => {
  const { getByText } = render(<MyComponent />);
  expect(getByText('Hello World')).toBeTruthy();
});
```

### 端到端测试

使用Detox进行端到端测试:

```bash
# 构建测试应用
detox build --configuration ios.sim.debug

# 运行测试
detox test --configuration ios.sim.debug
```

## 调试技巧

### React Native调试

- 使用React DevTools进行组件调试
- 使用Redux DevTools进行状态调试
- 使用Chrome DevTools进行JavaScript调试

启用开发者菜单:
- iOS: 摇动设备或在模拟器中按`Cmd+D`
- Android: 摇动设备或在模拟器中按`Cmd+M`(macOS)或`Ctrl+M`(Windows)

### 日志调试

- 使用`console.log`, `console.warn`, `console.error`进行简单调试
- 使用`react-native-logs`库进行高级日志记录

### 性能调试

- 使用React Native的Performance Monitor
- 使用Flipper进行性能分析
- 注意监控渲染性能，避免不必要的重渲染

## 性能优化

### 渲染优化

- 使用`React.memo`避免不必要的组件重渲染
- 使用`useMemo`和`useCallback`缓存计算结果和回调函数
- 使用`PureComponent`或实现`shouldComponentUpdate`优化类组件

### 列表优化

- 对于长列表，使用`FlatList`或`SectionList`
- 实现`getItemLayout`提高渲染性能
- 合理设置`windowSize`和`maxToRenderPerBatch`
- 使用`keyExtractor`提供稳定的key

### 资源优化

- 图片资源使用适当的分辨率和格式(如WebP)
- 懒加载非关键资源
- 使用适当的图片缓存策略

### 网络优化

- 实现请求缓存
- 使用批量请求减少网络往返
- 压缩API响应
- 实现请求超时和重试策略

## 发布流程

### 版本发布流程

1. **创建发布分支**

   ```bash
   git checkout develop
   git pull
   git checkout -b release/x.y.z
   ```

2. **版本号更新**

   更新`package.json`中的版本号和应用版本号(Android的`versionCode`和iOS的`CFBundleVersion`)。

3. **执行测试**

   确保所有测试通过，包括单元测试、组件测试和端到端测试。

4. **构建发布版本**

   ```bash
   # Android
   cd android && ./gradlew assembleRelease

   # iOS
   cd ios && pod install
   xcodebuild -workspace SuokeLife.xcworkspace -scheme SuokeLife -configuration Release
   ```

5. **提交发布分支**

   ```bash
   git add .
   git commit -m "chore(release): bump version to x.y.z"
   git push origin release/x.y.z
   ```

6. **合并到主分支**

   创建PR将release分支合并到main分支和develop分支。

7. **创建标签**

   ```bash
   git checkout main
   git pull
   git tag -a v.x.y.z -m "Version x.y.z"
   git push origin v.x.y.z
   ```

8. **发布到应用商店**

   - Android: 上传APK到Google Play Console
   - iOS: 使用App Store Connect上传应用

### 持续集成/持续部署

项目使用GitHub Actions进行CI/CD:

- 每次推送到feature分支，运行lint和测试
- 每次推送到develop分支，运行完整测试并构建开发版本
- 每次推送到release分支，运行完整测试并构建预发布版本
- 每次推送到main分支或创建tag，构建并发布生产版本

## 常见问题

### 环境问题

**Q: Android构建失败，提示"SDK location not found"**

A: 确保已正确设置ANDROID_HOME环境变量，指向Android SDK目录。

**Q: iOS构建失败，提示"CocoaPods not installed"**

A: 运行`sudo gem install cocoapods`安装CocoaPods，然后在iOS目录下运行`pod install`。

**Q: Metro服务启动失败**

A: 尝试清除Metro缓存: `npx react-native start --reset-cache`

### 开发问题

**Q: 如何添加新的环境变量?**

A: 在`.env.development`和`.env.production`文件中添加，然后在`config/env.ts`中引用。所有环境变量必须以`REACT_APP_`开头。

**Q: 如何定义新的API端点?**

A: 在`api`目录下创建新的服务文件，使用axios实例进行API调用。

**Q: 如何添加新的导航路由?**

A: 在`navigation`目录下修改导航配置，添加新的屏幕组件。

### 调试问题

**Q: 无法连接到开发服务器**

A: 确保设备和电脑在同一网络，检查防火墙设置，尝试使用explicit host: `npx react-native start --host <your-ip>`

**Q: Redbox错误: "Invariant Violation: Module not registered in Metro"**

A: 尝试重启Metro服务器，使用`--reset-cache`选项。

**Q: 无法使用Chrome调试器**

A: 确保已启用开发者菜单中的"Debug JS Remotely"选项，并且没有网络限制阻止连接到localhost:8081。
