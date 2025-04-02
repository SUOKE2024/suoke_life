# 索克生活微服务API契约测试框架

本目录包含用于验证微服务之间API契约一致性的测试框架。API契约测试确保服务之间的接口保持兼容，即使内部实现发生变化。

## 目录结构

```
api-contract-tests/
├── schemas/ - OpenAPI规范文件
│   ├── xiaoai-service.yaml
│   ├── rag-service.yaml
│   └── ...
├── tests/ - 契约测试代码
│   ├── xiaoai-rag-contract.test.js
│   └── ...
├── contract-test-runner.js - 测试运行器
└── README.md - 文档
```

## 使用方法

### 添加新服务API契约

1. 在`schemas/`目录下创建一个新的OpenAPI规范文件，命名为`<service-name>.yaml`
2. 定义服务API的端点、请求和响应模式

例如，新建`schemas/xiaoai-service.yaml`:

```yaml
openapi: 3.0.0
info:
  title: 小艾服务API
  version: 1.0.0
  description: 索克生活小艾服务API规范
paths:
  /api/v1/chat:
    post:
      summary: 聊天对话接口
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  description: 用户消息
                conversation_id:
                  type: string
                  description: 对话ID
      responses:
        '200':
          description: 成功响应
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                    description: AI响应
                  conversation_id:
                    type: string
                    description: 对话ID
```

### 创建契约测试

在`tests/`目录中创建一个新的测试文件，命名为`<consumer>-<provider>-contract.test.js`：

例如，新建`tests/xiaoai-rag-contract.test.js`：

```javascript
const { ContractTest } = require('../contract-test-runner');

describe('小艾服务和RAG服务契约测试', () => {
  const contractTest = new ContractTest({
    consumer: 'xiaoai-service',
    provider: 'rag-service',
    consumerEndpoint: '/api/v1/chat',
    providerEndpoint: '/api/v1/query',
  });

  beforeAll(async () => {
    await contractTest.setup();
  });

  test('小艾服务查询请求应符合RAG服务查询接口规范', async () => {
    await contractTest.validateRequest(
      // 示例请求对象
      {
        message: '中医四诊法的主要内容是什么？',
        conversation_id: '12345'
      }, 
      // 请求字段映射
      {
        'message': 'query',
        'conversation_id': 'session_id'
      }
    );
  });

  test('RAG服务响应应符合小艾服务期望格式', async () => {
    await contractTest.validateResponse(
      // 示例响应对象
      {
        results: [
          { content: '中医四诊法包括望、闻、问、切四种诊断方法。' }
        ],
        session_id: '12345'
      },
      // 响应字段映射
      {
        'results[0].content': 'response',
        'session_id': 'conversation_id'
      }
    );
  });
});
```

### 运行测试

```bash
# 安装依赖
npm install

# 运行所有契约测试
npm test

# 运行特定契约测试
npm test -- tests/xiaoai-rag-contract.test.js
```

## 自动化集成

在CI/CD流程中添加契约测试：

```yaml
# .github/workflows/ci-cd.yml
jobs:
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      - name: Install dependencies
        run: cd services/shared/api-contract-tests && npm install
      - name: Run API contract tests
        run: cd services/shared/api-contract-tests && npm test
```

## 最佳实践

1. **先定义契约**: 在开发API前，先定义OpenAPI规范，使开发基于契约进行
2. **保持版本控制**: 为API规范添加版本控制，避免意外的破坏性变更
3. **自动化验证**: 通过CI/CD自动运行契约测试，确保兼容性
4. **变更管理**: 当需要更改API时，先更新契约并确保消费者知晓
5. **测试边界条件**: 不仅测试正常流程，还要测试异常情况和边界条件