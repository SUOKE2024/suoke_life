# Rag Service API 文档

## 服务概述

**服务名称**: rag-service  
**版本**: 1.0.0  
**描述**: RAG服务主入口
整合所有组件并启动服务

## API 端点

### GET 请求

#### GET /health

**功能**: 健康检查

**函数**: `health_check`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /metrics

**功能**: 获取Prometheus格式的指标

**函数**: `get_metrics`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /status

**功能**: 获取详细的服务状态

**函数**: `get_service_status`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /documents/search

**功能**: GET /documents/search

**函数**: `search_documents`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /agents/{agent_name}/status

**功能**: GET /agents/{agent_name}/status

**函数**: `get_agent_status`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /status

**功能**: GET /status

**函数**: `get_service_status`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /metrics

**功能**: GET /metrics

**函数**: `get_metrics`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

### POST 请求

#### POST /query

**功能**: POST /query

**函数**: `query_rag`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /query/stream

**功能**: POST /query/stream

**函数**: `query_rag_stream`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /tcm/analysis

**功能**: POST /tcm/analysis

**函数**: `analyze_tcm`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /tcm/herbs

**功能**: POST /tcm/herbs

**函数**: `recommend_herbs`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /documents/index

**功能**: POST /documents/index

**函数**: `index_document`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /knowledge-graph/query

**功能**: POST /knowledge-graph/query

**函数**: `query_knowledge_graph`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agents/broadcast

**功能**: POST /agents/broadcast

**函数**: `broadcast_to_agents`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

## 数据模型

### RAGQueryRequest

RAG查询请求

```python
class RAGQueryRequest(BaseModel):
    # 字段定义
    pass
```

### TCMAnalysisRequest

中医分析请求

```python
class TCMAnalysisRequest(BaseModel):
    # 字段定义
    pass
```

### HerbRecommendationRequest

中药推荐请求

```python
class HerbRecommendationRequest(BaseModel):
    # 字段定义
    pass
```

### DocumentIndexRequest

文档索引请求

```python
class DocumentIndexRequest(BaseModel):
    # 字段定义
    pass
```

### KnowledgeGraphQueryRequest

知识图谱查询请求

```python
class KnowledgeGraphQueryRequest(BaseModel):
    # 字段定义
    pass
```

### RAGQueryResponse

RAG查询响应

```python
class RAGQueryResponse(BaseModel):
    # 字段定义
    pass
```

### TCMAnalysisResponse

中医分析响应

```python
class TCMAnalysisResponse(BaseModel):
    # 字段定义
    pass
```

### HerbRecommendationResponse

中药推荐响应

```python
class HerbRecommendationResponse(BaseModel):
    # 字段定义
    pass
```

### ServiceStatusResponse

服务状态响应

```python
class ServiceStatusResponse(BaseModel):
    # 字段定义
    pass
```

### QueryRequest

查询请求验证模型

```python
class QueryRequest(BaseModel):
    # 字段定义
    pass
```

### DocumentRequest

文档请求验证模型

```python
class DocumentRequest(BaseModel):
    # 字段定义
    pass
```

### AddDocumentRequest

添加文档请求验证模型

```python
class AddDocumentRequest(BaseModel):
    # 字段定义
    pass
```

### TCMSyndromeRequest

中医证候分析请求验证模型

```python
class TCMSyndromeRequest(BaseModel):
    # 字段定义
    pass
```

### HerbRecommendationRequest

中药推荐请求验证模型

```python
class HerbRecommendationRequest(BaseModel):
    # 字段定义
    pass
```

### BatchQueryRequest

批量查询请求验证模型

```python
class BatchQueryRequest(BaseModel):
    # 字段定义
    pass
```

### DocumentModel

文档模型

```python
class DocumentModel(BaseModel):
    # 字段定义
    pass
```

### DocumentReferenceModel

文档引用模型

```python
class DocumentReferenceModel(BaseModel):
    # 字段定义
    pass
```

### SearchRequest

搜索请求

```python
class SearchRequest(BaseModel):
    # 字段定义
    pass
```

### SearchResponse

搜索响应

```python
class SearchResponse(BaseModel):
    # 字段定义
    pass
```

### GenerateRequest

生成请求

```python
class GenerateRequest(BaseModel):
    # 字段定义
    pass
```

### GenerateResponse

生成响应

```python
class GenerateResponse(BaseModel):
    # 字段定义
    pass
```

### QueryRequest

查询请求

```python
class QueryRequest(BaseModel):
    # 字段定义
    pass
```

### QueryResponse

查询响应

```python
class QueryResponse(BaseModel):
    # 字段定义
    pass
```

### AddDocumentRequest

添加文档请求

```python
class AddDocumentRequest(BaseModel):
    # 字段定义
    pass
```

### AddDocumentResponse

添加文档响应

```python
class AddDocumentResponse(BaseModel):
    # 字段定义
    pass
```

### DeleteDocumentRequest

删除文档请求

```python
class DeleteDocumentRequest(BaseModel):
    # 字段定义
    pass
```

### DeleteDocumentResponse

删除文档响应

```python
class DeleteDocumentResponse(BaseModel):
    # 字段定义
    pass
```

### HealthResponse

健康检查响应

```python
class HealthResponse(BaseModel):
    # 字段定义
    pass
```

## 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权访问 | 检查认证信息 |
| 403 | 权限不足 | 联系管理员 |
| 404 | 资源不存在 | 检查请求路径 |
| 500 | 服务器内部错误 | 联系技术支持 |

## 使用示例

### Python 示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 示例请求
response = requests.get(f"{BASE_URL}/api/v1/health")
print(response.json())
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/api/v1/health"

# 带认证的请求
curl -X GET "http://localhost:8000/api/v1/data" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 联系信息

- **技术支持**: tech@suoke.life
- **文档更新**: 2025年6月6日
- **维护团队**: 索克生活技术团队

