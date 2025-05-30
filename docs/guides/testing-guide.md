# 索克生活测试指南

本文档提供了索克生活项目的完整测试指南，包括单元测试、集成测试、性能测试和端到端测试。

## 目录

- [测试概览](#测试概览)
- [测试环境设置](#测试环境设置)
- [单元测试](#单元测试)
- [集成测试](#集成测试)
- [性能测试](#性能测试)
- [端到端测试](#端到端测试)
- [测试运行](#测试运行)
- [测试覆盖率](#测试覆盖率)
- [持续集成](#持续集成)
- [最佳实践](#最佳实践)

## 测试概览

索克生活项目采用多层次的测试策略：

### 测试金字塔

```
    /\
   /  \     E2E Tests (端到端测试)
  /____\
 /      \   Integration Tests (集成测试)
/________\  Unit Tests (单元测试)
```

- **单元测试 (70%)**：测试单个组件、函数和服务
- **集成测试 (20%)**：测试组件间的交互和API集成
- **端到端测试 (10%)**：测试完整的用户流程

### 测试工具栈

- **测试框架**: Jest
- **React Native 测试**: @testing-library/react-native
- **Mock 工具**: Jest mocks
- **覆盖率工具**: Jest coverage
- **性能测试**: 自定义性能测试工具

## 测试环境设置

### 1. 安装依赖

```bash
npm install
```

### 2. 测试配置

测试配置位于以下文件：
- `jest.config.js` - Jest 主配置
- `src/setupTests.ts` - 测试环境设置
- `src/__tests__/utils/testUtils.tsx` - 测试工具函数

### 3. 环境变量

创建 `.env.test` 文件：

```env
NODE_ENV=test
API_BASE_URL=http://localhost:3000
MOCK_API=true
```

## 单元测试

### 组件测试

组件测试位于 `src/__tests__/components/` 目录下。

#### 示例：Button 组件测试

```typescript
import { render, fireEvent } from '@testing-library/react-native';
import { Button } from '@/components/common/Button';
import { TestWrapper } from '../utils/testUtils';

describe('Button Component', () => {
  it('应该正确渲染按钮', () => {
    const { getByText } = render(
      <TestWrapper>
        <Button title="测试按钮" onPress={() => {}} />
      </TestWrapper>
    );

    expect(getByText('测试按钮')).toBeTruthy();
  });

  it('应该响应点击事件', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <TestWrapper>
        <Button title="点击我" onPress={mockOnPress} />
      </TestWrapper>
    );

    fireEvent.press(getByText('点击我'));
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });
});
```

### 服务测试

服务测试位于 `src/__tests__/services/` 目录下。

#### 示例：API 服务测试

```typescript
import { authService } from '@/services/authService';
import { mockFetch } from '../utils/testUtils';

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该成功登录', async () => {
    const mockResponse = {
      success: true,
      data: { token: 'mock-token', user: { id: '1', name: '测试用户' } }
    };
    
    mockFetch(mockResponse);

    const result = await authService.login('test@example.com', 'password');
    
    expect(result.success).toBe(true);
    expect(result.data.token).toBe('mock-token');
  });
});
```

### 运行单元测试

```bash
# 运行所有单元测试
npm run test:unit

# 运行特定组件测试
npm run test:unit -- --testPathPattern=Button

# 监听模式
npm run test:watch
```

## 集成测试

集成测试位于 `src/__tests__/integration/` 目录下，测试组件间的交互和完整的用户流程。

### 端到端流程测试

```typescript
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { TestWrapper } from '../utils/testUtils';
import { MockApp } from './MockApp';

describe('用户登录流程', () => {
  it('应该完成完整的登录到诊断流程', async () => {
    const { getByTestId, getByText } = render(
      <TestWrapper>
        <MockApp />
      </TestWrapper>
    );

    // 1. 登录
    fireEvent.press(getByTestId('login-button'));
    
    // 2. 验证登录成功
    await waitFor(() => {
      expect(getByTestId('home-screen')).toBeTruthy();
    });

    // 3. 开始诊断
    fireEvent.press(getByTestId('start-diagnosis-button'));
    
    // 4. 验证诊断页面
    await waitFor(() => {
      expect(getByTestId('diagnosis-screen')).toBeTruthy();
    });
  });
});
```

### 运行集成测试

```bash
# 运行集成测试
npm run test:integration

# 运行特定集成测试
npm run test:integration -- --testNamePattern="登录流程"
```

## 性能测试

性能测试位于 `src/__tests__/performance/` 目录下，测试应用的性能指标。

### 性能基准测试

```typescript
import { measurePerformance, measureMemoryUsage } from '../utils/testUtils';

describe('性能基准测试', () => {
  it('组件渲染性能', async () => {
    const renderTime = await measurePerformance(async () => {
      render(<ComplexComponent />);
    });

    expect(renderTime).toBeLessThan(50); // 50ms 内完成
  });

  it('内存使用测试', async () => {
    const memoryUsage = await measureMemoryUsage(async () => {
      // 执行内存密集型操作
    });

    expect(memoryUsage).toBeLessThan(50 * 1024 * 1024); // 50MB 以内
  });
});
```

### 运行性能测试

```bash
# 运行性能测试
npm run test:performance

# 生成性能报告
npm run test:performance -- --verbose
```

## 端到端测试

端到端测试模拟真实用户的完整操作流程。

### E2E 测试示例

```typescript
describe('完整用户体验', () => {
  it('新用户注册到首次诊断', async () => {
    // 1. 用户注册
    // 2. 邮箱验证
    // 3. 完善个人信息
    // 4. 首次五诊检测
    // 5. 查看诊断结果
    // 6. 获取健康建议
  });
});
```

## 测试运行

### 快速测试

```bash
# 运行所有测试
npm test

# 运行完整测试套件
npm run test:all

# 持续集成模式
npm run test:ci
```

### 测试脚本

使用自动化测试脚本：

```bash
# 运行完整测试套件（包括报告生成）
./scripts/test/run-tests.sh
```

该脚本会：
1. 检查代码质量（ESLint、TypeScript）
2. 运行单元测试
3. 运行集成测试
4. 运行性能测试
5. 生成覆盖率报告
6. 生成测试报告

## 测试覆盖率

### 覆盖率目标

- **语句覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 75%
- **函数覆盖率**: ≥ 80%
- **行覆盖率**: ≥ 80%

### 生成覆盖率报告

```bash
# 生成覆盖率报告
npm run test:coverage

# 查看 HTML 报告
open coverage/lcov-report/index.html
```

### 覆盖率配置

在 `jest.config.js` 中配置：

```javascript
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/__tests__/**',
  ],
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

## 持续集成

### GitHub Actions

CI 配置位于 `.github/workflows/ci.yml`：

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test:ci
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 测试阶段

1. **代码质量检查**
   - ESLint 检查
   - TypeScript 类型检查
   - Prettier 格式检查

2. **单元测试**
   - 组件测试
   - 服务测试
   - 工具函数测试

3. **集成测试**
   - API 集成测试
   - 组件集成测试

4. **性能测试**
   - 渲染性能测试
   - 内存使用测试

## 最佳实践

### 1. 测试命名

```typescript
// ✅ 好的测试命名
describe('UserProfile Component', () => {
  it('应该显示用户头像和姓名', () => {});
  it('应该在用户未登录时显示默认头像', () => {});
  it('应该在点击编辑按钮时打开编辑模式', () => {});
});

// ❌ 不好的测试命名
describe('UserProfile', () => {
  it('test1', () => {});
  it('renders', () => {});
});
```

### 2. 测试结构

使用 AAA 模式（Arrange, Act, Assert）：

```typescript
it('应该计算正确的BMI值', () => {
  // Arrange - 准备测试数据
  const height = 170; // cm
  const weight = 70;  // kg
  
  // Act - 执行被测试的操作
  const bmi = calculateBMI(height, weight);
  
  // Assert - 验证结果
  expect(bmi).toBeCloseTo(24.22, 2);
});
```

### 3. Mock 策略

```typescript
// ✅ 合理的 Mock
jest.mock('@/services/apiClient', () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

// ✅ 部分 Mock
jest.mock('@/utils/dateUtils', () => ({
  ...jest.requireActual('@/utils/dateUtils'),
  getCurrentTimestamp: jest.fn(() => 1640995200000),
}));
```

### 4. 异步测试

```typescript
// ✅ 使用 async/await
it('应该异步加载用户数据', async () => {
  const userData = await userService.getCurrentUser();
  expect(userData).toBeDefined();
});

// ✅ 使用 waitFor
it('应该等待加载完成', async () => {
  render(<UserProfile />);
  
  await waitFor(() => {
    expect(screen.getByText('用户姓名')).toBeTruthy();
  });
});
```

### 5. 测试数据管理

```typescript
// 使用工厂函数创建测试数据
const createMockUser = (overrides = {}) => ({
  id: '1',
  name: '测试用户',
  email: 'test@example.com',
  ...overrides,
});

// 使用 beforeEach 清理状态
beforeEach(() => {
  jest.clearAllMocks();
  // 重置全局状态
});
```

### 6. 错误测试

```typescript
it('应该处理网络错误', async () => {
  // 模拟网络错误
  mockApiClient.get.mockRejectedValue(new Error('Network error'));
  
  await expect(userService.getProfile()).rejects.toThrow('Network error');
});
```

## 故障排除

### 常见问题

1. **测试超时**
   ```typescript
   // 增加超时时间
   it('长时间运行的测试', async () => {
     // 测试代码
   }, 10000); // 10秒超时
   ```

2. **Mock 不生效**
   ```typescript
   // 确保 Mock 在正确位置
   jest.mock('@/services/api', () => ({
     // Mock 实现
   }));
   ```

3. **异步测试失败**
   ```typescript
   // 使用 waitFor 等待异步操作
   await waitFor(() => {
     expect(element).toBeTruthy();
   });
   ```

### 调试技巧

1. **使用 console.log**
   ```typescript
   it('调试测试', () => {
     console.log('当前状态:', component.state);
   });
   ```

2. **使用 screen.debug()**
   ```typescript
   it('查看渲染结果', () => {
     render(<Component />);
     screen.debug(); // 打印当前 DOM 结构
   });
   ```

## 总结

良好的测试策略是确保索克生活项目质量的关键。通过遵循本指南中的最佳实践，我们可以：

- 提高代码质量和可靠性
- 减少生产环境的 bug
- 提升开发效率
- 增强代码的可维护性

记住：**测试不是负担，而是投资**。投入时间编写好的测试，会在长期开发中节省大量的调试和修复时间。 