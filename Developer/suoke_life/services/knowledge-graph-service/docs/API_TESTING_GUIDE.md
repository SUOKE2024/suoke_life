# 索克生活知识图谱服务API测试指南

本指南提供了如何测试索克生活知识图谱服务API的方法和最佳实践。包括自动化测试和手动测试方法，帮助开发者确保API功能正常并符合预期。

## 目录

- [测试工具](#测试工具)
- [自动化测试](#自动化测试)
- [手动测试](#手动测试)
- [测试环境](#测试环境)
- [常见测试场景](#常见测试场景)
- [性能测试](#性能测试)
- [安全测试](#安全测试)
- [持续集成](#持续集成)

## 测试工具

推荐使用以下工具进行API测试：

1. **自动化测试**：
   - Jest + Supertest：单元测试和集成测试
   - Mocha + Chai：可选的测试框架
   
2. **手动测试**：
   - Swagger UI：通过API文档直接测试
   - Postman：更强大的手动测试工具
   - curl：命令行测试工具

3. **性能测试**：
   - Artillery：轻量级负载测试
   - k6：高性能负载测试框架

4. **安全测试**：
   - OWASP ZAP：安全漏洞扫描
   - NodeJSScan：Node.js专用安全扫描工具

## 自动化测试

### 单元测试

为服务层和实用工具编写单元测试：

```typescript
// 测试知识图谱服务 - 获取节点
describe('KnowledgeGraphService', () => {
  let service: KnowledgeGraphService;
  
  beforeEach(() => {
    // 设置模拟依赖
  });
  
  test('getNodes 应返回分页节点列表', async () => {
    const result = await service.getNodes({ page: 1, limit: 10 });
    expect(result.items).toHaveLength(10);
    expect(result.pagination.currentPage).toBe(1);
  });
});
```

### 集成测试

使用Supertest测试完整的HTTP请求流程：

```typescript
import { build } from '../src/app';
import supertest from 'supertest';

describe('知识图谱API端点', () => {
  let app;
  
  beforeEach(async () => {
    app = await build();
  });
  
  afterEach(async () => {
    await app.close();
  });
  
  test('GET /api/v1/graph/nodes 应返回节点列表', async () => {
    const response = await supertest(app.server)
      .get('/api/v1/graph/nodes')
      .expect(200)
      .expect('Content-Type', /json/);
      
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toBeDefined();
  });
});
```

### 运行测试

使用以下命令运行测试：

```bash
# 运行所有测试
npm test

# 运行特定测试文件
npm test -- tests/routes/knowledge-graph.test.ts

# 运行带有覆盖率报告的测试
npm run test:coverage
```

## 手动测试

### 使用Swagger UI

1. 访问 `http://localhost:3000/api-docs`
2. 选择要测试的端点
3. 点击"Try it out"按钮
4. 填写必要的参数
5. 点击"Execute"按钮发送请求
6. 查看响应结果

### 使用Postman

1. 导入OpenAPI规范到Postman
   - 在Postman中，点击"Import" > "Link"
   - 输入 `http://localhost:3000/api-docs/json`
   - 点击"Import"按钮
2. 使用生成的请求集合进行测试
3. 为不同环境创建环境变量

### 使用curl

示例命令：

```bash
# 获取节点列表
curl -X GET "http://localhost:3000/api/v1/graph/nodes?page=1&limit=10" -H "accept: application/json"

# 创建新节点
curl -X POST "http://localhost:3000/api/v1/graph/nodes" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"type":"TCMHerb","labels":["中药","植物类"],"properties":{"name":"人参","pinyin":"renshen","description":"补气补血药"}}'
```

## 测试环境

### 环境配置

确保针对每个环境使用正确的配置：

1. **本地开发环境**：
   - 基本URL: `http://localhost:3000`
   - 使用测试用Neo4j数据库

2. **测试环境**：
   - 基本URL: `http://test.api.suoke.life/knowledge-graph`
   - 使用隔离的测试数据

3. **生产环境**：
   - 基本URL: `https://api.suoke.life/knowledge-graph`
   - 只进行非破坏性测试

### 测试数据管理

1. 使用测试脚本创建一致的测试数据：
   ```bash
   npm run setup:test-data
   ```

2. 每次测试后清理数据：
   ```bash
   npm run cleanup:test-data
   ```

## 常见测试场景

### 1. 知识图谱基础操作

- 创建多种类型的节点（TCM中药、疾病、食材等）
- 创建不同类型的关系
- 查询节点和关系
- 更新节点属性
- 删除节点和关系

### 2. 图谱查询场景

- 路径查询：找到两个节点之间的路径
- 复杂过滤：按多种条件筛选节点
- 分页和排序：测试各种分页和排序组合

### 3. 知识搜索场景

- 关键词搜索：测试不同复杂度的搜索查询
- 向量搜索：测试语义相似性搜索
- 自然语言查询：测试复杂问题的回答能力
- 自动完成：测试前缀匹配建议

### 4. 可视化API场景

- 2D可视化：测试不同布局算法和过滤条件
- 3D可视化：测试3D渲染数据格式
- AR可视化：测试AR场景数据结构

## 性能测试

使用Artillery进行负载测试：

1. 创建测试脚本 `performance-test.yml`：
```yaml
config:
  target: "http://localhost:3000"
  phases:
    - duration: 60
      arrivalRate: 5
      rampTo: 50
      name: "Warm up phase"
    - duration: 120
      arrivalRate: 50
      name: "Sustained load"
  defaults:
    headers:
      accept: "application/json"

scenarios:
  - name: "获取节点列表和详情"
    flow:
      - get:
          url: "/api/v1/graph/nodes?page=1&limit=20"
          capture:
            - json: "$.data.items[0].id"
              as: "nodeId"
      - get:
          url: "/api/v1/graph/nodes/{{ nodeId }}"
```

2. 运行测试：
```bash
artillery run performance-test.yml
```

## 安全测试

建议执行以下安全测试：

1. **输入验证测试**：
   - 测试各种恶意输入，如XSS和注入攻击
   - 测试过大的请求体
   
2. **认证和授权测试**：
   - 尝试未经授权访问受保护端点
   - 测试令牌失效或篡改的场景
   
3. **速率限制测试**：
   - 测试API速率限制是否生效
   - 确认系统在过多请求下保持稳定

## 持续集成

在CI管道中设置自动化测试：

```yaml
# .github/workflows/api-test.yml 示例
name: API Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      neo4j:
        image: neo4j:4.4
        env:
          NEO4J_AUTH: neo4j/password
        ports:
          - 7474:7474
          - 7687:7687
    
    steps:
      - uses: actions/checkout@v2
      - name: Use Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
      - name: Generate coverage report
        run: npm run test:coverage
      - name: Upload coverage report
        uses: codecov/codecov-action@v2
```

## 测试检查清单

每次发布前确保：

- [x] 所有单元测试通过
- [x] 所有集成测试通过
- [x] 已手动测试主要功能
- [x] 已进行性能测试并满足SLA
- [x] 已检查安全漏洞
- [x] 已验证API响应格式符合规范
- [x] 已测试错误处理
- [x] 已测试边界条件