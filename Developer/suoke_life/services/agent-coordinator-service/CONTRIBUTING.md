# 索克生活APP 代理协调器服务贡献指南

欢迎为索克生活APP代理协调器服务贡献代码！本文档将指导您如何为本项目做出贡献，包括代码规范、测试要求、提交流程等。

## 目录

- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [测试规范](#测试规范)
- [提交流程](#提交流程)
- [问题报告](#问题报告)
- [分支管理](#分支管理)

## 开发环境设置

1. 克隆代码库：
   ```bash
   git clone <repository-url>
   cd services/agent-coordinator-service
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 本地开发：
   ```bash
   npm run dev
   ```

4. 构建项目：
   ```bash
   npm run build
   ```

## 代码规范

本项目使用TypeScript编写，并遵循以下代码规范：

1. **类型安全**：始终使用强类型定义，避免使用`any`。
2. **错误处理**：使用自定义错误类，并确保所有异常都被恰当处理。
3. **异步代码**：使用`async/await`处理异步操作，避免直接使用回调函数。
4. **命名规范**：
   - 文件名：使用kebab-case（如`file-name.ts`）
   - 类名：使用PascalCase（如`ClassName`）
   - 方法和变量：使用camelCase（如`functionName`）
   - 常量：使用UPPER_SNAKE_CASE（如`MAX_RETRY_COUNT`）
5. **注释**：为所有公共API添加JSDoc注释。
6. **模块导出**：使用命名导出而非默认导出。
7. **依赖管理**：避免引入过多第三方库，合理评估每个依赖。

## 测试规范

本项目使用Jest进行测试，并要求所有代码都有足够的测试覆盖率。

### 测试目录结构

```
test/
├── unit/                  # 单元测试
│   ├── services/          # 服务测试
│   ├── controllers/       # 控制器测试
│   ├── middlewares/       # 中间件测试
│   └── utils/             # 工具函数测试
├── integration/           # 集成测试
│   └── routes/            # 路由集成测试
├── mock-routes.ts         # 测试路由模拟工具
└── jest.setup.js          # Jest设置文件
```

### 测试要求

1. **覆盖率要求**：
   - 所有服务(services)、控制器(controllers)和工具(utils)必须达到至少80%的测试覆盖率
   - 总体代码覆盖率必须至少达到70%

2. **单元测试**：
   - 每个文件必须有对应的单元测试
   - 使用模拟(mock)隔离依赖
   - 测试文件命名为`[原文件名].test.ts`

3. **集成测试**：
   - 为每个API路由创建集成测试
   - 测试HTTP状态码、响应格式和错误处理
   - 模拟外部服务依赖

4. **运行测试**：
   ```bash
   # 运行所有测试
   npm test
   
   # 运行单个测试文件
   npm test -- test/unit/services/session-service.test.ts
   
   # 运行测试并生成覆盖率报告
   npm run test:coverage
   ```

5. **写测试技巧**：
   - 每个测试函数只测试一个功能点
   - 使用描述性的测试名称（如`it('should return 404 when user not found')`)
   - 确保测试之间相互独立，不要有状态依赖
   - 避免在测试中使用随机值或时间敏感值
   - 使用`beforeEach`和`afterEach`设置和清理测试环境

## 提交流程

1. **创建分支**：从`develop`分支创建功能分支或修复分支
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. **提交规范**：使用Angular风格的提交消息
   ```
   <type>(<scope>): <subject>
   
   <body>
   
   <footer>
   ```
   
   Type可以是：
   - `feat`：新功能
   - `fix`：Bug修复
   - `docs`：文档变更
   - `style`：代码格式变更
   - `refactor`：重构代码
   - `test`：添加缺失的测试
   - `chore`：构建过程或辅助工具变更

3. **代码审查**：创建拉取请求(Pull Request)到`develop`分支
   - 描述此PR的目的和变更
   - 确保所有测试通过
   - 确保代码覆盖率达到要求
   - 请求至少一位团队成员进行代码审查

4. **合并**：通过代码审查后才能合并到`develop`分支

## 问题报告

如果您发现bug或有功能建议，请创建Issue并提供以下信息：

- 详细的问题描述
- 复现步骤
- 预期结果和实际结果
- 环境信息（操作系统、Node.js版本等）
- 可能的解决方案（如果有）

## 分支管理

- `main`：生产环境分支，只接受来自`develop`的合并
- `develop`：开发分支，所有功能和修复都合并到这里
- `feature/*`：新功能分支，从`develop`创建
- `fix/*`：Bug修复分支，从`develop`创建
- `release/*`：发布准备分支，从`develop`创建

感谢您对索克生活APP的贡献！ 