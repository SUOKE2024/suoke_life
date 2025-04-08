# 知识图谱API服务使用指南

知识图谱API服务提供了一组RESTful接口，用于访问和操作知识图谱数据。本文档详细介绍了API的设计、实现和使用方法，以及不同类型的查询和操作。

## API概览

知识图谱API服务包含以下主要端点：

| 端点类别 | 基础路径 | 功能描述 |
|--------|---------|---------|
| 节点API | `/api/v1/nodes` | 用于节点的创建、查询、更新和删除 |
| 关系API | `/api/v1/relationships` | 用于关系的创建、查询、更新和删除 |
| 查询API | `/api/v1/query` | 用于复杂查询、路径搜索和模式匹配 |
| 向量API | `/api/v1/vectors` | 用于向量存储和相似度搜索 |
| 健康检查 | `/health` | 服务健康状态检查 |
| 指标 | `/metrics` | Prometheus格式的服务指标 |

所有API端点都支持JSON格式的请求和响应，使用标准的HTTP方法（GET、POST、PUT、DELETE等）进行操作。认证使用JWT令牌，通过Authorization头部传递。

## 节点API

节点API用于管理知识图谱中的节点实体。

### 创建节点

```
POST /api/v1/nodes
```

**请求体**:

```json
{
  "labels": ["Herb"],
  "properties": {
    "name": "黄芪",
    "pinyin": "huáng qí",
    "description": "补气固表，利水消肿，托毒排脓，生肌",
    "latin_name": "Astragalus membranaceus"
  }
}
```

**响应**:

```json
{
  "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "labels": ["Herb"],
  "properties": {
    "name": "黄芪",
    "pinyin": "huáng qí",
    "description": "补气固表，利水消肿，托毒排脓，生肌",
    "latin_name": "Astragalus membranaceus"
  },
  "created_at": "2023-08-15T12:34:56Z"
}
```

### 批量创建节点

```
POST /api/v1/nodes/batch
```

**请求体**:

```json
{
  "nodes": [
    {
      "labels": ["Herb"],
      "properties": {
        "name": "党参",
        "pinyin": "dǎng shēn"
      }
    },
    {
      "labels": ["Herb"],
      "properties": {
        "name": "白术",
        "pinyin": "bái zhú"
      }
    }
  ]
}
```

**响应**:

```json
{
  "count": 2,
  "nodes": [
    {
      "id": "2b3c4d5e-6f7g-8h9i-0j1k-2l3m4n5o6p7q",
      "labels": ["Herb"],
      "properties": {
        "name": "党参",
        "pinyin": "dǎng shēn"
      },
      "created_at": "2023-08-15T12:34:57Z"
    },
    {
      "id": "3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
      "labels": ["Herb"],
      "properties": {
        "name": "白术",
        "pinyin": "bái zhú"
      },
      "created_at": "2023-08-15T12:34:57Z"
    }
  ]
}
```

### 根据ID获取节点

```
GET /api/v1/nodes/{id}
```

**响应**:

```json
{
  "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "labels": ["Herb"],
  "properties": {
    "name": "黄芪",
    "pinyin": "huáng qí",
    "description": "补气固表，利水消肿，托毒排脓，生肌",
    "latin_name": "Astragalus membranaceus"
  },
  "created_at": "2023-08-15T12:34:56Z",
  "updated_at": "2023-08-15T12:34:56Z"
}
```

### 根据属性查询节点

```
GET /api/v1/nodes/search?label=Herb&property=name&value=黄芪
```

**响应**:

```json
{
  "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "labels": ["Herb"],
  "properties": {
    "name": "黄芪",
    "pinyin": "huáng qí",
    "description": "补气固表，利水消肿，托毒排脓，生肌",
    "latin_name": "Astragalus membranaceus"
  },
  "created_at": "2023-08-15T12:34:56Z",
  "updated_at": "2023-08-15T12:34:56Z"
}
```

### 高级节点搜索

```
POST /api/v1/nodes/advanced-search
```

**请求体**:

```json
{
  "label": "Herb",
  "properties": {
    "name": "黄*",
    "category": "补气药"
  },
  "limit": 10,
  "offset": 0,
  "order_by": "name",
  "order_dir": "asc"
}
```

**响应**:

```json
{
  "total": 25,
  "limit": 10,
  "offset": 0,
  "nodes": [
    {
      "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪",
        "pinyin": "huáng qí",
        "category": "补气药"
      }
    },
    {
      "id": "4d5e6f7g-8h9i-0j1k-2l3m-4n5o6p7q8r9s",
      "labels": ["Herb"],
      "properties": {
        "name": "黄精",
        "pinyin": "huáng jīng",
        "category": "补气药"
      }
    }
    // 更多节点...
  ]
}
```

### 更新节点

```
PUT /api/v1/nodes/{id}
```

**请求体**:

```json
{
  "properties": {
    "description": "补气固表，利水消肿，托毒排脓，生肌，强壮免疫系统",
    "english_name": "Astragalus root"
  }
}
```

**响应**:

```json
{
  "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "labels": ["Herb"],
  "properties": {
    "name": "黄芪",
    "pinyin": "huáng qí",
    "description": "补气固表，利水消肿，托毒排脓，生肌，强壮免疫系统",
    "latin_name": "Astragalus membranaceus",
    "english_name": "Astragalus root"
  },
  "updated_at": "2023-08-15T14:56:78Z"
}
```

### 删除节点

```
DELETE /api/v1/nodes/{id}
```

**响应**:

```json
{
  "success": true,
  "message": "节点删除成功"
}
```

## 关系API

关系API用于管理知识图谱中节点之间的关系。

### 创建关系

```
POST /api/v1/relationships
```

**请求体**:

```json
{
  "source_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "target_id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "type": "TREATS",
  "properties": {
    "confidence": 0.95,
    "source": "中国药典2020版"
  }
}
```

**响应**:

```json
{
  "id": "9i0j1k2l-3m4n-5o6p-7q8r-9s0t1u2v3w4x",
  "source_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "target_id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "type": "TREATS",
  "properties": {
    "confidence": 0.95,
    "source": "中国药典2020版"
  },
  "created_at": "2023-08-15T15:67:89Z"
}
```

### 批量创建关系

```
POST /api/v1/relationships/batch
```

**请求体**:

```json
{
  "relationships": [
    {
      "source_id": "formula-123",
      "target_id": "herb-456",
      "type": "CONTAINS",
      "properties": {
        "amount": "10g"
      }
    },
    {
      "source_id": "formula-123",
      "target_id": "herb-789",
      "type": "CONTAINS",
      "properties": {
        "amount": "15g"
      }
    }
  ]
}
```

**响应**:

```json
{
  "count": 2,
  "relationships": [
    {
      "id": "rel-001",
      "source_id": "formula-123",
      "target_id": "herb-456",
      "type": "CONTAINS",
      "properties": {
        "amount": "10g"
      }
    },
    {
      "id": "rel-002",
      "source_id": "formula-123",
      "target_id": "herb-789",
      "type": "CONTAINS",
      "properties": {
        "amount": "15g"
      }
    }
  ]
}
```

### 根据ID获取关系

```
GET /api/v1/relationships/{id}
```

**响应**:

```json
{
  "id": "9i0j1k2l-3m4n-5o6p-7q8r-9s0t1u2v3w4x",
  "source_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "target_id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "type": "TREATS",
  "properties": {
    "confidence": 0.95,
    "source": "中国药典2020版"
  },
  "created_at": "2023-08-15T15:67:89Z",
  "updated_at": "2023-08-15T15:67:89Z"
}
```

### 查询节点的出向关系

```
GET /api/v1/nodes/{id}/relationships/outgoing?type=TREATS
```

**响应**:

```json
{
  "count": 5,
  "relationships": [
    {
      "id": "rel-003",
      "source_id": "herb-123",
      "target_id": "symptom-001",
      "type": "TREATS",
      "properties": {
        "effectiveness": "高",
        "source": "中医内科学"
      }
    },
    {
      "id": "rel-004",
      "source_id": "herb-123",
      "target_id": "symptom-002",
      "type": "TREATS",
      "properties": {
        "effectiveness": "中",
        "source": "中医内科学"
      }
    }
    // 更多关系...
  ]
}
```

### 查询两个节点之间的关系

```
GET /api/v1/relationships/between?source={source_id}&target={target_id}&type=CONTAINS
```

**响应**:

```json
{
  "count": 1,
  "relationships": [
    {
      "id": "rel-005",
      "source_id": "formula-123",
      "target_id": "herb-456",
      "type": "CONTAINS",
      "properties": {
        "amount": "10g"
      }
    }
  ]
}
```

### 更新关系

```
PUT /api/v1/relationships/{id}
```

**请求体**:

```json
{
  "properties": {
    "confidence": 0.98,
    "updated_by": "system"
  }
}
```

**响应**:

```json
{
  "id": "9i0j1k2l-3m4n-5o6p-7q8r-9s0t1u2v3w4x",
  "source_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "target_id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "type": "TREATS",
  "properties": {
    "confidence": 0.98,
    "source": "中国药典2020版",
    "updated_by": "system"
  },
  "updated_at": "2023-08-15T16:78:90Z"
}
```

### 删除关系

```
DELETE /api/v1/relationships/{id}
```

**响应**:

```json
{
  "success": true,
  "message": "关系删除成功"
}
```

## 查询API

查询API提供了强大的图谱查询功能，包括自定义Cypher查询、路径搜索和模式匹配。

### 执行Cypher查询

```
POST /api/v1/query/cypher
```

**请求体**:

```json
{
  "query": "MATCH (h:Herb)-[:TREATS]->(s:Symptom) WHERE h.name = $name RETURN s.name AS symptom, count(*) AS count ORDER BY count DESC LIMIT 10",
  "parameters": {
    "name": "黄芪"
  }
}
```

**响应**:

```json
{
  "results": [
    {
      "symptom": "气虚乏力",
      "count": 12
    },
    {
      "symptom": "自汗",
      "count": 8
    },
    {
      "symptom": "水肿",
      "count": 7
    },
    // 更多结果...
  ],
  "execution_time_ms": 15
}
```

### 查找最短路径

```
POST /api/v1/query/shortest-path
```

**请求体**:

```json
{
  "source_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "target_id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "relationship_types": ["TREATS", "SIMILAR_TO"],
  "max_depth": 3
}
```

**响应**:

```json
{
  "path": {
    "nodes": [
      {
        "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
        "labels": ["Herb"],
        "properties": {
          "name": "黄芪"
        }
      },
      {
        "id": "mid-node-id",
        "labels": ["Symptom"],
        "properties": {
          "name": "气虚乏力"
        }
      },
      {
        "id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
        "labels": ["Herb"],
        "properties": {
          "name": "人参"
        }
      }
    ],
    "relationships": [
      {
        "id": "rel-001",
        "source_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
        "target_id": "mid-node-id",
        "type": "TREATS"
      },
      {
        "id": "rel-002",
        "source_id": "5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
        "target_id": "mid-node-id",
        "type": "TREATS"
      }
    ],
    "length": 2
  }
}
```

### 查找所有路径

```
POST /api/v1/query/all-paths
```

**请求体**:

```json
{
  "source_id": "formula-123",
  "target_id": "symptom-001",
  "relationship_types": ["CONTAINS", "TREATS"],
  "max_depth": 3
}
```

**响应**:

```json
{
  "count": 2,
  "paths": [
    // 路径1
    {
      "nodes": [...],
      "relationships": [...],
      "length": 2
    },
    // 路径2
    {
      "nodes": [...],
      "relationships": [...],
      "length": 3
    }
  ]
}
```

### 模式匹配查询

```
POST /api/v1/query/pattern
```

**请求体**:

```json
{
  "pattern": "(f:Formula)-[:CONTAINS]->(h:Herb)-[:TREATS]->(s:Symptom)",
  "parameters": {
    "formula_name": "四君子汤"
  },
  "where_clause": "f.name = $formula_name",
  "return_clause": "f.name AS formula, h.name AS herb, s.name AS symptom",
  "limit": 20
}
```

**响应**:

```json
{
  "results": [
    {
      "formula": "四君子汤",
      "herb": "人参",
      "symptom": "气虚乏力"
    },
    {
      "formula": "四君子汤",
      "herb": "白术",
      "symptom": "脾虚食少"
    }
    // 更多结果...
  ],
  "execution_time_ms": 25
}
```

### 图谱聚合查询

```
POST /api/v1/query/aggregate
```

**请求体**:

```json
{
  "label": "Herb",
  "group_by": "category",
  "aggregations": {
    "herb_count": "COUNT(*)",
    "avg_effectiveness": "AVG(effectiveness)"
  }
}
```

**响应**:

```json
{
  "results": [
    {
      "category": "补气药",
      "herb_count": 45,
      "avg_effectiveness": 0.85
    },
    {
      "category": "补血药",
      "herb_count": 32,
      "avg_effectiveness": 0.78
    }
    // 更多结果...
  ]
}
```

### 全文搜索

```
POST /api/v1/query/fulltext-search
```

**请求体**:

```json
{
  "label": "Herb",
  "field": "description",
  "search_term": "补气 固表",
  "limit": 10
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪",
        "description": "补气固表，利水消肿，托毒排脓，生肌"
      },
      "score": 0.95
    },
    // 更多结果...
  ]
}
```

## 向量API

向量API用于向量存储和相似度搜索，支持基于语义的查询。

### 添加向量

```
POST /api/v1/vectors
```

**请求体**:

```json
{
  "node_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  "field": "description_vector"
}
```

**响应**:

```json
{
  "success": true,
  "node_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "field": "description_vector",
  "dimensions": 8
}
```

### 批量添加向量

```
POST /api/v1/vectors/batch
```

**请求体**:

```json
{
  "vectors": [
    {
      "node_id": "node-1",
      "vector": [0.1, 0.2, 0.3, 0.4],
      "field": "description_vector"
    },
    {
      "node_id": "node-2",
      "vector": [0.5, 0.6, 0.7, 0.8],
      "field": "description_vector"
    }
  ]
}
```

**响应**:

```json
{
  "success": true,
  "count": 2
}
```

### 相似度搜索

```
POST /api/v1/vectors/similar
```

**请求体**:

```json
{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  "field": "description_vector",
  "limit": 10
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪"
      },
      "score": 0.98
    },
    {
      "id": "other-node-id",
      "labels": ["Herb"],
      "properties": {
        "name": "白术"
      },
      "score": 0.85
    }
    // 更多结果...
  ]
}
```

### 带标签的相似度搜索

```
POST /api/v1/vectors/similar-with-label
```

**请求体**:

```json
{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  "label": "Herb",
  "field": "description_vector",
  "limit": 10
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪"
      },
      "score": 0.98
    }
    // 更多结果...
  ]
}
```

### 混合搜索

```
POST /api/v1/vectors/hybrid-search
```

**请求体**:

```json
{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  "label": "Herb",
  "field": "description_vector",
  "filters": {
    "category": "补气药"
  },
  "limit": 5
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪",
        "category": "补气药"
      },
      "score": 0.98
    }
    // 更多结果...
  ]
}
```

## API认证与安全

所有API端点都需要通过JWT令牌进行认证，除了健康检查和公共文档端点。

### 登录获取令牌

```
POST /api/v1/auth/login
```

**请求体**:

```json
{
  "username": "admin",
  "password": "your-secure-password"
}
```

**响应**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### 使用令牌访问API

在所有API请求的头部添加Authorization:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 刷新令牌

```
POST /api/v1/auth/refresh
```

**请求头**:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

## 错误处理

API使用标准的HTTP状态码表示请求结果：

- 200 OK: 请求成功
- 201 Created: 资源创建成功
- 400 Bad Request: 请求参数错误
- 401 Unauthorized: 身份验证失败
- 403 Forbidden: 权限不足
- 404 Not Found: 资源未找到
- 409 Conflict: 资源冲突
- 500 Internal Server Error: 服务器内部错误

所有错误响应都会包含详细的错误信息：

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "找不到指定的节点",
    "details": "节点ID 'non-existent-id' 不存在",
    "request_id": "req-1234567890"
  }
}
```

## API限流

为了保护服务，API实施了请求限流：

- 基本认证用户: 100请求/分钟
- JWT认证用户: 1000请求/分钟
- 管理员用户: 5000请求/分钟

超过限制时，将返回429 Too Many Requests状态码：

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求频率超出限制",
    "details": "请等待60秒后再试",
    "reset_at": "2023-08-15T12:35:45Z"
  }
}
```

## API客户端示例

### Go客户端示例

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

func main() {
    // 创建节点
    node := map[string]interface{}{
        "labels": []string{"Herb"},
        "properties": map[string]interface{}{
            "name": "黄芪",
            "pinyin": "huáng qí",
        },
    }
    
    jsonData, _ := json.Marshal(node)
    req, _ := http.NewRequest("POST", "https://kg-api.suoke.life/api/v1/nodes", bytes.NewBuffer(jsonData))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer YOUR_JWT_TOKEN")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        fmt.Printf("请求失败: %v\n", err)
        return
    }
    defer resp.Body.Close()
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Printf("创建节点成功: %v\n", result)
}
```

### Python客户端示例

```python
import requests
import json

# 设置API端点和认证
api_url = 'https://kg-api.suoke.life/api/v1'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
}

# 创建节点
node_data = {
    'labels': ['Herb'],
    'properties': {
        'name': '黄芪',
        'pinyin': 'huáng qí'
    }
}

response = requests.post(f'{api_url}/nodes', headers=headers, json=node_data)
if response.status_code == 201:
    result = response.json()
    node_id = result['id']
    print(f'创建节点成功，ID: {node_id}')
else:
    print(f'创建节点失败: {response.text}')

# 执行Cypher查询
query_data = {
    'query': 'MATCH (h:Herb) WHERE h.name = $name RETURN h',
    'parameters': {
        'name': '黄芪'
    }
}

response = requests.post(f'{api_url}/query/cypher', headers=headers, json=query_data)
if response.status_code == 200:
    results = response.json()['results']
    print(f'查询结果: {json.dumps(results, ensure_ascii=False, indent=2)}')
else:
    print(f'查询失败: {response.text}')
```

### Java客户端示例

```java
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;

public class KnowledgeGraphClient {
    
    private static final String API_URL = "https://kg-api.suoke.life/api/v1";
    private static final String JWT_TOKEN = "YOUR_JWT_TOKEN";
    private static final ObjectMapper mapper = new ObjectMapper();
    
    public static void main(String[] args) throws IOException, InterruptedException {
        // 创建节点
        Map<String, Object> nodeData = new HashMap<>();
        nodeData.put("labels", List.of("Herb"));
        
        Map<String, Object> properties = new HashMap<>();
        properties.put("name", "黄芪");
        properties.put("pinyin", "huáng qí");
        nodeData.put("properties", properties);
        
        String requestBody = mapper.writeValueAsString(nodeData);
        
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL + "/nodes"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + JWT_TOKEN)
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();
        
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() == 201) {
            Map<String, Object> result = mapper.readValue(response.body(), Map.class);
            System.out.println("创建节点成功，ID: " + result.get("id"));
        } else {
            System.out.println("创建节点失败: " + response.body());
        }
    }
}
```

## API开发最佳实践

1. **使用JWT认证**：所有请求都应包含有效的JWT令牌

2. **批量操作**：对于大批量数据操作，优先使用批量API端点

3. **错误处理**：始终检查响应状态码和错误信息

4. **分页处理**：对于大结果集，使用分页参数控制数据量

5. **异步处理**：对于长时间运行的复杂查询，使用异步API

6. **缓存控制**：利用HTTP缓存头优化频繁请求的性能

7. **压缩**：对大型请求和响应使用gzip压缩

8. **超时设置**：为客户端请求设置合理的超时时间

9. **重试策略**：对于网络错误和服务端错误实现自动重试

10. **监控和日志**：记录API调用和性能指标，便于问题诊断