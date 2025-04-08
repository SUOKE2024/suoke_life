# 知识图谱向量化与相似搜索指南

知识图谱服务支持将节点内容向量化，并提供基于向量相似度的搜索功能。本文档详细介绍了向量化过程、索引创建和相似搜索的实现与使用方法。

## 向量化概览

向量化是将文本、图像等非结构化数据转换为数值向量的过程，使其可以进行数学运算和相似度计算。知识图谱服务支持以下内容的向量化：

| 内容类型 | 向量模型 | 向量维度 | 说明 |
|----------|---------|----------|------|
| 文本内容 | text-embedding-3-large | 768 | 适用于节点描述、属性等文本 |
| 中医术语 | tcm-embedding-1 | 1024 | 专为中医术语优化的embedding模型 |
| 图像内容 | clip-vit-large | 768 | 适用于药材图片等图像内容 |

向量化后的内容存储在图谱节点的特定属性中（如`embedding`、`description_vector`等），并通过Neo4j的向量索引支持高效的相似度搜索。

## 向量化服务

知识图谱服务使用独立的向量化微服务，支持不同类型内容的向量化。

### 向量化端点

```
POST /api/v1/vectorize
```

**请求体**:

```json
{
  "content": "黄芪，性味甘、微温，归肺、脾经，具有补气固表，利水消肿，托毒排脓，生肌功效。",
  "content_type": "text",
  "model": "text-embedding-3-large"
}
```

**响应**:

```json
{
  "vector": [0.0234, 0.0123, -0.0345, ...],  // 768维向量
  "dimensions": 768,
  "model": "text-embedding-3-large"
}
```

### 批量向量化

```
POST /api/v1/vectorize/batch
```

**请求体**:

```json
{
  "items": [
    {
      "id": "item-1",
      "content": "黄芪，性味甘、微温，归肺、脾经...",
      "content_type": "text"
    },
    {
      "id": "item-2",
      "content": "人参，性味甘、微温，归脾、肺经...",
      "content_type": "text"
    }
  ],
  "model": "text-embedding-3-large"
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "item-1",
      "vector": [0.0234, 0.0123, ...],
      "dimensions": 768
    },
    {
      "id": "item-2",
      "vector": [0.0345, 0.0456, ...],
      "dimensions": 768
    }
  ],
  "model": "text-embedding-3-large"
}
```

### 支持的模型

| 模型名称 | 内容类型 | 维度 | 特点 |
|---------|----------|------|------|
| text-embedding-3-large | 文本 | 768 | 通用文本向量化模型 |
| text-embedding-3-small | 文本 | 512 | 轻量级文本向量化模型 |
| tcm-embedding-1 | 文本 | 1024 | 中医特化向量化模型 |
| clip-vit-large | 图像 | 768 | 图像向量化模型 |
| multi-modal-1 | 图文 | 1536 | 多模态向量化模型 |

## 向量索引配置

向量搜索需要在Neo4j中创建向量索引。知识图谱服务支持以下向量索引类型：

### 节点内容向量索引

```cypher
CREATE VECTOR INDEX node_content_vector_index
FOR (n:Node)
ON (n.embedding)
OPTIONS {
  indexConfig: {
    metric: "cosine",
    dimensions: 768,
    efConstruction: 200,
    maxConnections: 16
  }
}
```

### 中药描述向量索引

```cypher
CREATE VECTOR INDEX herb_description_vector_index
FOR (h:Herb)
ON (h.description_vector)
OPTIONS {
  indexConfig: {
    metric: "cosine", 
    dimensions: 768,
    efConstruction: 200,
    maxConnections: 16
  }
}
```

### 方剂功效向量索引

```cypher
CREATE VECTOR INDEX formula_function_vector_index
FOR (f:Formula)
ON (f.function_vector)
OPTIONS {
  indexConfig: {
    metric: "cosine",
    dimensions: 768,
    efConstruction: 200,
    maxConnections: 16
  }
}
```

### 索引配置参数

| 参数 | 说明 | 常用值 |
|------|------|-------|
| metric | 相似度度量方式 | cosine, euclidean, dot |
| dimensions | 向量维度 | 取决于向量模型 |
| efConstruction | 影响索引构建质量 | 100-500，值越高质量越好 |
| maxConnections | 每个节点最大连接数 | 8-64，值越高召回率越高 |
| ef | 查询时考虑的候选集大小 | 50-500，值越高结果越准确 |

## 向量化工作流

完整的向量化工作流程如下：

1. **内容准备**：准备需要向量化的文本或图像内容
2. **向量生成**：使用向量化服务将内容转换为向量
3. **向量存储**：将向量保存到图谱节点的属性中
4. **索引创建**：为向量属性创建适当的向量索引
5. **相似搜索**：使用向量进行相似度搜索

### 工作流示例代码

```go
// 1. 准备内容
herbDescription := "黄芪，性味甘、微温，归肺、脾经，具有补气固表，利水消肿，托毒排脓，生肌功效。"

// 2. 向量化内容
vectorization := vectorization.NewService(apiClient, logger)
vector, err := vectorization.Vectorize(ctx, herbDescription, "text", "text-embedding-3-large")
if err != nil {
    log.Fatalf("向量化失败: %v", err)
}

// 3. 保存向量到节点
herbID := "herb-123"
err = vectorRepo.AddVector(ctx, herbID, vector, "description_vector")
if err != nil {
    log.Fatalf("保存向量失败: %v", err)
}

// 4. 创建索引（仅需执行一次）
createIndex := `
    CREATE VECTOR INDEX herb_description_vector_index 
    FOR (h:Herb) 
    ON (h.description_vector)
    OPTIONS {
        indexConfig: {
            metric: "cosine",
            dimensions: 768
        }
    }
`
_, err = queryRepo.ExecuteCypher(ctx, createIndex, nil)
if err != nil {
    log.Fatalf("创建向量索引失败: %v", err)
}

// 5. 向量相似搜索
queryText := "补气固表的中药"
queryVector, _ := vectorization.Vectorize(ctx, queryText, "text", "text-embedding-3-large")
similarHerbs, err := vectorRepo.FindSimilarWithLabel(ctx, queryVector, "Herb", "description_vector", 10)
if err != nil {
    log.Fatalf("相似搜索失败: %v", err)
}
for _, herb := range similarHerbs {
    fmt.Printf("中药: %s, 相似度: %.4f\n", herb.Node.Properties["name"], herb.Score)
}
```

## 相似搜索方法

知识图谱服务提供多种向量相似搜索方法，满足不同的应用场景。

### 基本相似搜索

```go
// 根据向量查找相似节点
similarNodes, err := vectorRepo.FindSimilar(ctx, vector, "description_vector", 10)
```

### 带标签过滤的相似搜索

```go
// 仅在特定标签内搜索
similarHerbs, err := vectorRepo.FindSimilarWithLabel(ctx, vector, "Herb", "description_vector", 10)
```

### 混合相似搜索

```go
// 结合向量相似度和属性过滤条件
filters := map[string]interface{}{
    "category": "补气药",
    "nature": "温",
}
results, err := vectorRepo.HybridSearch(ctx, vector, "Herb", "description_vector", filters, 5)
```

### Cypher直接查询

```go
query := `
    MATCH (h:Herb)
    WHERE h.description_vector IS NOT NULL
    WITH h, vector.similarity(h.description_vector, $queryVector) AS score
    WHERE score > 0.7
    RETURN h.name AS name, h.pinyin AS pinyin, score
    ORDER BY score DESC
    LIMIT 10
`
params := map[string]interface{}{
    "queryVector": vector,
}
results, err := queryRepo.ExecuteCypher(ctx, query, params)
```

## REST API接口

知识图谱服务提供了一系列REST API接口，用于向量化和相似搜索。

### 向量化文本

```
POST /api/v1/vectors/vectorize-text
```

**请求体**:

```json
{
  "text": "黄芪，性味甘、微温，归肺、脾经，具有补气固表，利水消肿，托毒排脓，生肌功效。",
  "model": "text-embedding-3-large"
}
```

**响应**:

```json
{
  "vector": [0.0234, 0.0123, ...],
  "dimensions": 768
}
```

### 保存节点向量

```
POST /api/v1/nodes/{id}/vector
```

**请求体**:

```json
{
  "vector": [0.0234, 0.0123, ...],
  "field": "description_vector"
}
```

**响应**:

```json
{
  "success": true,
  "node_id": "herb-123",
  "field": "description_vector",
  "dimensions": 768
}
```

### 相似搜索

```
POST /api/v1/vectors/similar
```

**请求体**:

```json
{
  "vector": [0.0234, 0.0123, ...],
  "field": "description_vector",
  "limit": 10
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "herb-123",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪"
      },
      "score": 0.98
    },
    {
      "id": "herb-456",
      "labels": ["Herb"],
      "properties": {
        "name": "党参"
      },
      "score": 0.85
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
  "vector": [0.0234, 0.0123, ...],
  "label": "Herb",
  "field": "description_vector",
  "filters": {
    "category": "补气药",
    "taste": "甘"
  },
  "limit": 5
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "herb-123",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪",
        "category": "补气药",
        "taste": "甘"
      },
      "score": 0.98
    }
    // 更多结果...
  ]
}
```

### 基于文本的相似搜索

```
POST /api/v1/vectors/text-search
```

**请求体**:

```json
{
  "text": "补气固表的中药",
  "label": "Herb",
  "field": "description_vector",
  "model": "text-embedding-3-large",
  "limit": 10
}
```

**响应**:

```json
{
  "results": [
    {
      "id": "herb-123",
      "labels": ["Herb"],
      "properties": {
        "name": "黄芪"
      },
      "score": 0.98
    }
    // 更多结果...
  ],
  "query_vector": [0.0234, 0.0123, ...]
}
```

## 相似度计算方法

知识图谱服务支持多种相似度计算方法：

### 余弦相似度 (Cosine Similarity)

计算两个向量之间夹角的余弦值，范围在[-1, 1]之间，通常归一化到[0, 1]。

```
cosine_similarity(A, B) = (A·B) / (||A|| * ||B||)
```

余弦相似度是最常用的向量相似度度量方法，适合大多数文本嵌入模型。

### 欧几里得距离 (Euclidean Distance)

计算两个向量之间的直线距离，通常需要转换为相似度分数。

```
euclidean_distance(A, B) = √Σ(ai - bi)²
euclidean_similarity(A, B) = 1 / (1 + euclidean_distance(A, B))
```

欧几里得距离适合某些特定的向量空间，尤其是当向量长度有意义时。

### 点积 (Dot Product)

计算两个向量的点积，适用于已经归一化的向量。

```
dot_product(A, B) = Σ(ai * bi)
```

当向量已经归一化（单位长度）时，点积等同于余弦相似度。

## 中医特色向量化应用

知识图谱服务针对中医领域提供了特色的向量化应用。

### 中药功效语义向量化

中药功效文本（如"补气固表"、"清热解毒"）可以向量化以捕捉其语义信息，使得可以查询功效相似的中药。

```go
// 向量化中药功效描述
effectsText := "补气固表，益卫固表"
effectsVector, _ := vectorization.Vectorize(ctx, effectsText, "text", "tcm-embedding-1")

// 保存到节点
err = vectorRepo.AddVector(ctx, herbID, effectsVector, "effects_vector")

// 搜索功效相似的中药
queryEffects := "提高免疫力，抵抗感冒"
queryVector, _ := vectorization.Vectorize(ctx, queryEffects, "text", "tcm-embedding-1")
similarHerbs, _ := vectorRepo.FindSimilarWithLabel(ctx, queryVector, "Herb", "effects_vector", 10)
```

### 方剂组成相似度分析

通过向量化方剂组成信息，可以分析方剂之间的相似度：

```go
// 查询方剂组成相似度
query := `
    MATCH (f1:Formula {name: $formula1})
    MATCH (f2:Formula {name: $formula2})
    WHERE f1.composition_vector IS NOT NULL AND f2.composition_vector IS NOT NULL
    RETURN vector.similarity(f1.composition_vector, f2.composition_vector) AS similarity
`
params := map[string]interface{}{
    "formula1": "四君子汤",
    "formula2": "六君子汤",
}
result, _ := queryRepo.ExecuteCypher(ctx, query, params)
similarity := result[0]["similarity"].(float64)
fmt.Printf("方剂相似度: %.4f\n", similarity)
```

### 症状-证候关联分析

通过向量化症状和证候描述，可以建立症状与证候之间的语义关联：

```go
// 分析症状与证候的关联度
query := `
    MATCH (s:Symptom)
    WHERE s.name = $symptom AND s.description_vector IS NOT NULL
    MATCH (p:Pattern)
    WHERE p.description_vector IS NOT NULL
    WITH s, p, vector.similarity(s.description_vector, p.description_vector) AS score
    WHERE score > 0.7
    RETURN p.name AS pattern, score
    ORDER BY score DESC
    LIMIT 5
`
params := map[string]interface{}{
    "symptom": "疲乏无力",
}
results, _ := queryRepo.ExecuteCypher(ctx, query, params)
for _, r := range results {
    fmt.Printf("证候: %s, 关联度: %.4f\n", r["pattern"], r["score"])
}
```

## 向量搜索性能优化

以下是提高向量搜索性能的关键策略：

### 索引参数优化

调整向量索引参数以平衡搜索速度和精度：

```cypher
CREATE VECTOR INDEX optimized_herb_vector_index
FOR (h:Herb)
ON (h.description_vector)
OPTIONS {
  indexConfig: {
    metric: "cosine",
    dimensions: 768,
    efConstruction: 300,  // 增加构建质量
    maxConnections: 24,   // 增加连接数
    ef: 150               // 增加搜索范围
  }
}
```

### 预过滤策略

在向量搜索前使用传统索引进行预过滤：

```cypher
// 先过滤再进行向量搜索
MATCH (h:Herb)
WHERE h.category = '补气药' AND h.description_vector IS NOT NULL
WITH h, vector.similarity(h.description_vector, $queryVector) AS score
WHERE score > 0.7
RETURN h.name, score
ORDER BY score DESC
LIMIT 10
```

### 向量缓存

对频繁使用的查询向量实现缓存机制：

```go
// 向量缓存实现
type VectorCache struct {
    cache map[string][]float32
    mu    sync.RWMutex
    ttl   time.Duration
}

// 使用缓存
queryKey := fmt.Sprintf("%s:%s", queryText, modelName)
queryVector, found := vectorCache.Get(queryKey)
if !found {
    queryVector, _ = vectorization.Vectorize(ctx, queryText, "text", modelName)
    vectorCache.Set(queryKey, queryVector, 1*time.Hour)
}
```

### 批量处理

对大量节点的向量化使用批处理：

```go
// 批量向量化
texts := []string{
    "黄芪，性味甘、微温，归肺、脾经...",
    "人参，性味甘、微温，归脾、肺经...",
    // 更多文本...
}
vectors, _ := vectorization.VectorizeBatch(ctx, texts, "text", "text-embedding-3-large")

// 批量存储向量
nodeIDs := []string{"node-1", "node-2", ...}
err = vectorRepo.AddVectorBatch(ctx, nodeIDs, vectors, "description_vector")
```

## 高级应用场景

### 基于向量的RAG系统

结合向量搜索和生成式AI实现检索增强生成（RAG）系统：

```go
// RAG系统工作流
func ProcessRAGQuery(ctx context.Context, query string) (string, error) {
    // 1. 向量化查询
    queryVector, _ := vectorization.Vectorize(ctx, query, "text", "text-embedding-3-large")
    
    // 2. 向量相似搜索获取相关知识
    similarNodes, _ := vectorRepo.HybridSearch(
        ctx, 
        queryVector, 
        "KnowledgeNode", 
        "content_vector", 
        nil, 
        10,
    )
    
    // 3. 构建上下文
    var context strings.Builder
    for _, node := range similarNodes {
        context.WriteString(node.Node.Properties["content"].(string))
        context.WriteString("\n\n")
    }
    
    // 4. 生成回答
    llmService := llm.NewService(apiClient, logger)
    response, err := llmService.GenerateWithContext(
        ctx,
        query,
        context.String(),
        "gpt-4o",
    )
    
    return response, err
}
```

### 多模态知识图谱搜索

结合文本和图像向量进行多模态搜索：

```go
// 多模态搜索
func MultiModalSearch(ctx context.Context, textQuery string, imagePath string) ([]*entities.ScoredNode, error) {
    // 1. 向量化文本
    textVector, _ := vectorization.Vectorize(ctx, textQuery, "text", "text-embedding-3-large")
    
    // 2. 向量化图像
    imageBytes, _ := ioutil.ReadFile(imagePath)
    imageVector, _ := vectorization.Vectorize(ctx, base64.StdEncoding.EncodeToString(imageBytes), "image", "clip-vit-large")
    
    // 3. 组合向量（简单平均）
    combinedVector := make([]float32, len(textVector))
    for i := 0; i < len(textVector); i++ {
        combinedVector[i] = (textVector[i] + imageVector[i]) / 2
    }
    
    // 4. 相似搜索
    return vectorRepo.FindSimilarWithLabel(ctx, combinedVector, "Herb", "multimodal_vector", 10)
}
```

### 动态向量更新

根据新内容自动更新节点向量：

```go
// 监听节点更新事件并更新向量
func UpdateNodeVector(ctx context.Context, nodeID string, newContent string) error {
    // 1. 向量化新内容
    newVector, _ := vectorization.Vectorize(ctx, newContent, "text", "text-embedding-3-large")
    
    // 2. 更新节点向量
    return vectorRepo.AddVector(ctx, nodeID, newVector, "description_vector")
}

// 设置数据更新触发器
// 在Neo4j中创建触发内容向量化的存储过程
createProcedure := `
    CREATE OR REPLACE PROCEDURE updateNodeVector() 
    LANGUAGE CYPHER AS
    MATCH (n)
    WHERE n.content_updated = true AND n.content IS NOT NULL
    SET n.content_updated = false
    WITH n
    CALL apoc.trigger.invokeEvent('update_vector', {nodeId: id(n), content: n.content}) YIELD value
    RETURN count(*)
`
```

## 常见问题与解决方案

### 1. 向量搜索性能不佳

**问题**：向量搜索速度缓慢，尤其是数据量大时。

**解决方案**：
- 优化向量索引参数（尝试不同的efConstruction、maxConnections值）
- 对搜索结果进行预过滤
- 考虑分片或向量数据库级别的优化
- 监控查询计划并优化索引使用

### 2. 向量质量问题

**问题**：向量相似搜索结果与预期不符。

**解决方案**：
- 使用更适合领域的向量模型（如中医特化模型）
- 优化文本预处理（清理、规范化）
- 尝试不同的相似度度量方法（cosine, euclidean等）
- 考虑使用更大维度的向量捕获更多语义信息

### 3. 批量向量化效率低

**问题**：大量数据向量化处理速度慢。

**解决方案**：
- 实现并行向量化处理
- 使用队列系统分批处理
- 利用缓存机制避免重复向量化
- 使用轻量级向量模型进行初始处理

### 4. 向量存储空间占用大

**问题**：向量数据占用大量存储空间。

**解决方案**：
- 使用量化技术（如PQ、SQ量化）减小向量大小
- 仅为关键节点创建向量
- 考虑使用专门的向量数据库存储向量
- 定期清理不再使用的向量数据

### 5. 多维向量可视化困难

**问题**：难以可视化和理解高维向量空间。

**解决方案**：
- 使用降维技术（PCA、t-SNE、UMAP）进行可视化
- 构建向量空间探索工具
- 使用聚类技术识别向量模式
- 开发交互式向量空间浏览界面

## 最佳实践

1. **选择合适的向量模型**：根据具体领域和数据类型选择专用向量模型

2. **定期更新向量**：当节点内容更新时同步更新向量

3. **优化索引参数**：根据数据规模和查询模式调整索引参数

4. **组合过滤和向量搜索**：使用传统过滤器缩小向量搜索范围

5. **实现向量缓存**：缓存频繁使用的查询向量和中间结果

6. **使用批处理**：对大量数据采用批量向量化和存储

7. **监控向量质量**：定期评估向量搜索结果的质量和相关性

8. **结合域知识**：利用领域知识优化向量搜索（如中医关系模型）

9. **平衡精度和效率**：根据应用需求调整向量搜索的精度和速度平衡

10. **异步处理**：将向量化作为异步任务处理，避免阻塞主流程