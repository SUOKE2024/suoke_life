# Web搜索模块集成文档

本文档描述了Web搜索功能模块与RAG服务的集成，包括架构设计、API接口说明、配置指南和部署步骤。

## 架构概述

Web搜索模块已完全集成到RAG服务中，提供以下核心功能：

1. **多引擎搜索**：支持Brave、Google、Bing等搜索引擎
2. **内容处理**：网页内容提取、过滤、摘要生成
3. **知识库整合**：将Web搜索结果与知识库搜索结果融合
4. **知识图谱集成**：关联相关实体和关系数据

### 模块结构

```
src/web_search/
├── __init__.py          # 导出主要类和函数
├── search_provider.py   # 搜索提供者实现
├── content_processor.py # 内容处理实现
└── knowledge_integration.py # 知识库集成实现

src/api/routes/
└── web_search.py        # Web搜索API路由定义
```

## API接口

RAG服务新增了以下Web搜索相关API端点：

### 1. 基础搜索

**端点:** `/api/web-search/search`  
**方法:** POST  
**描述:** 执行基本Web搜索

**请求示例:**
```json
{
  "query": "中医养生太极拳",
  "engine": "brave",
  "max_results": 5
}
```

**响应示例:**
```json
{
  "query": "中医养生太极拳",
  "engine": "brave",
  "web_results": [
    {
      "title": "中医养生太极拳入门教程",
      "link": "https://example.com/taichi",
      "snippet": "太极拳是中医养生的重要方法之一..."
    },
    ...
  ]
}
```

### 2. 知识库查询

**端点:** `/api/web-search/knowledge`  
**方法:** POST  
**描述:** 仅查询知识库

**请求示例:**
```json
{
  "query": "太极拳",
  "limit": 3
}
```

**响应示例:**
```json
{
  "query": "太极拳",
  "results": [
    {
      "title": "太极拳养生原理",
      "content": "太极拳通过调整呼吸和缓慢动作...",
      "relevance": 0.92
    },
    ...
  ]
}
```

### 3. 知识图谱查询

**端点:** `/api/web-search/graph`  
**方法:** POST  
**描述:** 查询与实体相关的知识图谱

**请求示例:**
```json
{
  "entity": "太极拳",
  "relation_types": ["helps_with", "part_of"]
}
```

**响应示例:**
```json
{
  "entity": "太极拳",
  "graph": {
    "nodes": [
      {"id": "太极拳", "type": "exercise"},
      {"id": "养生", "type": "concept"}
    ],
    "edges": [
      {"source": "太极拳", "target": "养生", "type": "helps_with"}
    ]
  }
}
```

### 4. 集成搜索

**端点:** `/api/web-search/integrated-search`  
**方法:** POST  
**描述:** 执行整合的搜索，包含Web搜索、知识库查询和知识图谱

**请求示例:**
```json
{
  "query": "太极拳养生",
  "engine": "brave",
  "max_results": 5,
  "include_insights": true
}
```

**响应示例:**
```json
{
  "query": "太极拳养生",
  "web_results": [...],
  "knowledge_results": [...],
  "graph_data": {
    "nodes": [...],
    "edges": [...]
  },
  "combined_results": [...],
  "insights": {
    "top_topics": ["太极", "养生", "健康"],
    "source_distribution": {"web": 60, "knowledge_base": 40},
    "average_relevance": 0.85
  }
}
```

## 配置说明

Web搜索模块的配置位于`config.yaml`中：

```yaml
web_search:
  api_keys:
    brave: "YOUR_BRAVE_API_KEY"
    google: "YOUR_GOOGLE_API_KEY"
  search:
    default_engine: "brave"
    max_results: 5
    timeout: 10
  content:
    summarization_enabled: true
    max_summary_length: 200
    translation_enabled: false
    target_language: "zh"
    filtering_enabled: true
    blocked_domains: ["spam.com", "ads.example.com"]
  knowledge:
    knowledge_base_url: "http://knowledge-base-service/api"
    knowledge_graph_url: "http://knowledge-graph-service/api"
    api_key: "INTERNAL_API_KEY"
    timeout: 5
```

## 环境变量

敏感配置项也可通过环境变量设置（推荐使用Vault动态注入）：

```
RAG_BRAVE_API_KEY=your_brave_api_key
RAG_GOOGLE_API_KEY=your_google_api_key
RAG_KB_API_KEY=your_kb_api_key
```

## 部署说明

Web搜索模块已集成到RAG服务中，不需要单独部署。只需确保：

1. 配置文件包含所有必要的Web搜索配置项
2. 相关的API密钥已正确设置
3. 知识库服务和知识图谱服务可访问

## 测试

执行以下命令运行Web搜索模块相关测试：

```bash
cd services/rag-service
pytest tests/test_web_search
```

单元测试包括：
- `test_search_provider.py` - 测试搜索提供者功能
- `test_content_processor.py` - 测试内容处理功能
- `test_knowledge_integration.py` - 测试知识库集成功能
- `test_api_routes.py` - 测试API端点

集成测试：
- `test_integration.py` - 测试模块间集成以及与外部服务交互

## 监控与日志

Web搜索模块日志位于标准RAG服务日志中，使用前缀`[WebSearch]`标识：

```
[WebSearch] INFO: 执行搜索，引擎=brave，查询=中医养生
[WebSearch] ERROR: Brave API请求失败：超时
```

API调用指标通过标准Prometheus指标暴露：
- `rag_web_search_requests_total` - 搜索请求计数
- `rag_web_search_errors_total` - 搜索错误计数
- `rag_web_search_latency` - 搜索延迟时间

## 已知限制

1. 当搜索API不可用时，将返回模拟数据，可能导致结果质量下降
2. 内容提取可能无法处理复杂JavaScript渲染的页面
3. 每个API服务提供商有独立的请求频率限制，大量请求可能导致暂时性阻断

## 故障排除

常见问题解决方案：

1. **搜索结果为空**
   - 检查API密钥是否正确
   - 验证网络连接是否正常
   - 查看日志中是否有API错误

2. **内容提取失败**
   - 检查目标网站是否阻止爬虫
   - 尝试增加请求超时设置

3. **知识库集成错误**
   - 确认知识库服务是否正常运行
   - 检查服务间网络连接

## 更新历史

- **v1.0.0** (2023-07-15) - 初始集成版本
- **v1.1.0** (2023-08-30) - 增加内容摘要功能
- **v1.2.0** (2024-01-10) - 增加多引擎支持
- **v2.0.0** (2024-04-25) - 完全集成到RAG服务 