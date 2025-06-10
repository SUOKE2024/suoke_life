# 索克生活 - 测试套件

## 概述

这是索克生活（Suoke Life）应用的完整测试套件，包含单元测试、集成测试和性能测试。

## 测试结构

```
src/__tests__/
├── components/           # 组件单元测试
│   ├── ProfileHeader.test.tsx
│   └── HealthMetricCard.test.tsx
├── hooks/               # Hook单元测试
│   ├── useProfile.test.ts
│   └── useLife.test.ts
├── integration/         # 集成测试
│   └── ProfileScreen.integration.test.tsx
├── performance/         # 性能测试
│   └── ComponentPerformance.test.tsx
├── jest.config.js       # Jest配置
├── runTests.js          # 测试运行脚本
└── README.md           # 测试文档
```

## 测试类型

### 1. 组件单元测试 (`components/`)

测试React组件的：

- 正确渲染
- Props处理
- 用户交互
- 状态变化
- 错误处理

**示例：**

```bash
npm test -- --testPathPattern=components
```

### 2. Hook单元测试 (`hooks/`)

测试自定义Hook的：

- 状态管理
- 副作用处理
- 返回值正确性
- 错误处理
- 性能优化

**示例：**

```bash
npm test -- --testPathPattern=hooks
```

### 3. 集成测试 (`integration/`)

测试组件间的：

- 数据流
- 用户交互流程
- 页面导航
- 状态同步

**示例：**

```bash
npm test -- --testPathPattern=integration
```

### 4. 性能测试 (`performance/`)

测试应用的：

- 渲染性能
- 内存使用
- 组件卸载
- 重新渲染效率

**示例：**

```bash
npm test -- --testPathPattern=performance
```

## 运行测试

### 运行所有测试

```bash
npm test
```

### 运行特定测试套件

```bash
# 组件测试
npm test -- --testPathPattern=components

# Hook测试
npm test -- --testPathPattern=hooks

# 集成测试
npm test -- --testPathPattern=integration

# 性能测试
npm test -- --testPathPattern=performance
```

### 监视模式

```bash
npm test -- --watch
```

### 生成覆盖率报告

```bash
npm test -- --coverage
```

### 详细输出

```bash
npm test -- --verbose
```

### 使用自定义测试脚本

```bash
node src/__tests__/runTests.js
```

## 测试配置

### Jest配置 (`jest.config.js`)

- **预设**: `react-native`
- **测试环境**: `node`
- **覆盖率阈值**: 70%
- **超时时间**: 10秒
- **Mock设置**: 自动清理和重置

### 测试设置 (`../setupTests.ts`)

包含：

- React Native模块Mock
- 第三方库Mock
- 全局测试配置
- 测试工具函数

## 测试最佳实践

### 1. 组件测试

```tsx
import { render, fireEvent } from '@testing-library/react-native';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('应该正确渲染', () => {
    const { getByText } = render(<MyComponent />);
    expect(getByText('期望文本')).toBeTruthy();
  });

  it('应该处理用户交互', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(<MyComponent onPress={mockOnPress} />);

    fireEvent.press(getByText('按钮'));
    expect(mockOnPress).toHaveBeenCalled();
  });
});
```

### 2. Hook测试

```tsx
import { renderHook, act } from '@testing-library/react-native';
import { useMyHook } from '../useMyHook';

describe('useMyHook', () => {
  it('应该返回正确的初始状态', () => {
    const { result } = renderHook(() => useMyHook());

    expect(result.current.value).toBe(initialValue);
    expect(result.current.loading).toBe(false);
  });

  it('应该正确更新状态', () => {
    const { result } = renderHook(() => useMyHook());

    act(() => {
      result.current.updateValue(newValue);
    });

    expect(result.current.value).toBe(newValue);
  });
});
```

### 3. 集成测试

```tsx
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import MyScreen from '../MyScreen';

const TestWrapper = ({ children }) => (
  <NavigationContainer>{children}</NavigationContainer>
);

describe('MyScreen Integration', () => {
  it('应该完成完整的用户流程', async () => {
    const { getByText } = render(
      <TestWrapper>
        <MyScreen />
      </TestWrapper>
    );

    // 模拟用户操作
    fireEvent.press(getByText('开始'));

    // 等待异步操作
    await waitFor(() => {
      expect(getByText('完成')).toBeTruthy();
    });
  });
});
```

## Mock策略

### 1. React Native组件Mock

```javascript
// setupTests.ts
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
  }),
}));
```

### 2. 异步操作Mock

```javascript
jest.mock('../api/service', () => ({
  fetchData: jest.fn(() => Promise.resolve(mockData)),
}));
```

### 3. 第三方库Mock

```javascript
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: 'SafeAreaView',
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));
```

## 覆盖率目标

- **语句覆盖率**: ≥ 70%
- **分支覆盖率**: ≥ 70%
- **函数覆盖率**: ≥ 70%
- **行覆盖率**: ≥ 70%

## 持续集成

测试套件集成到CI/CD流程中：

1. **代码提交时**: 运行快速测试
2. **Pull Request**: 运行完整测试套件
3. **发布前**: 运行所有测试 + 覆盖率检查

## 故障排除

### 常见问题

1. **Mock失败**

   - 检查Mock路径是否正确
   - 确保Mock在测试前设置

2. **异步测试超时**

   - 使用`waitFor`等待异步操作
   - 增加测试超时时间

3. **组件渲染失败**
   - 检查必需的Props
   - 确保测试环境正确设置

### 调试技巧

```bash
# 运行单个测试文件
npm test -- ProfileHeader.test.tsx

# 调试模式
npm test -- --detectOpenHandles

# 查看详细错误
npm test -- --verbose --no-cache
```

## 贡献指南

### 添加新测试

1. 在相应目录创建测试文件
2. 遵循命名约定：`ComponentName.test.tsx`
3. 包含充分的测试用例
4. 确保测试通过且覆盖率达标

### 测试代码规范

- 使用描述性的测试名称
- 每个测试只验证一个功能点
- 适当使用Mock和Stub
- 清理测试副作用

## 相关资源

- [Jest文档](https://jestjs.io/docs/getting-started)
- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

# 索克生活专项测试目录说明

本目录包含健康数据、AI推理、多Agent协作等专项自动化测试用例模板，覆盖单元、集成、端到端（E2E）各层级。

## 目录结构

- `health_data/`：健康数据处理相关单元与集成测试
- `ai_inference/`：AI推理相关单元与端到端测试
- `agent_collaboration/`：多Agent协作集成测试

## 编写与扩展建议

- 按业务链路和模块分目录，便于专项维护
- 用例命名清晰，描述覆盖场景与预期
- 推荐先补充占位断言，逐步完善真实业务逻辑
- 可结合Mock、Stub等技术模拟外部依赖

## 运行方式

- 推荐通过Jest（前端）或统一CI脚本运行
- 支持单独运行专项测试或全量测试

## 持续优化

- 随业务演进持续补充新链路、新场景的专项测试
- 定期复查用例有效性与覆盖率
