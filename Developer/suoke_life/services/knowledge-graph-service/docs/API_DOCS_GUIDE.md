# 索克生活知识图谱服务API文档使用指南

本指南提供了如何使用和理解索克生活知识图谱服务的API文档。API文档是使用Swagger/OpenAPI规范生成的，提供了交互式界面，可以直接测试API端点。

## 目录

- [访问API文档](#访问API文档)
- [API文档结构](#API文档结构)
- [使用API文档进行测试](#使用API文档进行测试)
- [常见问题](#常见问题)
- [API鉴权](#API鉴权)
- [开发者进阶](#开发者进阶)

## 访问API文档

### 本地开发环境

API文档可通过以下URL访问：

```
http://localhost:3000/api-docs
```

### 测试环境

```
http://test.api.suoke.life/knowledge-graph/api-docs
```

### 生产环境

```
https://api.suoke.life/knowledge-graph/api-docs
```

> 注意：生产环境的API文档受到基本认证保护，需要用户名和密码。请联系管理员获取访问凭据。

## API文档结构

API文档按以下方式组织：

1. **顶部导航栏**：包含版本信息、服务名称和搜索功能
2. **左侧边栏**：API端点分组
   - 知识图谱：图谱节点和关系管理
   - 可视化：图谱可视化相关接口
   - 搜索：知识搜索相关接口
   - 系统：健康检查等系统接口
3. **主内容区**：显示所选端点的详细文档
4. **模型定义**：底部显示所有数据模型的定义

## 使用API文档进行测试

API文档提供了交互式测试功能，可直接从浏览器发送API请求：

1. 选择要测试的端点
2. 点击"Try it out"按钮
3. 填写必要的参数
4. 点击"Execute"按钮发送请求
5. 查看响应结果

### 示例：获取所有节点

1. 导航到`GET /api/v1/graph/nodes`端点
2. 点击"Try it out"
3. 根据需要设置分页和筛选参数
4. 点击"Execute"
5. 查看返回的节点列表

## 常见问题

### 如何使用筛选条件？

大多数列表端点支持以下筛选参数：

- **page**: 页码，从1开始
- **limit**: 每页返回的记录数
- **sortBy**: 排序字段
- **sortDirection**: 排序方向，`asc`或`desc`
- **nodeTypes[]**: 按节点类型筛选（可指定多个）
- **domains[]**: 按领域筛选（可指定多个）

注意：数组类型参数可以重复指定，例如：`nodeTypes[]=TCMHerb&nodeTypes[]=Disease`

### 错误响应格式

所有错误响应使用统一格式：

```json
{
  "success": false,
  "message": "错误描述",
  "error": "错误类型",
  "statusCode": 400,
  "timestamp": "2023-12-25T10:30:00.000Z"
}
```

## API鉴权

### 认证方式

需要授权的端点使用JWT Bearer令牌认证：

1. 先通过认证服务获取JWT令牌
2. 在API请求的"Authorization"头中包含令牌：`Bearer <your_token>`

在Swagger UI中测试受保护端点：

1. 点击右上角的"Authorize"按钮
2. 在弹出的对话框中输入Bearer令牌（格式：`Bearer <your_token>`）
3. 点击"Authorize"按钮

### 权限级别

API操作需要不同级别的权限：

- **读取操作**：基本用户权限
- **创建/更新操作**：编辑者权限
- **删除操作**：管理员权限

## 开发者进阶

### 代码中添加Schema文档

开发新API端点时，按照以下模式添加Schema定义：

```typescript
fastify.get('/example', {
  schema: {
    description: '端点描述',
    tags: ['分类标签'],
    querystring: {
      // 查询参数定义
    },
    response: {
      200: {
        description: '成功响应描述',
        // 响应模式定义
      }
    }
  },
  handler: async (request, reply) => {
    // 处理逻辑
  }
});
```

更多详细信息，请参阅[Fastify Schema指南](./FASTIFY_SCHEMA_GUIDE.md)。

### 可重用模型

常用模型已定义为可重用变量，例如：

- `nodeSchema`: 知识图谱节点模型
- `relationshipSchema`: 关系模型
- `dataResponseSchema`: 标准数据响应
- `errorResponseSchema`: 标准错误响应
- `paginatedResponseSchema`: 分页响应

使用这些模型可保持API响应的一致性。

### 生成OpenAPI规范文件

可使用以下命令导出完整的OpenAPI规范文件：

```bash
npm run generate-openapi
```

这将在`docs/openapi`目录下生成OpenAPI规范文件，可用于客户端代码生成或导入其他API工具。