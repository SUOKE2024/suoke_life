# 知识库服务API文档

本文档描述了知识库服务提供的API接口。知识库服务提供RESTful API，所有接口均以`/api/v1`为前缀。

## 通用信息

### 基础URL
- 开发环境：`https://dev.api.suoke.life/kb/api/v1`
- 预发布环境：`https://staging.api.suoke.life/kb/api/v1`
- 生产环境：`https://api.suoke.life/kb/api/v1`

### 认证
所有API请求必须包含以下HTTP头：
```
Authorization: Bearer <access_token>
```

### 响应格式
所有API响应均使用JSON格式，标准响应结构如下：
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

错误响应结构：
```json
{
  "success": false,
  "code": 400,
  "message": "请求参数错误",
  "errors": [
    {
      "field": "title",
      "message": "标题不能为空"
    }
  ]
}
```

### 状态码
- 200: 成功
- 201: 创建成功
- 400: 客户端错误
- 401: 认证失败
- 403: 权限不足
- 404: 资源不存在
- 409: 资源冲突
- 422: 验证失败
- 500: 服务器错误

## API端点

### 健康检查

#### 获取服务健康状态
```
GET /health
```

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "服务正常",
  "data": {
    "status": "ok",
    "version": "2024.04.06-abc123",
    "db_connected": true,
    "vector_store_connected": true,
    "uptime": 1234567
  }
}
```

### 文档管理

#### 获取文档列表
```
GET /documents
```

**查询参数：**
- `page`: 页码 (默认: 1)
- `limit`: 每页条数 (默认: 20, 最大: 100)
- `category`: 按分类过滤
- `tags`: 按标签过滤，多个标签使用逗号分隔
- `sort`: 排序字段 (默认: created_at)
- `order`: 排序方向 (asc, desc, 默认: desc)

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "获取文档列表成功",
  "data": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "id": "doc123",
        "title": "中医体质辨识基础",
        "summary": "介绍九种体质的基本特征和辨识方法",
        "category": "中医理论",
        "tags": ["体质辨识", "中医基础"],
        "created_at": "2024-04-01T08:00:00Z",
        "updated_at": "2024-04-02T10:30:00Z"
      },
      // ...更多文档
    ]
  }
}
```

#### 获取文档详情
```
GET /documents/{id}
```

**路径参数：**
- `id`: 文档ID

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "获取文档成功",
  "data": {
    "id": "doc123",
    "title": "中医体质辨识基础",
    "content": "中医体质学说是中医学对人体生命本质的认识...",
    "summary": "介绍九种体质的基本特征和辨识方法",
    "category": "中医理论",
    "tags": ["体质辨识", "中医基础"],
    "references": [
      {
        "title": "《中医体质学》",
        "author": "王琦",
        "year": 2005
      }
    ],
    "related_documents": ["doc456", "doc789"],
    "version": 2,
    "created_at": "2024-04-01T08:00:00Z",
    "updated_at": "2024-04-02T10:30:00Z"
  }
}
```

#### 创建文档
```
POST /documents
```

**请求Body：**
```json
{
  "title": "四季养生之春季养生",
  "content": "春季养生应当以养肝为主，饮食宜甘少酸...",
  "summary": "介绍春季养生的基本原则和方法",
  "category": "养生保健",
  "tags": ["四季养生", "春季", "养肝"],
  "references": [
    {
      "title": "《黄帝内经》",
      "section": "四气调神大论"
    }
  ]
}
```

**响应示例：**
```json
{
  "success": true,
  "code": 201,
  "message": "创建文档成功",
  "data": {
    "id": "doc456",
    "title": "四季养生之春季养生",
    "created_at": "2024-04-06T14:22:10Z",
    "updated_at": "2024-04-06T14:22:10Z"
  }
}
```

#### 更新文档
```
PUT /documents/{id}
```

**路径参数：**
- `id`: 文档ID

**请求Body：**
```json
{
  "title": "四季养生之春季养生指南",
  "content": "春季养生应当以养肝为主，饮食宜甘少酸...",
  "summary": "全面介绍春季养生的基本原则和实用方法",
  "category": "养生保健",
  "tags": ["四季养生", "春季", "养肝", "实用指南"]
}
```

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "更新文档成功",
  "data": {
    "id": "doc456",
    "version": 2,
    "updated_at": "2024-04-06T16:45:30Z"
  }
}
```

#### 删除文档
```
DELETE /documents/{id}
```

**路径参数：**
- `id`: 文档ID

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "删除文档成功",
  "data": null
}
```

### 搜索功能

#### 关键词搜索
```
GET /documents/search
```

**查询参数：**
- `q`: 搜索关键词
- `page`: 页码 (默认: 1)
- `limit`: 每页条数 (默认: 20, 最大: 100)
- `category`: 按分类过滤
- `tags`: 按标签过滤，多个标签使用逗号分隔

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "搜索成功",
  "data": {
    "total": 15,
    "page": 1,
    "limit": 20,
    "query": "春季养生",
    "items": [
      {
        "id": "doc456",
        "title": "四季养生之春季养生指南",
        "summary": "全面介绍春季养生的基本原则和实用方法",
        "category": "养生保健",
        "tags": ["四季养生", "春季", "养肝", "实用指南"],
        "highlight": {
          "title": "四季养生之<em>春季养生</em>指南",
          "content": "...<em>春季养生</em>应当以养肝为主..."
        },
        "score": 0.89
      },
      // ...更多搜索结果
    ]
  }
}
```

#### 语义搜索
```
GET /documents/semantic-search
```

**查询参数：**
- `q`: 搜索问题或描述
- `page`: 页码 (默认: 1)
- `limit`: 每页条数 (默认: 20, 最大: 50)
- `threshold`: 相似度阈值 (0-1, 默认: 0.7)
- `category`: 按分类过滤
- `tags`: 按标签过滤，多个标签使用逗号分隔

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "语义搜索成功",
  "data": {
    "total": 8,
    "page": 1,
    "limit": 20,
    "query": "如何预防春季肝火旺盛",
    "items": [
      {
        "id": "doc456",
        "title": "四季养生之春季养生指南",
        "summary": "全面介绍春季养生的基本原则和实用方法",
        "category": "养生保健",
        "tags": ["四季养生", "春季", "养肝", "实用指南"],
        "similarity": 0.92
      },
      {
        "id": "doc789",
        "title": "中医肝火调理方法",
        "summary": "详解肝火旺盛的症状和调理方法",
        "category": "中医理论",
        "tags": ["肝火", "情志调节", "中医调理"],
        "similarity": 0.85
      },
      // ...更多搜索结果
    ]
  }
}
```

### 分类与标签管理

#### 获取分类列表
```
GET /categories
```

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "获取分类列表成功",
  "data": [
    {
      "id": "cat1",
      "name": "中医理论",
      "description": "中医基础理论和概念",
      "document_count": 120
    },
    {
      "id": "cat2",
      "name": "养生保健",
      "description": "日常养生和保健知识",
      "document_count": 95
    },
    // ...更多分类
  ]
}
```

#### 获取标签列表
```
GET /tags
```

**查询参数：**
- `q`: 标签名称搜索 (可选)
- `limit`: 返回数量 (默认: 50, 最大: 200)

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "获取标签列表成功",
  "data": [
    {
      "id": "tag1",
      "name": "四季养生",
      "document_count": 45
    },
    {
      "id": "tag2",
      "name": "春季",
      "document_count": 18
    },
    // ...更多标签
  ]
}
```

## 错误代码

| 错误代码 | 描述 |
|---------|------|
| 400001 | 请求参数验证失败 |
| 400002 | 请求体格式错误 |
| 401001 | 缺少授权令牌 |
| 401002 | 授权令牌无效 |
| 403001 | 权限不足 |
| 404001 | 文档不存在 |
| 404002 | 分类不存在 |
| 409001 | 文档标题已存在 |
| 500001 | 数据库错误 |
| 500002 | 向量存储错误 |

## 使用示例

### 基于语义搜索的实体关系查询示例

```shell
# 查询关于"气虚体质与食疗方案"的相关知识
curl -X GET "https://api.suoke.life/kb/api/v1/documents/semantic-search?q=气虚体质的人应该如何调整饮食&threshold=0.75" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 创建文档示例

```shell
curl -X POST "https://api.suoke.life/kb/api/v1/documents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "气虚体质食疗指南",
    "content": "气虚体质的人常见症状包括...",
    "summary": "针对气虚体质人群的饮食调理方案",
    "category": "中医体质调理",
    "tags": ["气虚体质", "食疗", "体质调理"]
  }'
```

## 版本历史

| 版本 | 日期 | 变更描述 |
|-----|------|---------|
| 1.0.0 | 2024-04-07 | 初始版本 |

## 下一步计划

1. 增加批量文档操作API
2. 添加文档版本控制功能
3. 实现文档关系管理API
4. 集成Swagger/OpenAPI文档系统