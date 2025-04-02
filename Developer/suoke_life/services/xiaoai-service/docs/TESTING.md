# 小艾智能体服务测试指南

本文档提供了关于如何设置和运行小艾智能体服务测试的详细说明。

## 测试架构

测试套件使用以下技术和框架：

- **Jest**: 作为主要测试框架
- **ts-jest**: 用于TypeScript支持
- **测试类型**:
  - 单元测试: 测试单个组件的功能
  - 集成测试: 测试组件之间的交互
  - 端到端测试: 测试整个应用流程

## 测试目录结构

```
tests/
├── jest.config.js                # Jest配置文件
├── unit/                         # 单元测试
│   ├── helpers/                  # 测试辅助工具
│   │   ├── mockMongoose.ts       # Mongoose模拟工具
│   │   └── mockRedis.ts          # Redis模拟工具
│   ├── repositories/             # 数据仓库测试
│   │   ├── BaseRepository.test.ts
│   │   ├── UserRepository.test.ts
│   │   ├── ConversationRepository.test.ts
│   │   └── XiaoAiAgentRepository.test.ts
│   ├── services/                 # 服务测试
│   │   ├── CacheService.test.ts
│   │   └── DialogueService.test.ts
│   ├── controllers/              # 控制器测试
│   │   └── xiaoAi.controller.test.ts
│   ├── providers/                # 提供者测试
│   │   └── providers.test.ts
│   └── integration/              # 集成测试
│       ├── database.integration.test.ts
│       └── cache.integration.test.ts
└── e2e/                          # 端到端测试(未来扩展)
```

## 测试辅助工具

测试套件提供了几个辅助工具来简化测试过程：

### Mongoose模拟工具 (`mockMongoose.ts`)

提供了对Mongoose数据库操作的模拟实现，使单元测试可以在没有实际数据库连接的情况下运行。

主要函数：
- `createMockModel()`: 创建模拟的Mongoose模型
- `createMockDocument()`: 创建模拟的文档实例
- `clearAllMocks()`: 清除所有模拟状态

### Redis模拟工具 (`mockRedis.ts`)

提供了对Redis客户端的模拟实现，使单元测试可以在没有实际Redis连接的情况下运行。

主要函数：
- `createMockRedisClient()`: 创建模拟的Redis客户端
- `clearRedisMocks()`: 清除所有Redis模拟状态

## 运行测试

### 前提条件

- 安装Node.js（推荐版本：16+）
- 安装项目依赖：`npm install`

### 使用NPM脚本运行测试

使用以下命令运行不同类型的测试：

```bash
# 运行所有测试
npm test

# 观察模式运行测试（在文件更改时自动重新运行）
npm run test:watch

# 生成测试覆盖率报告
npm run test:coverage

# 仅运行仓库测试
npm run test:repositories

# 仅运行服务测试
npm run test:services
```

### 使用测试运行脚本

提供了更灵活的测试运行脚本，可通过以下命令使用：

```bash
# 获取帮助信息
npm run test:run

# 运行所有测试
npm run test:full

# 仅运行单元测试
npm run test:unit

# 仅运行集成测试
npm run test:integration

# 直接使用脚本并传递参数
bash scripts/run-tests.sh --unit --watch
```

可用选项：
- `-a, --all`: 运行所有测试
- `-u, --unit`: 仅运行单元测试
- `-i, --integration`: 仅运行集成测试
- `-r, --repositories`: 仅运行仓库测试
- `-s, --services`: 仅运行服务测试
- `-c, --controllers`: 仅运行控制器测试
- `-w, --watch`: 观察模式运行测试
- `-h, --help`: 显示帮助信息

## 集成测试注意事项

运行集成测试需要以下环境：

### 数据库集成测试

需要可用的MongoDB实例：

```bash
# 设置MongoDB连接
export MONGODB_URI="mongodb://localhost:27017/xiaoai_test"
```

### 缓存服务集成测试

需要可用的Redis实例：

```bash
# 设置Redis连接
export REDIS_URL="redis://localhost:6379/1"
```

**注意**：集成测试将会创建和删除数据，建议使用专用的测试数据库/实例。

## 编写测试

遵循以下原则编写新测试：

1. **测试文件命名**: 使用 `.test.ts` 或 `.spec.ts` 后缀
2. **测试分组**: 使用 `describe` 将相关测试分组
3. **测试案例**: 使用 `it` 或 `test` 定义单个测试案例
4. **断言**: 使用 Jest 的 `expect` 函数进行断言
5. **设置与清理**: 使用 `beforeEach/afterEach` 设置和清理测试环境

示例：

```typescript
import { SomeService } from '../../src/services/SomeService';

describe('SomeService', () => {
  let service: SomeService;
  
  beforeEach(() => {
    service = new SomeService();
  });
  
  it('应该执行某个功能', () => {
    const result = service.someMethod();
    expect(result).toBe(expectedValue);
  });
});
```

## 测试覆盖率

测试覆盖率报告会在运行 `npm run test:coverage` 后生成在 `coverage/` 目录中。

目标覆盖率：
- 整体代码覆盖率: 80%+
- 关键服务和仓库: 90%+
- 工具类和辅助函数: 70%+ 