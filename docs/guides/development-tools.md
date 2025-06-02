# 索克生活开发工具使用指南

## 🛠️ 新增开发工具概览

本项目在前端Bug修复过程中新增了多个开发工具，用于提升代码质量和开发效率。

### 1. Logger服务 (`src/services/Logger.ts`)

统一的日志管理服务，支持开发/生产环境区分。

#### 使用方法
```typescript
import { Logger } from '../services/Logger';

// 基本使用
Logger.info('用户登录成功', { userId: '123' });
Logger.warn('网络请求超时', { url: '/api/health' });
Logger.error('数据加载失败', error);

// 调试信息（仅开发环境）
Logger.debug('组件渲染状态', { state });
```

#### 特性
- 🔧 开发环境控制台输出
- 📊 生产环境错误监控集成
- 💾 内存日志缓存
- ⏰ 时间戳和堆栈跟踪

### 2. 性能监控Hook (`src/hooks/usePerformanceMonitor.ts`)

组件渲染性能监控和内存使用跟踪。

#### 使用方法
```typescript
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';

function MyComponent() {
  const performanceMonitor = usePerformanceMonitor('MyComponent', {
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms
  });

  // 记录渲染性能
  performanceMonitor.recordRender();

  return <View>...</View>;
}
```

#### 特性
- 📊 组件渲染时间监控
- 💾 内存使用情况跟踪
- ⚠️ 性能阈值警告
- 📈 开发环境性能指标记录

### 3. 内存泄漏检测工具 (`src/utils/memoryLeakDetector.ts`)

定时器和事件监听器泄漏检测。

#### 使用方法
```typescript
import { memoryLeakDetector } from '../utils/memoryLeakDetector';

// 在组件中使用
useEffect(() => {
  const timerId = setInterval(() => {
    // 定时任务
  }, 1000);

  // 注册定时器以便检测
  memoryLeakDetector.trackTimer(timerId);

  return () => {
    clearInterval(timerId);
    memoryLeakDetector.untrackTimer(timerId);
  };
}, []);
```

#### 特性
- ⏰ 定时器跟踪和清理
- 🎧 事件监听器管理
- 🔄 组件生命周期监控
- 📋 泄漏报告生成

### 4. API类型定义 (`src/types/api.ts`)

完整的TypeScript类型安全接口。

#### 使用方法
```typescript
import { ApiResponse, HealthData, AgentMessage } from '../types/api';

// API响应类型
const response: ApiResponse<HealthData> = await fetchHealthData();

// 智能体消息类型
const message: AgentMessage = {
  id: '123',
  content: 'Hello',
  sender: 'xiaoai',
  timestamp: Date.now(),
};
```

## 🔧 修复脚本使用指南

### 1. TypeScript错误修复
```bash
node scripts/fix-typescript-errors.js
```

### 2. 测试套件增强
```bash
node scripts/enhance-test-suite.js
```

### 3. 性能监控集成
```bash
node scripts/integrate-performance-monitoring.js
```

### 4. 前端修复总结
```bash
node scripts/frontend-fix-summary.js
```

## 📊 性能监控配置

性能监控配置文件位于 `src/config/performance.ts`，可以自定义：

- 全局监控开关
- 开发/生产环境配置
- 组件特定配置
- 性能阈值设置

## 🧪 测试最佳实践

1. **组件测试**：使用自动生成的测试模板
2. **Hook测试**：使用 `@testing-library/react-hooks`
3. **性能测试**：集成性能监控Hook
4. **覆盖率目标**：保持80%以上的测试覆盖率

## 🚀 持续集成建议

1. 在CI/CD中运行所有修复脚本
2. 设置性能基准和警告阈值
3. 定期生成性能报告
4. 监控内存泄漏和性能回归

## 📝 开发规范

1. **日志记录**：使用Logger服务而非console
2. **性能监控**：关键组件必须集成性能监控
3. **类型安全**：使用严格的TypeScript类型
4. **测试覆盖**：新功能必须包含测试用例
