# Fastify Schema编写指南

本指南提供了如何为索克生活知识图谱服务编写Fastify路由Schema的标准方法。良好定义的Schema不仅能生成高质量的API文档，还能自动进行请求和响应验证。

## 目录

- [基本结构](#基本结构)
- [通用Schema定义](#通用Schema定义)
- [路由定义最佳实践](#路由定义最佳实践)
- [请求验证](#请求验证)
- [响应定义](#响应定义)
- [常见错误响应](#常见错误响应)
- [示例和描述](#示例和描述)
- [安全性定义](#安全性定义)
- [完整示例](#完整示例)

## 基本结构

每个路由的Schema应包含以下部分：

```typescript
{
  description: '端点描述',
  tags: ['标签分类'],
  params: {
    // URL参数定义
  },
  querystring: {
    // 查询参数定义
  },
  body: {
    // 请求体定义
  },
  response: {
    // 各状态码的响应定义
  },
  security: [
    // 安全性定义
  ]
}
```

## 通用Schema定义

为了保持一致性，应使用以下通用Schema定义：

```typescript
// 成功响应基础模式
const successResponseSchema = {
  type: 'object',
  properties: {
    success: { type: 'boolean', example: true },
    message: { type: 'string' },
    timestamp: { type: 'string', format: 'date-time' }
  }
};

// 数据响应模式
const dataResponseSchema = {
  type: 'object',
  properties: {
    success: { type: 'boolean', example: true },
    message: { type: 'string' },
    data: { type: 'object' },
    timestamp: { type: 'string', format: 'date-time' }
  }
};

// 错误响应模式
const errorResponseSchema = {
  type: 'object',
  properties: {
    success: { type: 'boolean', example: false },
    message: { type: 'string' },
    error: { type: 'string' },
    statusCode: { type: 'integer' },
    timestamp: { type: 'string', format: 'date-time' }
  }
};

// 分页响应模式
const paginatedResponseSchema = {
  type: 'object',
  properties: {
    success: { type: 'boolean', example: true },
    message: { type: 'string' },
    data: {
      type: 'object',
      properties: {
        items: { 
          type: 'array',
          items: { type: 'object' }
        },
        pagination: {
          type: 'object',
          properties: {
            totalItems: { type: 'integer' },
            totalPages: { type: 'integer' },
            currentPage: { type: 'integer' },
            itemsPerPage: { type: 'integer' }
          }
        }
      }
    },
    timestamp: { type: 'string', format: 'date-time' }
  }
};
```

## 路由定义最佳实践

### 路由描述

- 使用简洁但描述性的文本
- 使用动词开头（获取、创建、更新、删除等）
- 说明端点的主要功能

```typescript
description: '获取知识图谱节点列表',
```

### 标签分类

- 使用预定义的标签集合
  - 知识图谱
  - 可视化
  - 搜索
  - 系统

```typescript
tags: ['知识图谱'],
```

## 请求验证

### URL参数定义

```typescript
params: {
  type: 'object',
  required: ['id'],
  properties: {
    id: { 
      type: 'string', 
      description: '节点ID' 
    }
  }
}
```

### 查询参数定义

```typescript
querystring: {
  type: 'object',
  properties: {
    page: { 
      type: 'integer', 
      minimum: 1, 
      default: 1,
      description: '页码' 
    },
    limit: { 
      type: 'integer', 
      minimum: 1, 
      maximum: 100, 
      default: 20,
      description: '每页数量' 
    }
  }
}
```

### 请求体定义

```typescript
body: {
  type: 'object',
  required: ['type', 'properties'],
  properties: {
    type: { 
      type: 'string', 
      description: '节点类型',
      example: 'TCMHerb'
    },
    labels: { 
      type: 'array', 
      items: { type: 'string' },
      description: '节点标签',
      example: ['中药', '植物类']
    },
    properties: {
      type: 'object',
      additionalProperties: true,
      description: '节点属性',
      example: {
        name: '人参',
        pinyin: 'renshen',
        description: '补气补血药'
      }
    }
  }
}
```

## 响应定义

为每个HTTP状态码定义适当的响应：

```typescript
response: {
  200: {
    description: '成功获取节点',
    ...dataResponseSchema,
    properties: {
      ...dataResponseSchema.properties,
      data: {
        type: 'object',
        properties: {
          node: nodeSchema,
          relationships: {
            type: 'array',
            items: relationshipSchema,
            description: '关联的关系'
          }
        }
      }
    }
  },
  404: {
    description: '节点不存在',
    ...errorResponseSchema
  },
  500: {
    description: '服务器错误',
    ...errorResponseSchema
  }
}
```

## 常见错误响应

包含以下常见错误状态码的响应：

- 400 - 请求参数错误
- 401 - 未授权
- 403 - 禁止访问
- 404 - 资源不存在
- 409 - 资源冲突
- 500 - 服务器错误

## 示例和描述

为所有参数和响应添加描述和示例值：

```typescript
properties: {
  name: { 
    type: 'string', 
    description: '中药名称',
    example: '人参'
  }
}
```

## 安全性定义

对需要认证的端点添加安全性定义：

```typescript
security: [
  { bearerAuth: [] }
]
```

## 完整示例

以下是一个完整的路由Schema定义示例：

```typescript
fastify.get('/nodes/:id', {
  schema: {
    description: '获取特定知识图谱节点',
    tags: ['知识图谱'],
    params: {
      type: 'object',
      required: ['id'],
      properties: {
        id: { 
          type: 'string', 
          description: '节点ID' 
        }
      }
    },
    querystring: {
      type: 'object',
      properties: {
        includeRelationships: { 
          type: 'boolean', 
          default: false,
          description: '是否包含关系' 
        },
        maxDepth: { 
          type: 'integer', 
          minimum: 1, 
          maximum: 5, 
          default: 1,
          description: '包含关系时的最大深度' 
        }
      }
    },
    response: {
      200: {
        description: '成功获取节点',
        ...dataResponseSchema,
        properties: {
          ...dataResponseSchema.properties,
          data: {
            type: 'object',
            properties: {
              node: nodeSchema,
              relationships: {
                type: 'array',
                items: relationshipSchema,
                description: '关联的关系（如果请求包含关系）'
              }
            }
          }
        }
      },
      404: {
        description: '节点不存在',
        ...errorResponseSchema
      },
      500: {
        description: '服务器错误',
        ...errorResponseSchema
      }
    }
  },
  handler: async (request, reply) => {
    // 处理函数
  }
});
```

## 附加参考

有关更多信息，请参阅：

- [Fastify Validation and Serialization](https://www.fastify.io/docs/latest/Reference/Validation-and-Serialization/)
- [JSON Schema](https://json-schema.org/understanding-json-schema/)