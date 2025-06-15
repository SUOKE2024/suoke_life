# 索克生活 Agentic AI 测试验证文档

## 📋 测试概述

本测试套件为索克生活的Agentic AI架构升级提供全面的质量保证，确保系统在各种场景下的可靠性、性能和用户体验。

## 🏗️ 测试架构

### 测试分层结构

```
tests/
├── agentic/                 # 单元测试
│   ├── AgenticWorkflowEngine.test.ts
│   ├── ReflectionSystem.test.ts
│   ├── PlanningSystem.test.ts
│   ├── ToolOrchestrationSystem.test.ts
│   └── AgenticCollaborationSystem.test.ts
├── integration/             # 集成测试
│   └── AgenticIntegration.test.ts
├── performance/             # 性能测试
│   └── AgenticPerformance.test.ts
├── e2e/                     # 端到端测试
│   └── AgenticE2E.test.ts
├── setup/                   # 测试配置
│   ├── jest.setup.ts
│   └── custom-matchers.ts
├── scripts/                 # 测试脚本
│   └── run-tests.sh
├── jest.config.js           # Jest配置
└── README.md               # 本文档
```

## 🧪 测试类型

### 1. 单元测试 (Unit Tests)
- **目标**: 测试各个Agentic AI组件的独立功能
- **覆盖范围**: 
  - AgenticWorkflowEngine: 工作流引擎核心逻辑
  - ReflectionSystem: 反思系统的自我评估能力
  - PlanningSystem: 规划系统的决策制定
  - ToolOrchestrationSystem: 工具编排和选择
  - AgenticCollaborationSystem: 多智能体协作机制

### 2. 集成测试 (Integration Tests)
- **目标**: 验证Agentic AI系统与现有架构的集成
- **覆盖范围**:
  - 五诊系统集成
  - 区块链健康数据集成
  - 微服务架构集成
  - 四个智能体协作流程

### 3. 性能测试 (Performance Tests)
- **目标**: 确保系统满足性能要求
- **关键指标**:
  - 响应时间: 简单任务 <200ms, 复杂任务 <2s
  - 吞吐量: ≥50 请求/秒
  - 内存使用: 合理范围内
  - 并发处理: 支持高负载

### 4. 端到端测试 (E2E Tests)
- **目标**: 模拟真实用户场景的完整流程
- **测试场景**:
  - 新用户健康评估流程
  - 老年慢性病管理流程
  - 急性症状紧急处理
  - 复杂病例多智能体会诊

## 🎯 性能基准

### 响应时间目标
- **简单咨询**: < 200ms
- **复杂诊断**: < 2000ms
- **紧急处理**: < 30s (首次响应)
- **协作决策**: < 5000ms

### 质量分数目标
- **诊断准确率**: > 90%
- **用户满意度**: > 90%
- **协作共识率**: > 88%
- **系统可用性**: > 99.5%

### 吞吐量目标
- **并发用户**: 支持1000+
- **每秒请求**: ≥ 50 req/s
- **峰值处理**: 支持10倍突发流量

## 🚀 快速开始

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0
- TypeScript >= 4.5.0
- Jest >= 29.0.0

### 安装依赖
```bash
npm install
```

### 运行测试

#### 运行所有测试
```bash
./tests/scripts/run-tests.sh --all
```

#### 运行特定类型测试
```bash
# 单元测试
./tests/scripts/run-tests.sh --unit

# 集成测试
./tests/scripts/run-tests.sh --integration

# 性能测试
./tests/scripts/run-tests.sh --performance

# 端到端测试
./tests/scripts/run-tests.sh --e2e
```

#### 生成覆盖率报告
```bash
./tests/scripts/run-tests.sh --unit --coverage
```

#### 监视模式
```bash
./tests/scripts/run-tests.sh --watch
```

## 📊 测试报告

### 报告类型
1. **HTML报告**: `tests/reports/test-report.html`
2. **覆盖率报告**: `tests/coverage/lcov-report/index.html`
3. **JUnit报告**: `tests/reports/junit.xml`
4. **性能报告**: 控制台输出

### 覆盖率要求
- **整体覆盖率**: ≥ 85%
- **核心组件覆盖率**: ≥ 90%
- **分支覆盖率**: ≥ 80%
- **函数覆盖率**: ≥ 85%

## 🔧 自定义匹配器

测试套件提供了专用的Jest匹配器：

```typescript
// 验证Agentic任务格式
expect(task).toBeValidAgenticTask();

// 验证工作流结果
expect(result).toBeValidWorkflowResult();

// 验证质量分数
expect(result).toHaveQualityScore(0.8, 1.0);

// 验证响应时间
expect(result).toHaveResponseTimeBelow(1000);

// 验证诊断结果
expect(diagnosis).toBeValidDiagnosis();

// 验证协作结果
expect(collaboration).toBeValidCollaborationResult();
```

## 🧩 测试场景

### 健康管理场景
1. **新用户首次评估**
   - 初始健康咨询
   - 五诊详细评估
   - 个性化治疗方案
   - 长期健康计划

2. **慢性病管理**
   - 病情状态评估
   - 药物调整建议
   - 生活方式干预
   - 长期监护计划

3. **紧急处理**
   - 急性症状识别
   - 紧急处理指导
   - 实时监护
   - 转诊建议

### 技术集成场景
1. **五诊系统集成**
   - 望闻问切算数据处理
   - 中医证候分析
   - 体质辨识

2. **区块链集成**
   - 数据完整性验证
   - 隐私保护
   - 审计追踪

3. **微服务集成**
   - 服务间通信
   - 数据一致性
   - 故障容错

## 🔍 调试和故障排除

### 常见问题

1. **测试超时**
   ```bash
   # 增加超时时间
   jest --testTimeout=60000
   ```

2. **内存不足**
   ```bash
   # 限制并发数
   jest --maxWorkers=2
   ```

3. **模拟失败**
   ```bash
   # 清除模拟缓存
   jest --clearCache
   ```

### 调试技巧

1. **启用详细输出**
   ```bash
   ./tests/scripts/run-tests.sh --verbose
   ```

2. **运行单个测试**
   ```bash
   npx jest --testNamePattern="特定测试名称"
   ```

3. **调试模式**
   ```bash
   node --inspect-brk node_modules/.bin/jest --runInBand
   ```

## 📈 持续集成

### CI/CD 配置
```yaml
# .github/workflows/test.yml
name: Agentic AI Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: ./tests/scripts/run-tests.sh --all --ci --coverage
      - uses: codecov/codecov-action@v3
```

### 质量门禁
- 所有测试必须通过
- 覆盖率不低于85%
- 性能指标满足要求
- 无严重安全漏洞

## 🎨 最佳实践

### 测试编写原则
1. **AAA模式**: Arrange, Act, Assert
2. **单一职责**: 每个测试只验证一个功能点
3. **独立性**: 测试之间不应相互依赖
4. **可重复性**: 测试结果应该一致
5. **有意义的命名**: 测试名称应清楚描述测试内容

### 性能测试建议
1. **基准测试**: 建立性能基准线
2. **负载测试**: 模拟真实负载
3. **压力测试**: 测试系统极限
4. **监控指标**: 关注关键性能指标

### 模拟策略
1. **外部依赖**: 模拟所有外部服务
2. **时间控制**: 使用固定时间进行测试
3. **随机性**: 控制随机因素
4. **网络条件**: 模拟不同网络环境

## 📚 参考资源

- [Jest 官方文档](https://jestjs.io/docs/getting-started)
- [TypeScript Jest 配置](https://jestjs.io/docs/getting-started#using-typescript)
- [测试最佳实践](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [性能测试指南](https://web.dev/performance-testing/)

## 🤝 贡献指南

### 添加新测试
1. 确定测试类型和位置
2. 遵循现有命名约定
3. 使用自定义匹配器
4. 添加适当的文档
5. 更新覆盖率要求

### 报告问题
1. 提供详细的错误信息
2. 包含重现步骤
3. 说明预期行为
4. 提供环境信息

---

**注意**: 本测试套件是索克生活Agentic AI架构升级的重要组成部分，确保系统质量和用户体验。请在修改代码后及时运行相关测试，保持代码质量。