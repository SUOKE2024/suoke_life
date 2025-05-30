# 索克生活 RAG & 多模态 API 文档入口

## 1. API 文档位置

- OpenAPI 3.0 文档：`services/rag-service/api/rest/openapi.yaml`
- 主要接口：
  - `/api/v1/rag/query_multimodal` 多模态RAG推理（文本+图片/音频/视频）
  - `/api/v1/rag/documents/upload_multimodal` 多模态文件上传

## 2. 典型接口说明

### 2.1 多模态RAG推理
- **路径**：`/api/v1/rag/query_multimodal`
- **方法**：POST
- **请求类型**：`multipart/form-data`
- **参数**：
  - `query`：文本查询内容
  - `files`：多模态文件（图片/音频/视频等）
- **返回**：
  - `answer`：生成的健康建议
  - `references`：参考文档
  - `multimodal_context`：多模态内容解析详情

#### 示例（curl）
```bash
curl -X POST http://localhost:8085/api/v1/rag/query_multimodal \
  -F "query=我最近咳嗽，舌苔发白" \
  -F "files=@/path/to/tongue.jpg" \
  -F "files=@/path/to/voice.wav"
```

### 2.2 多模态文件上传
- **路径**：`/api/v1/rag/documents/upload_multimodal`
- **方法**：POST
- **请求类型**：`multipart/form-data`
- **参数**：
  - `files`：多模态文件
  - `collection_name`：知识库集合名（可选）
- **返回**：
  - `status`、`document_ids`、`count`、`message`

## 3. 详细接口定义
- 详见 `openapi.yaml`，可用Swagger等工具可视化查看。

## 4. 联系方式
- 技术支持：tech@suokelife.com 