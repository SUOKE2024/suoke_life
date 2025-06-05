# RAG服务API使用示例

## 目录
- [基础查询示例](#基础查询示例)
- [多模态查询示例](#多模态查询示例)
- [中医特色功能示例](#中医特色功能示例)
- [管理接口示例](#管理接口示例)
- [错误处理示例](#错误处理示例)
- [性能优化示例](#性能优化示例)

## 基础查询示例

### 1. 简单文本查询

```bash
# 基础查询
curl -X POST "http://localhost:8076/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "高血压的中医治疗方法有哪些？",
    "top_k": 5,
    "collection_names": ["tcm_knowledge", "medical_guidelines"]
  }'
```

**响应示例：**
```json
{
  "answer": "中医治疗高血压主要采用辨证论治的方法，常见治疗方案包括：\n\n1. **肝阳上亢型**：使用天麻钩藤饮加减\n2. **痰湿壅盛型**：采用半夏白术天麻汤\n3. **肾阴虚型**：选用杞菊地黄丸\n4. **血瘀型**：运用血府逐瘀汤\n\n配合针灸、推拿等非药物疗法，效果更佳。",
  "references": [
    {
      "id": "tcm_hypertension_001",
      "title": "中医高血压诊疗指南",
      "source": "中华中医药学会",
      "url": "https://example.com/tcm-hypertension",
      "snippet": "肝阳上亢是高血压最常见的中医证型..."
    }
  ],
  "retrieval_latency_ms": 45.2,
  "generation_latency_ms": 1200.5,
  "total_latency_ms": 1245.7
}
```

### 2. 流式查询

```bash
# 流式查询，实时获取生成结果
curl -X POST "http://localhost:8076/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "糖尿病患者的饮食调理建议",
    "top_k": 3,
    "system_prompt": "你是一位专业的中医营养师，请提供科学、实用的建议。"
  }'
```

**流式响应示例：**
```
data: {"answer_fragment": "糖尿病患者的饮食调理", "is_final": false}

data: {"answer_fragment": "应遵循以下原则：\n\n1. 控制总热量", "is_final": false}

data: {"answer_fragment": "摄入\n2. 合理搭配营养素", "is_final": false}

data: {"answer_fragment": "\n3. 定时定量进餐", "is_final": true, "references": [...]}
```

## 多模态查询示例

### 3. 图文结合查询

```bash
# 上传舌象图片进行中医诊断
curl -X POST "http://localhost:8076/api/v1/query_multimodal" \
  -H "X-API-Key: your-api-key" \
  -F "query=请分析这个舌象，给出中医诊断建议" \
  -F "files=@tongue_image.jpg"
```

**响应示例：**
```json
{
  "answer": "根据舌象分析：\n\n**舌质**：舌质偏红，提示有热象\n**舌苔**：苔薄黄，表明有湿热\n**舌形**：舌体略胖大，提示脾虚湿盛\n\n**诊断建议**：脾虚湿热证\n**治疗原则**：健脾化湿，清热解毒\n**方药建议**：三仁汤加减",
  "multimodal_context": [
    {
      "type": "image_analysis",
      "features": {
        "tongue_color": "red",
        "coating_color": "yellow",
        "coating_thickness": "thin",
        "tongue_shape": "slightly_enlarged"
      }
    }
  ],
  "references": [...],
  "total_latency_ms": 2100.3
}
```

## 中医特色功能示例

### 4. 证候分析

```bash
# 中医证候分析
curl -X POST "http://localhost:8076/api/v1/tcm/syndrome_analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "symptoms": ["头痛", "眩晕", "面红", "急躁易怒", "口苦"],
    "pulse": "弦脉",
    "tongue": "舌红苔黄"
  }'
```

**响应示例：**
```json
{
  "syndrome": "肝阳上亢证",
  "confidence": 0.92,
  "treatment_principle": "平肝潜阳，滋阴降火",
  "recommended_formula": "天麻钩藤饮",
  "herbs": [
    {"name": "天麻", "dosage": "10g", "function": "平肝息风"},
    {"name": "钩藤", "dosage": "15g", "function": "清热平肝"},
    {"name": "石决明", "dosage": "30g", "function": "平肝潜阳"}
  ],
  "lifestyle_advice": [
    "保持情绪稳定，避免急躁",
    "饮食清淡，少食辛辣",
    "适当运动，如太极拳"
  ]
}
```

### 5. 中药推荐

```bash
# 基于症状的中药推荐
curl -X POST "http://localhost:8076/api/v1/tcm/herb_recommendation" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "condition": "失眠多梦",
    "constitution": "阴虚体质",
    "age": 45,
    "gender": "female"
  }'
```

## 管理接口示例

### 6. 添加文档到知识库

```bash
# 添加新的医学文档
curl -X POST "http://localhost:8076/api/v1/documents" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "document": {
      "content": "针灸治疗失眠的临床研究表明，百会、神门、三阴交等穴位组合使用效果显著...",
      "metadata": {
        "title": "针灸治疗失眠临床研究",
        "author": "张医生",
        "category": "针灸学",
        "date": "2024-01-15",
        "source": "中医临床杂志"
      },
      "source": "clinical_research"
    },
    "collection_name": "acupuncture_knowledge",
    "reindex": true
  }'
```

### 7. 批量文档管理

```bash
# 获取文档列表
curl -X GET "http://localhost:8076/api/v1/documents?collection=tcm_knowledge&page=1&limit=20" \
  -H "X-API-Key: your-api-key"

# 删除文档
curl -X DELETE "http://localhost:8076/api/v1/documents/doc_12345" \
  -H "X-API-Key: your-api-key"
```

## 错误处理示例

### 8. 常见错误及处理

```bash
# 查询参数错误
curl -X POST "http://localhost:8076/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "top_k": -1
  }'
```

**错误响应：**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "查询参数验证失败",
    "details": {
      "query": "查询内容不能为空",
      "top_k": "top_k必须大于0"
    }
  },
  "request_id": "req_12345",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 9. 服务限流处理

```bash
# 超出API调用限制
curl -X POST "http://localhost:8076/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "测试查询"}'
```

**限流响应：**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API调用频率超限",
    "details": {
      "limit": 100,
      "window": "1分钟",
      "retry_after": 30
    }
  }
}
```

## 性能优化示例

### 10. 缓存使用

```bash
# 启用缓存的查询
curl -X POST "http://localhost:8076/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-Cache-Control: max-age=3600" \
  -d '{
    "query": "常见的中医养生方法",
    "top_k": 5
  }'
```

### 11. 批量查询优化

```bash
# 批量查询接口
curl -X POST "http://localhost:8076/api/v1/query/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "queries": [
      {"query": "高血压治疗", "top_k": 3},
      {"query": "糖尿病饮食", "top_k": 3},
      {"query": "失眠调理", "top_k": 3}
    ],
    "parallel": true
  }'
```

## Python SDK示例

### 12. 使用Python客户端

```python
from rag_client import RAGClient

# 初始化客户端
client = RAGClient(
    base_url="http://localhost:8076",
    api_key="your-api-key"
)

# 简单查询
result = await client.query(
    query="中医如何治疗失眠？",
    top_k=5,
    collection_names=["tcm_knowledge"]
)

print(f"答案：{result.answer}")
for ref in result.references:
    print(f"参考：{ref.title} - {ref.source}")

# 流式查询
async for chunk in client.stream_query("详细介绍太极拳的养生功效"):
    print(chunk.answer_fragment, end="", flush=True)

# 多模态查询
with open("tongue_image.jpg", "rb") as f:
    result = await client.multimodal_query(
        query="请分析这个舌象",
        files=[f]
    )
```

## 监控和调试

### 13. 健康检查

```bash
# 服务健康检查
curl -X GET "http://localhost:8076/health"

# 详细状态检查
curl -X GET "http://localhost:8076/status"

# 获取指标
curl -X GET "http://localhost:8076/metrics"
```

### 14. 调试模式

```bash
# 启用调试模式的查询
curl -X POST "http://localhost:8076/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-Debug: true" \
  -d '{
    "query": "测试查询",
    "top_k": 3
  }'
```

**调试响应包含额外信息：**
```json
{
  "answer": "...",
  "references": [...],
  "debug_info": {
    "retrieval_details": {
      "vector_search_time": 23.5,
      "keyword_search_time": 12.3,
      "rerank_time": 8.7
    },
    "generation_details": {
      "prompt_tokens": 1250,
      "completion_tokens": 380,
      "model_used": "gpt-4o-mini"
    },
    "cache_status": "miss"
  }
}
```

## 最佳实践

### 15. 性能优化建议

1. **合理设置top_k值**：通常3-10个结果足够
2. **使用缓存**：对于常见查询启用缓存
3. **批量处理**：多个查询时使用批量接口
4. **选择合适的集合**：指定相关的知识库集合
5. **流式查询**：对于长文本生成使用流式接口

### 16. 安全最佳实践

1. **API密钥管理**：定期轮换API密钥
2. **访问控制**：使用IP白名单限制访问
3. **数据加密**：敏感数据传输使用HTTPS
4. **审计日志**：记录所有API调用
5. **输入验证**：严格验证用户输入

这些示例涵盖了RAG服务的所有主要功能，为开发者提供了完整的使用指南。 