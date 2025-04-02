# API测试指南

本指南提供了如何测试索克生活知识库服务API的详细说明，包括使用Swagger UI进行交互测试和使用自动化工具进行集成测试。

## 使用Swagger UI测试

Swagger UI提供了一个交互式界面，可以直接在浏览器中测试API。

### 准备工作

1. 确保服务正在运行：
   ```bash
   npm run dev
   ```

2. 打开Swagger UI：
   ```
   http://localhost:3002/api-docs
   ```

### 认证设置

对于需要认证的API：

1. 点击Swagger UI界面顶部的"Authorize"按钮
2. 根据需要选择认证方式：
   - **JWT认证**：输入`Bearer your_token_here`
   - **API密钥**：输入您的API密钥

### 执行测试

1. 展开要测试的API端点
2. 填写必要的请求参数：
   - 路径参数（Path parameters）
   - 查询参数（Query parameters）
   - 请求体（Request body）
3. 点击"Execute"按钮
4. 查看：
   - 请求URL和请求体
   - 响应状态码
   - 响应头
   - 响应体

### 常见测试场景

#### 1. 获取知识条目列表

测试分页、过滤和排序功能：
- 尝试不同的`page`和`limit`值
- 使用不同的`sortBy`和`sortDirection`参数
- 添加过滤条件如`categories`或`tags`

#### 2. 创建新知识条目

提供必要的字段并验证：
- 所有必需字段均已填写
- 格式验证是否正常工作
- 创建后能否通过获取API找到

#### 3. 版本控制测试

测试版本管理功能：
- 创建知识条目的新版本
- 获取历史版本列表
- 比较两个版本的差异
- 回滚到特定版本

#### 4. 审核流程测试

测试完整的审核流程：
- 提交内容审核
- 查看待审核列表
- 通过/拒绝审核
- 验证状态变更

## 使用自动化工具测试

### Postman

1. **导入OpenAPI规范**
   - 从`/api-docs.json`获取OpenAPI规范
   - 在Postman中导入该规范

2. **设置环境变量**
   ```
   BASE_URL: http://localhost:3002/api
   AUTH_TOKEN: your_token_here
   API_KEY: your_api_key_here
   ```

3. **使用集合运行器**
   - 创建测试脚本验证响应
   - 使用集合运行器按顺序执行请求
   - 保存测试结果以供分析

### 自动化测试脚本

使用Jest和Supertest进行API测试：

```typescript
import request from 'supertest';
import app from '../src/app';

describe('知识库API测试', () => {
  let authToken: string;
  let createdItemId: string;

  beforeAll(async () => {
    // 获取认证令牌
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        username: 'test@example.com',
        password: 'password123'
      });
    
    authToken = response.body.data.token;
  });

  test('创建知识条目', async () => {
    const response = await request(app)
      .post('/api/knowledge/tcm')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: '测试条目',
        content: '测试内容',
        tags: ['测试', '示例']
      });
    
    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    
    createdItemId = response.body.data.id;
  });

  test('获取知识条目', async () => {
    const response = await request(app)
      .get(`/api/knowledge/tcm/${createdItemId}`)
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.title).toBe('测试条目');
  });

  // 更多测试...
});
```

### 性能测试

使用k6进行负载测试：

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function() {
  const baseUrl = 'http://localhost:3002/api';
  
  // 获取知识条目列表
  const listResponse = http.get(`${baseUrl}/knowledge/tcm?page=1&limit=10`);
  check(listResponse, {
    'status is 200': (r) => r.status === 200,
    'response has items': (r) => JSON.parse(r.body).data.items.length > 0
  });
  
  sleep(1);
}
```

## 错误处理测试

确保测试各种错误场景：

1. **验证错误**
   - 提交无效数据（缺少必填字段、格式错误等）
   - 验证错误响应格式和状态码

2. **授权错误**
   - 没有令牌访问受保护的端点
   - 使用过期或无效的令牌
   - 使用权限不足的账户

3. **资源不存在**
   - 尝试访问不存在的资源ID
   - 验证404响应和错误消息

4. **服务器错误模拟**
   - 当使用测试环境时，可以触发模拟的服务器错误
   - 验证错误处理和日志记录

## 测试检查清单

进行全面测试时，请检查以下方面：

- [ ] 所有端点都能返回预期的状态码和数据结构
- [ ] 认证和授权机制正常工作
- [ ] 输入验证能正确处理无效数据
- [ ] 分页、排序和过滤功能正常工作
- [ ] 错误响应包含有用的错误消息
- [ ] API性能在可接受的范围内
- [ ] 所有业务流程（如审核、版本控制）都能按预期工作

## 报告问题

发现API问题时，请提供以下信息：

1. API端点和HTTP方法
2. 请求参数和请求体
3. 预期响应和实际响应
4. 错误消息和状态码
5. 重现步骤
6. 环境信息（开发、测试或生产）

## 资源

- [Jest文档](https://jestjs.io/docs/getting-started)
- [Supertest文档](https://github.com/visionmedia/supertest)
- [Postman文档](https://learning.postman.com/docs/getting-started/introduction/)
- [k6负载测试文档](https://k6.io/docs/)