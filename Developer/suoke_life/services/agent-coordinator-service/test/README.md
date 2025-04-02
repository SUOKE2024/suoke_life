# 代理协调服务测试指南

本文档提供了索克生活APP代理协调服务的测试相关信息和指南。

## 测试策略

我们采用了多层次的测试策略，确保系统的可靠性和稳定性：

1. **单元测试**：测试独立组件的功能，模拟其依赖项
2. **集成测试**：测试多个组件之间的交互
3. **边缘情况测试**：测试各种异常情况和边界条件
4. **性能测试**：测试系统在负载下的响应时间和资源使用
5. **端到端测试**：模拟真实用户场景的完整流程测试

## 测试目录结构

```
test/
├── ci/                  # CI环境配置
│   └── jest.config.ci.js
├── e2e/                 # 端到端测试
├── integration/         # 集成测试
│   ├── routes/          # 路由集成测试
│   └── test-server.ts   # 测试服务器配置
├── performance/         # 性能测试
├── unit/                # 单元测试
│   ├── controllers/     # 控制器测试
│   ├── middleware/      # 中间件测试
│   ├── models/          # 模型测试
│   ├── services/        # 服务测试
│   └── utils/           # 工具函数测试
└── utils/               # 测试工具函数
    └── mock-response.ts # 响应模拟工具
```

## 运行测试

### 安装依赖

```bash
npm install
```

### 运行所有测试

```bash
npm test
```

### 运行特定类型的测试

```bash
# 单元测试
npm run test:unit

# 集成测试
npm run test:integration

# 性能测试
npm run test:performance

# 端到端测试
npm run test:e2e
```

### 生成测试覆盖率报告

```bash
npm run test:coverage
```

覆盖率报告将生成在 `coverage/` 目录下。

### 在CI环境中运行测试

```bash
npm run test:ci
```

## 测试类型详解

### 单元测试

单元测试关注于测试独立的代码单元（通常是一个函数或类）的功能。我们使用Jest作为测试框架，并模拟依赖项以确保测试的隔离性。

示例：`test/unit/controllers/agent-controller.test.ts`

#### 参数化测试

为了减少重复代码并测试多种参数组合，我们使用参数化测试方法：

```typescript
// 定义测试用例集合
const testCases = [
  { name: '测试1', input: 'a', expected: 'A' },
  { name: '测试2', input: 'b', expected: 'B' }
];

// 为每个测试用例运行测试
testCases.forEach((tc) => {
  it(tc.name, () => {
    expect(function(tc.input)).toBe(tc.expected);
  });
});
```

### 边缘情况测试

边缘情况测试关注于系统在各种异常情况下的行为，包括：

- 网络错误处理
- 服务器响应错误处理
- 认证和权限错误处理
- 异常数据处理

示例：`test/unit/controllers/edge-cases.test.ts`

### 集成测试

集成测试验证多个组件一起工作时的行为。我们使用supertest库来测试HTTP请求和响应。

示例：`test/integration/routes/coordination-routes.test.ts`

### 性能测试

性能测试验证系统在负载下的响应时间和资源使用情况。

示例：`test/performance/performance-tests.test.ts`

## 测试最佳实践

### 编写可维护的测试

1. 遵循AAA（Arrange-Act-Assert）模式
2. 为每个测试提供清晰的描述
3. 使用辅助函数减少重复代码
4. 每个测试只测试一个概念

### 模拟和存根

1. 只模拟直接依赖
2. 使用Jest的模拟功能：`jest.mock()`, `jest.spyOn()`
3. 为每个测试提供明确的模拟返回值

### 提高测试质量

1. 定期审查测试代码
2. 保持测试独立且可重复
3. 避免测试实现细节，专注于测试行为
4. 使用代码覆盖率报告识别未测试的代码路径

## CI/CD整合

我们使用GitHub Actions作为CI/CD平台:

1. 每次推送到main和develop分支时自动运行测试
2. 使用SonarCloud分析代码质量
3. 在测试和代码质量检查通过后，自动部署到测试环境

详见 `.github/workflows/test.yml`

## 疑难解答

### 常见问题

1. **测试超时**：检查是否有异步操作未正确处理
2. **模拟失败**：确保正确设置了模拟的返回值和实现
3. **路径问题**：确保测试文件和导入的模块使用正确的路径

### 获取帮助

如有测试相关问题，请联系索克生活开发团队或提交GitHub Issue。 