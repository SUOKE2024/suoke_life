# 索克生活端到端测试指南

## 概述

本文档介绍索克生活（Suoke Life）项目的端到端测试框架和使用方法。端到端测试确保整个应用程序从用户界面到后端服务的完整功能正常工作。

## 测试架构

### 测试分类

1. **用户旅程测试** (`user-journey.test.tsx`)
   - 应用启动和导航
   - 核心功能访问
   - 用户交互流程
   - 性能基准测试

2. **智能体协作测试** (`agent-collaboration.test.tsx`)
   - 四大智能体功能验证
   - 智能体间协作流程
   - 服务异常处理
   - 安全性验证

3. **性能压力测试** (`performance-stress.test.tsx`)
   - 应用性能基准
   - 并发操作测试
   - 内存使用监控
   - 网络性能测试

4. **综合端到端测试** (`comprehensive-e2e.test.tsx`)
   - 完整业务流程验证
   - 跨模块集成测试
   - 数据一致性验证

## 快速开始

### 环境要求

- Node.js >= 16
- Python 3.8+
- React Native 开发环境
- 可选：Docker（用于容器化测试）

### 安装依赖

```bash
# 安装Node.js依赖
npm install

# 安装Python依赖
pip3 install -r requirements.txt

# 安装端到端测试专用依赖
npm install --save-dev jest-html-reporters jest-junit @testing-library/jest-native
```

### 运行测试

#### 运行所有端到端测试
```bash
npm run test:e2e:all
```

#### 运行特定类型的测试
```bash
# 用户旅程测试
npm run test:e2e:user-journey

# 智能体协作测试
npm run test:e2e:agent-collaboration

# 性能压力测试
npm run test:e2e:performance

# 综合测试
npm run test:e2e:comprehensive
```

#### 使用脚本运行
```bash
# 运行所有测试
./scripts/run-e2e-tests.sh all

# 运行特定测试
./scripts/run-e2e-tests.sh user-journey
./scripts/run-e2e-tests.sh agent-collaboration
./scripts/run-e2e-tests.sh performance
./scripts/run-e2e-tests.sh comprehensive
```

## 测试配置

### Jest配置 (`jest.e2e.config.js`)

```javascript
module.exports = {
  preset: 'react-native',
  testEnvironment: 'node',
  testMatch: ['<rootDir>/src/__tests__/e2e/**/*.test.{js,jsx,ts,tsx}'],
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup/e2e-setup.ts'],
  testTimeout: 300000, // 5分钟
  // ... 其他配置
};
```

### 环境设置 (`src/__tests__/setup/e2e-setup.ts`)

- React Native模块模拟
- 权限和设备功能模拟
- 网络和存储模拟
- Redux状态模拟
- 全局错误处理

## 测试用例详解

### 用户旅程测试

```typescript
describe('用户旅程端到端测试', () => {
  test('应用启动和基础导航', async () => {
    // 测试应用启动
    // 验证导航功能
    // 检查性能指标
  });

  test('四诊功能访问', async () => {
    // 测试中医四诊功能
    // 验证用户交互
    // 检查数据流转
  });
});
```

### 智能体协作测试

```typescript
describe('智能体协作端到端测试', () => {
  test('小艾智能体功能', async () => {
    // 测试对话交互
    // 验证四诊协调
    // 检查响应时间
  });

  test('智能体协作流程', async () => {
    // 测试多智能体协作
    // 验证数据同步
    // 检查错误处理
  });
});
```

### 性能压力测试

```typescript
describe('性能压力端到端测试', () => {
  test('应用启动性能', async () => {
    // 测试启动时间
    // 监控内存使用
    // 验证性能基准
  });

  test('并发操作压力测试', async () => {
    // 模拟并发用户
    // 测试系统稳定性
    // 监控资源使用
  });
});
```

## 测试报告

### 报告生成

测试完成后，会在 `reports/e2e/` 目录下生成以下报告：

- `e2e-test-report.html` - HTML格式的详细测试报告
- `e2e-test-results.xml` - JUnit格式的测试结果
- `coverage/` - 代码覆盖率报告

### 查看报告

```bash
# 在浏览器中打开HTML报告
open reports/e2e/e2e-test-report.html

# 查看覆盖率报告
open reports/e2e/coverage/lcov-report/index.html
```

## 最佳实践

### 测试编写原则

1. **独立性**：每个测试用例应该独立运行
2. **可重复性**：测试结果应该一致和可重复
3. **清晰性**：测试意图应该清晰明确
4. **完整性**：覆盖关键业务流程

### 性能考虑

1. **超时设置**：合理设置测试超时时间
2. **资源清理**：及时清理测试资源
3. **并发控制**：控制并发测试数量
4. **缓存管理**：合理使用测试缓存

### 错误处理

1. **异常捕获**：捕获和记录测试异常
2. **重试机制**：对不稳定的测试实现重试
3. **日志记录**：详细记录测试过程
4. **环境清理**：确保测试环境清理

## 故障排除

### 常见问题

1. **测试超时**
   ```bash
   # 增加超时时间
   jest --testTimeout=600000
   ```

2. **模拟失败**
   ```bash
   # 清理Jest缓存
   npm run clean
   jest --clearCache
   ```

3. **服务连接失败**
   ```bash
   # 检查服务状态
   npm run services:status
   
   # 重启服务
   npm run services:restart
   ```

### 调试技巧

1. **详细日志**
   ```bash
   # 启用详细日志
   DEBUG=* npm run test:e2e
   ```

2. **单独运行测试**
   ```bash
   # 运行单个测试文件
   npx jest src/__tests__/e2e/user-journey.test.tsx --verbose
   ```

3. **检查模拟状态**
   ```typescript
   // 在测试中添加调试信息
   console.log('Mock状态:', jest.getMockImplementation());
   ```

## 持续集成

### CI/CD集成

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm install
      - name: Run E2E tests
        run: npm run test:e2e:all
      - name: Upload test reports
        uses: actions/upload-artifact@v2
        with:
          name: e2e-test-reports
          path: reports/e2e/
```

### 质量门禁

- 测试通过率 >= 95%
- 代码覆盖率 >= 60%
- 性能基准达标
- 无严重安全问题

## 扩展和定制

### 添加新测试

1. 在 `src/__tests__/e2e/` 目录下创建新的测试文件
2. 遵循现有的测试模式和命名约定
3. 更新测试脚本和配置
4. 添加相应的文档

### 自定义配置

1. 修改 `jest.e2e.config.js` 配置
2. 更新 `src/__tests__/setup/e2e-setup.ts` 设置
3. 调整 `scripts/run-e2e-tests.sh` 脚本
4. 配置CI/CD流水线

## 联系和支持

如有问题或建议，请联系：
- 邮箱：song.xu@icloud.com
- 项目仓库：https://github.com/SUOKE2024/suoke_life
- 文档：docs/testing/

---

*本文档持续更新，最后更新时间：2024年12月* 