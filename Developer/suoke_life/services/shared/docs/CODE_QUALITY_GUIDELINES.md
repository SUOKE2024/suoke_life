# 索克生活代码质量优化指南

本文档基于SonarCloud分析结果，提供代码质量优化的具体措施和最佳实践。

## 常见代码质量问题及解决方案

### 1. 安全漏洞 (Security Vulnerabilities)

#### SQL注入漏洞
- **问题**: 使用未参数化的SQL查询
- **解决方案**: 
  ```typescript
  // 错误写法 ❌
  const query = `SELECT * FROM users WHERE username = '${username}'`;
  
  // 正确写法 ✅
  const query = `SELECT * FROM users WHERE username = ?`;
  const result = await db.query(query, [username]);
  ```

#### 敏感数据暴露
- **问题**: 硬编码密钥、令牌或密码
- **解决方案**: 使用环境变量或密钥管理系统存储敏感信息
  ```typescript
  // 错误写法 ❌
  const apiKey = "1234567890abcdef";
  
  // 正确写法 ✅
  const apiKey = process.env.API_KEY;
  ```

### 2. 代码异味 (Code Smells)

#### 过长函数
- **问题**: 函数超过50行代码
- **解决方案**: 将大函数分解为更小、更专注的函数
  ```typescript
  // 重构前 ❌
  async function processUserData(userId) {
    // 200行代码...
  }
  
  // 重构后 ✅
  async function processUserData(userId) {
    const userData = await fetchUserData(userId);
    const processedData = transformUserData(userData);
    await saveUserData(processedData);
    return processedData;
  }
  
  async function fetchUserData(userId) { /* ... */ }
  function transformUserData(data) { /* ... */ }
  async function saveUserData(data) { /* ... */ }
  ```

#### 重复代码
- **问题**: 代码在多个地方重复出现
- **解决方案**: 提取共用函数或使用设计模式减少重复
  ```typescript
  // 提取公共逻辑到工具函数
  // utils/validation.ts
  export function validateUserId(id: string): boolean {
    return id && id.length === 24 && /^[0-9a-f]{24}$/.test(id);
  }
  ```

### 3. 单元测试覆盖率

#### 提高测试覆盖率
- **目标**: 达到80%以上的代码覆盖率
- **策略**:
  1. 对核心业务逻辑优先编写测试
  2. 使用测试驱动开发(TDD)方法
  3. 为每个公共函数和方法编写至少一个测试用例

#### 有效的测试示例
```typescript
// 原始函数
export function calculateHealthScore(metrics: HealthMetrics): number {
  let score = 0;
  if (metrics.sleepHours >= 7) score += 25;
  if (metrics.exerciseMinutes >= 30) score += 25;
  if (metrics.waterIntake >= 2000) score += 25;
  if (metrics.stressLevel <= 3) score += 25;
  return score;
}

// 测试用例
describe('calculateHealthScore', () => {
  it('返回满分当所有指标都达标', () => {
    const metrics = {
      sleepHours: 8,
      exerciseMinutes: 45,
      waterIntake: 2500,
      stressLevel: 2
    };
    expect(calculateHealthScore(metrics)).toBe(100);
  });
  
  it('返回0分当所有指标都不达标', () => {
    const metrics = {
      sleepHours: 5,
      exerciseMinutes: 15,
      waterIntake: 1000,
      stressLevel: 8
    };
    expect(calculateHealthScore(metrics)).toBe(0);
  });
  
  it('返回部分分数当部分指标达标', () => {
    const metrics = {
      sleepHours: 7,
      exerciseMinutes: 20,
      waterIntake: 2200,
      stressLevel: 5
    };
    expect(calculateHealthScore(metrics)).toBe(50); // 只有睡眠和水分摄入达标
  });
});
```

### 4. 类型安全

#### TypeScript严格模式
- **问题**: 松散的类型检查导致运行时错误
- **解决方案**: 启用严格模式和其他严格检查选项
  ```json
  // tsconfig.json
  {
    "compilerOptions": {
      "strict": true,
      "noImplicitAny": true,
      "strictNullChecks": true,
      "strictFunctionTypes": true,
      "strictBindCallApply": true,
      "strictPropertyInitialization": true,
      "noImplicitThis": true,
      "useUnknownInCatchVariables": true,
      "alwaysStrict": true
    }
  }
  ```

#### 类型断言最佳实践
- **问题**: 不安全的类型断言
- **解决方案**: 使用类型守卫和类型收窄
  ```typescript
  // 错误写法 ❌
  function processValue(value: any) {
    return (value as string).toLowerCase();
  }
  
  // 正确写法 ✅
  function processValue(value: unknown) {
    if (typeof value === 'string') {
      return value.toLowerCase();
    }
    throw new Error('Value must be a string');
  }
  ```

### 5. 性能优化

#### 内存泄漏
- **问题**: 未释放的资源或引用
- **解决方案**: 正确关闭连接和清理监听器
  ```typescript
  // 错误写法 ❌
  function setupEventSource() {
    const eventSource = new EventSource('/api/events');
    eventSource.onmessage = (event) => {
      console.log(event.data);
    };
  }
  
  // 正确写法 ✅
  function setupEventSource() {
    const eventSource = new EventSource('/api/events');
    eventSource.onmessage = (event) => {
      console.log(event.data);
    };
    
    return () => {
      eventSource.close(); // 清理资源
    };
  }
  ```

#### 数据库查询优化
- **问题**: 低效的数据库查询
- **解决方案**: 添加适当的索引和限制返回字段
  ```typescript
  // 优化前 ❌
  const users = await db.collection('users').find({}).toArray();
  
  // 优化后 ✅
  const users = await db.collection('users')
    .find({})
    .project({ name: 1, email: 1, _id: 1 }) // 只返回需要的字段
    .limit(100) // 限制结果数量
    .toArray();
  ```

## 项目级别代码质量监控

### 集成SonarCloud到开发流程

1. **自动分析**:
   - 每次PR时触发SonarCloud分析
   - 每周定期对main分支进行完整分析

2. **质量门控**:
   - 设置必要的质量门标准以阻止低质量代码合并
   - 关键指标: 零新增漏洞、测试覆盖率>80%、重复代码<5%

3. **代码审查整合**:
   - 使用SonarCloud提供的PR装饰
   - 审查者关注SonarCloud标记的问题

### 持续改进策略

1. **技术债务管理**:
   - 每个Sprint分配20%时间用于解决技术债务
   - 按严重性排序处理已识别的问题

2. **团队代码质量文化**:
   - 定期代码质量回顾会议
   - 鼓励团队成员共享最佳实践

## 服务特定优化建议

### 知识图谱服务

```typescript
// 优化图查询性能
// 1. 使用索引
await graphDB.createIndex({
  name: 'entity_type_index',
  type: 'graph',
  fields: ['entityType']
});

// 2. 批量操作替代单条操作
// 避免这样 ❌
for (const node of nodes) {
  await graphDB.createNode(node);
}

// 推荐这样 ✅
await graphDB.createNodes(nodes);
```

### RAG服务

```python
# 优化向量搜索
# 1. 使用非对称索引减少内存使用
index = faiss.IndexHNSWFlat(dimension, 32)  # 32个邻居

# 2. 实现批处理而不是单条查询
def batch_search(texts, top_k=5):
    embeddings = embed_model.encode(texts)
    return index.search(embeddings, top_k)
```

### 小艾服务

```typescript
// 1. 实现请求缓存
const responseCache = new LRUCache({
  max: 1000,  // 最多缓存1000个响应
  ttl: 1000 * 60 * 60 * 24  // 24小时过期
});

// 2. 使用流式响应减少首次响应时间
app.post('/api/v1/chat-stream', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  
  for await (const chunk of aiService.generateResponseStream(req.body.message)) {
    res.write(`data: ${JSON.stringify({ text: chunk })}\n\n`);
  }
  
  res.end();
});
```

## 后续步骤和衡量成效

1. **建立基线**:
   - 记录当前SonarCloud评分和关键指标
   - 设置90天内达成的改进目标

2. **监控进展**:
   - 每周检查SonarCloud趋势图
   - 跟踪已解决和新增问题的比率

3. **衡量业务影响**:
   - 分析代码质量改进与生产事故频率的关系
   - 测量开发周期时间的变化