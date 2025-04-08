# 知识图谱存储库使用指南

知识图谱服务使用专门设计的存储库(Repository)模式来抽象和管理与Neo4j数据库的交互。本文档详细介绍了核心存储库的设计、实现和使用方法，以及常见的图谱操作和查询方式。

## 存储库概览

系统包含以下核心存储库：

| 存储库类型 | 接口 | 实现 | 功能 |
|----------|------|------|------|
| 节点存储库 | NodeRepository | Neo4jNodeRepository | 管理知识图谱中的节点 |
| 关系存储库 | RelationshipRepository | Neo4jRelationshipRepository | 管理知识图谱中的关系 |
| 查询存储库 | QueryRepository | Neo4jQueryRepository | 执行复杂的图谱查询 |
| 向量存储库 | VectorRepository | Neo4jVectorRepository | 管理节点向量和相似度搜索 |

每个存储库都实现了特定的接口，提供了一组一致的操作，使上层业务逻辑不必关心底层存储实现细节。

## 节点存储库

`NodeRepository`接口定义了与图谱节点相关的所有操作，包括创建、查询、更新和删除节点。

### 核心方法

```go
type NodeRepository interface {
    // 根据ID查询节点
    GetByID(ctx context.Context, id string) (*entities.Node, error)
    
    // 根据标签和属性查询节点
    GetByProperty(ctx context.Context, label string, property string, value interface{}) (*entities.Node, error)
    
    // 根据标签和属性列表查询多个节点
    FindByProperties(ctx context.Context, label string, props map[string]interface{}) ([]*entities.Node, error)
    
    // 根据标签查询节点
    FindByLabel(ctx context.Context, label string, limit int) ([]*entities.Node, error)
    
    // 创建节点
    Create(ctx context.Context, node *entities.Node) (string, error)
    
    // 批量创建节点
    CreateBatch(ctx context.Context, nodes []*entities.Node) ([]string, error)
    
    // 更新节点属性
    Update(ctx context.Context, id string, props map[string]interface{}) error
    
    // 删除节点
    Delete(ctx context.Context, id string) error
    
    // 合并节点（创建或更新）
    Merge(ctx context.Context, node *entities.Node, identifyingProps []string) (string, error)
    
    // 向节点添加标签
    AddLabels(ctx context.Context, id string, labels []string) error
    
    // 移除节点的标签
    RemoveLabels(ctx context.Context, id string, labels []string) error
    
    // 统计特定标签的节点数量
    Count(ctx context.Context, label string) (int, error)
}
```

### 使用示例

```go
// 创建节点实例
node := &entities.Node{
    Labels: []string{"Herb"},
    Properties: map[string]interface{}{
        "name":        "黄芪",
        "pinyin":      "huáng qí",
        "description": "补气药，补脾肺之气",
    },
}

// 创建节点
id, err := nodeRepo.Create(ctx, node)
if err != nil {
    log.Fatalf("创建节点失败: %v", err)
}
fmt.Printf("创建成功，节点ID: %s\n", id)

// 查询节点
foundNode, err := nodeRepo.GetByProperty(ctx, "Herb", "name", "黄芪")
if err != nil {
    log.Fatalf("查询节点失败: %v", err)
}
fmt.Printf("找到节点: %+v\n", foundNode)

// 更新节点
err = nodeRepo.Update(ctx, id, map[string]interface{}{
    "description": "补气固表，利水消肿，托毒排脓，生肌",
    "latin_name":  "Astragalus membranaceus",
})
if err != nil {
    log.Fatalf("更新节点失败: %v", err)
}

// 批量创建节点
nodes := []*entities.Node{
    {
        Labels: []string{"Herb"},
        Properties: map[string]interface{}{
            "name": "党参",
            "pinyin": "dǎng shēn",
        },
    },
    {
        Labels: []string{"Herb"},
        Properties: map[string]interface{}{
            "name": "白术",
            "pinyin": "bái zhú",
        },
    },
}
ids, err := nodeRepo.CreateBatch(ctx, nodes)
if err != nil {
    log.Fatalf("批量创建节点失败: %v", err)
}
fmt.Printf("批量创建成功，节点IDs: %v\n", ids)
```

### Neo4j节点存储库实现

`Neo4jNodeRepository`提供了`NodeRepository`接口的Neo4j实现：

```go
// 创建Neo4j节点存储库
driver, err := neo4j.NewDriver(uri, neo4j.BasicAuth(username, password, ""))
if err != nil {
    log.Fatalf("无法创建Neo4j驱动: %v", err)
}

nodeRepo := repositories.NewNeo4jNodeRepository(driver, logger)
```

## 关系存储库

`RelationshipRepository`接口定义了与图谱关系相关的所有操作，包括创建、查询和删除关系。

### 核心方法

```go
type RelationshipRepository interface {
    // 创建关系
    Create(ctx context.Context, relationship *entities.Relationship) (string, error)
    
    // 批量创建关系
    CreateBatch(ctx context.Context, relationships []*entities.Relationship) ([]string, error)
    
    // 根据ID查询关系
    GetByID(ctx context.Context, id string) (*entities.Relationship, error)
    
    // 查询两个节点之间的关系
    FindBetweenNodes(ctx context.Context, sourceID, targetID string, relationshipType string) ([]*entities.Relationship, error)
    
    // 查询从节点出发的关系
    FindOutgoing(ctx context.Context, nodeID string, relationshipType string) ([]*entities.Relationship, error)
    
    // 查询指向节点的关系
    FindIncoming(ctx context.Context, nodeID string, relationshipType string) ([]*entities.Relationship, error)
    
    // 更新关系属性
    Update(ctx context.Context, id string, props map[string]interface{}) error
    
    // 删除关系
    Delete(ctx context.Context, id string) error
    
    // 合并关系（创建或更新）
    Merge(ctx context.Context, relationship *entities.Relationship) (string, error)
    
    // 统计特定类型的关系数量
    Count(ctx context.Context, relationshipType string) (int, error)
}
```

### 使用示例

```go
// 创建关系实例
rel := &entities.Relationship{
    SourceID: herbID,
    TargetID: categoryID,
    Type:     "BELONGS_TO",
    Properties: map[string]interface{}{
        "confidence": 0.95,
        "source":     "中国药典2020版",
    },
}

// 创建关系
id, err := relRepo.Create(ctx, rel)
if err != nil {
    log.Fatalf("创建关系失败: %v", err)
}
fmt.Printf("创建成功，关系ID: %s\n", id)

// 查询从节点出发的关系
relationships, err := relRepo.FindOutgoing(ctx, herbID, "TREATS")
if err != nil {
    log.Fatalf("查询关系失败: %v", err)
}
fmt.Printf("找到关系: %d\n", len(relationships))

// 批量创建关系
relationships := []*entities.Relationship{
    {
        SourceID: formulaID,
        TargetID: herbID1,
        Type:     "CONTAINS",
        Properties: map[string]interface{}{
            "amount": "10g",
        },
    },
    {
        SourceID: formulaID,
        TargetID: herbID2,
        Type:     "CONTAINS",
        Properties: map[string]interface{}{
            "amount": "15g",
        },
    },
}
ids, err := relRepo.CreateBatch(ctx, relationships)
if err != nil {
    log.Fatalf("批量创建关系失败: %v", err)
}
fmt.Printf("批量创建成功，关系IDs: %v\n", ids)
```

### Neo4j关系存储库实现

`Neo4jRelationshipRepository`提供了`RelationshipRepository`接口的Neo4j实现：

```go
// 创建Neo4j关系存储库
relRepo := repositories.NewNeo4jRelationshipRepository(driver, logger)
```

## 查询存储库

`QueryRepository`接口定义了复杂的图谱查询操作，如路径查询、模式匹配和聚合查询。

### 核心方法

```go
type QueryRepository interface {
    // 执行自定义Cypher查询
    ExecuteCypher(ctx context.Context, query string, params map[string]interface{}) ([]map[string]interface{}, error)
    
    // 查找两节点之间的最短路径
    FindShortestPath(ctx context.Context, sourceID, targetID string, relationshipTypes []string, maxDepth int) (*entities.Path, error)
    
    // 查找所有路径
    FindAllPaths(ctx context.Context, sourceID, targetID string, relationshipTypes []string, maxDepth int) ([]*entities.Path, error)
    
    // 查找符合模式的子图
    FindPattern(ctx context.Context, pattern string, params map[string]interface{}) (*entities.Subgraph, error)
    
    // 执行聚合查询
    Aggregate(ctx context.Context, label string, groupBy string, aggregations map[string]string) ([]map[string]interface{}, error)
    
    // 分页查询
    FindWithPagination(ctx context.Context, label string, props map[string]interface{}, page, pageSize int) (*entities.PagedResult, error)
    
    // 执行全文搜索
    FullTextSearch(ctx context.Context, label string, field string, searchTerm string, limit int) ([]*entities.Node, error)
}
```

### 使用示例

```go
// 执行Cypher查询
query := `
    MATCH (h:Herb)-[:TREATS]->(s:Symptom)
    WHERE h.name = $name
    RETURN s.name AS symptom, count(*) AS count
    ORDER BY count DESC
    LIMIT 10
`
params := map[string]interface{}{
    "name": "黄芪",
}
results, err := queryRepo.ExecuteCypher(ctx, query, params)
if err != nil {
    log.Fatalf("查询失败: %v", err)
}
for _, result := range results {
    fmt.Printf("症状: %s, 计数: %d\n", result["symptom"], result["count"])
}

// 查找最短路径
path, err := queryRepo.FindShortestPath(ctx, herbID, symptomID, []string{"TREATS", "SIMILAR_TO"}, 3)
if err != nil {
    log.Fatalf("路径查询失败: %v", err)
}
fmt.Printf("找到路径: %+v\n", path)

// 执行全文搜索
nodes, err := queryRepo.FullTextSearch(ctx, "Herb", "description", "补气 固表", 10)
if err != nil {
    log.Fatalf("全文搜索失败: %v", err)
}
fmt.Printf("搜索结果: %d 个节点\n", len(nodes))
```

### Neo4j查询存储库实现

`Neo4jQueryRepository`提供了`QueryRepository`接口的Neo4j实现：

```go
// 创建Neo4j查询存储库
queryRepo := repositories.NewNeo4jQueryRepository(driver, logger)
```

## 向量存储库

`VectorRepository`接口定义了与节点向量相关的操作，支持向量存储和相似度搜索。

### 核心方法

```go
type VectorRepository interface {
    // 给节点添加向量
    AddVector(ctx context.Context, nodeID string, vector []float32, field string) error
    
    // 批量添加向量
    AddVectorBatch(ctx context.Context, nodes []string, vectors [][]float32, field string) error
    
    // 根据向量相似度查询节点
    FindSimilar(ctx context.Context, vector []float32, field string, limit int) ([]*entities.ScoredNode, error)
    
    // 查询两个节点之间的向量相似度
    VectorSimilarity(ctx context.Context, nodeID1, nodeID2 string, field string) (float32, error)
    
    // 根据标签和向量相似度查询节点
    FindSimilarWithLabel(ctx context.Context, vector []float32, label string, field string, limit int) ([]*entities.ScoredNode, error)
    
    // 混合搜索（结合向量相似度和属性过滤）
    HybridSearch(ctx context.Context, vector []float32, label string, field string, filters map[string]interface{}, limit int) ([]*entities.ScoredNode, error)
}
```

### 使用示例

```go
// 创建向量
vector := []float32{0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8}

// 给节点添加向量
err := vectorRepo.AddVector(ctx, nodeID, vector, "description_vector")
if err != nil {
    log.Fatalf("添加向量失败: %v", err)
}

// 查询相似节点
similarNodes, err := vectorRepo.FindSimilar(ctx, vector, "description_vector", 10)
if err != nil {
    log.Fatalf("相似度搜索失败: %v", err)
}
for _, node := range similarNodes {
    fmt.Printf("节点: %s, 分数: %f\n", node.Node.Properties["name"], node.Score)
}

// 执行混合搜索
filters := map[string]interface{}{
    "category": "补气药",
}
results, err := vectorRepo.HybridSearch(ctx, vector, "Herb", "description_vector", filters, 5)
if err != nil {
    log.Fatalf("混合搜索失败: %v", err)
}
fmt.Printf("混合搜索结果: %d 个节点\n", len(results))
```

### Neo4j向量存储库实现

`Neo4jVectorRepository`提供了`VectorRepository`接口的Neo4j实现：

```go
// 创建Neo4j向量存储库
vectorRepo := repositories.NewNeo4jVectorRepository(driver, logger)
```

## 常见的图谱操作

### 1. 创建和查询复杂子图

```go
// 定义药方子图
// 创建方剂节点
formulaNode := &entities.Node{
    Labels: []string{"Formula"},
    Properties: map[string]interface{}{
        "name":     "四君子汤",
        "pinyin":   "sì jūn zǐ tāng",
        "function": "补气健脾",
    },
}
formulaID, _ := nodeRepo.Create(ctx, formulaNode)

// 创建组成中药节点
herbIDs := make([]string, 0)
herbs := []map[string]interface{}{
    {"name": "人参", "amount": "10g"},
    {"name": "白术", "amount": "15g"},
    {"name": "茯苓", "amount": "15g"},
    {"name": "甘草", "amount": "6g"},
}

for _, herb := range herbs {
    // 查询中药是否存在
    herbNode, err := nodeRepo.GetByProperty(ctx, "Herb", "name", herb["name"])
    if err != nil {
        // 创建新的中药节点
        herbNode = &entities.Node{
            Labels: []string{"Herb"},
            Properties: map[string]interface{}{
                "name": herb["name"],
            },
        }
        herbID, _ := nodeRepo.Create(ctx, herbNode)
        herbIDs = append(herbIDs, herbID)
    } else {
        herbIDs = append(herbIDs, herbNode.ID)
    }
}

// 创建方剂与中药的关系
relationships := make([]*entities.Relationship, 0)
for i, herbID := range herbIDs {
    rel := &entities.Relationship{
        SourceID: formulaID,
        TargetID: herbID,
        Type:     "CONTAINS",
        Properties: map[string]interface{}{
            "amount": herbs[i]["amount"],
        },
    }
    relationships = append(relationships, rel)
}

// 批量创建关系
relRepo.CreateBatch(ctx, relationships)
```

### 2. 查询和分析药物功效网络

```go
// 查询某种功效相关的中药网络
query := `
    MATCH (h:Herb)-[:HAS_PROPERTY]->(e:Effect {name: $effect})
    MATCH (h)-[:TREATS]->(s:Symptom)
    WITH h, collect(DISTINCT s.name) AS symptoms
    RETURN h.name AS herb, h.pinyin AS pinyin, symptoms
    ORDER BY size(symptoms) DESC
    LIMIT 20
`
params := map[string]interface{}{
    "effect": "补气",
}
results, _ := queryRepo.ExecuteCypher(ctx, query, params)

// 分析和打印结果
for _, result := range results {
    herbName := result["herb"].(string)
    pinyin := result["pinyin"].(string)
    symptoms := result["symptoms"].([]interface{})
    
    symptomStrs := make([]string, len(symptoms))
    for i, s := range symptoms {
        symptomStrs[i] = s.(string)
    }
    
    fmt.Printf("中药: %s (%s)\n", herbName, pinyin)
    fmt.Printf("治疗症状: %s\n", strings.Join(symptomStrs, ", "))
    fmt.Println("---")
}
```

### 3. 构建中药分类体系

```go
// 创建分类层级
categories := []struct {
    Name     string
    ParentID string
}{
    {Name: "中药", ParentID: ""},
    {Name: "补虚药", ParentID: ""},
    {Name: "解表药", ParentID: ""},
    {Name: "清热药", ParentID: ""},
    {Name: "补气药", ParentID: ""},
    {Name: "补血药", ParentID: ""},
    {Name: "补阴药", ParentID: ""},
    {Name: "补阳药", ParentID: ""},
}

// 创建分类节点
categoryIDs := make(map[string]string)
for _, category := range categories {
    categoryNode := &entities.Node{
        Labels: []string{"Category"},
        Properties: map[string]interface{}{
            "name": category.Name,
        },
    }
    id, _ := nodeRepo.Create(ctx, categoryNode)
    categoryIDs[category.Name] = id
}

// 创建分类层级关系
for _, category := range categories {
    if category.ParentID != "" {
        rel := &entities.Relationship{
            SourceID: categoryIDs[category.Name],
            TargetID: categoryIDs[category.ParentID],
            Type:     "SUBCATEGORY_OF",
        }
        relRepo.Create(ctx, rel)
    }
}

// 将中药分配到分类
herbCategories := map[string]string{
    "人参":   "补气药",
    "黄芪":   "补气药",
    "党参":   "补气药",
    "白术":   "补气药",
    "当归":   "补血药",
    "熟地黄":  "补血药",
    "白芍":   "补血药",
    "大枣":   "补血药",
    "麦冬":   "补阴药",
    "天冬":   "补阴药",
    "石斛":   "补阴药",
    "玄参":   "补阴药",
    "鹿茸":   "补阳药",
    "肉苁蓉":  "补阳药",
    "淫羊藿":  "补阳药",
    "巴戟天":  "补阳药",
}

// 批量创建中药与分类的关系
relationships := make([]*entities.Relationship, 0)
for herbName, categoryName := range herbCategories {
    herbNode, err := nodeRepo.GetByProperty(ctx, "Herb", "name", herbName)
    if err != nil {
        continue // 跳过不存在的中药
    }
    
    rel := &entities.Relationship{
        SourceID: herbNode.ID,
        TargetID: categoryIDs[categoryName],
        Type:     "BELONGS_TO",
    }
    relationships = append(relationships, rel)
}

// 批量创建关系
relRepo.CreateBatch(ctx, relationships)
```

## 进阶使用技巧

### 1. 事务管理

对于需要保证原子性的操作，应使用事务：

```go
// 创建事务函数
txFunc := func(tx neo4j.Transaction) (interface{}, error) {
    // 在事务中执行多个操作
    node := &entities.Node{
        Labels: []string{"Herb"},
        Properties: map[string]interface{}{
            "name": "黄芪",
        },
    }
    
    // 创建节点
    nodeID, err := nodeRepo.CreateInTx(tx, node)
    if err != nil {
        return nil, err // 事务将回滚
    }
    
    // 创建关系
    rel := &entities.Relationship{
        SourceID: nodeID,
        TargetID: categoryID,
        Type:     "BELONGS_TO",
    }
    _, err = relRepo.CreateInTx(tx, rel)
    if err != nil {
        return nil, err // 事务将回滚
    }
    
    return nodeID, nil // 事务将提交
}

// 执行事务
session := driver.NewSession(neo4j.SessionConfig{})
defer session.Close()

result, err := session.WriteTransaction(txFunc)
if err != nil {
    log.Fatalf("事务失败: %v", err)
}
fmt.Printf("事务成功，节点ID: %s\n", result.(string))
```

### 2. 批量操作优化

对于大批量数据导入，可以使用以下优化策略：

```go
// 批量创建节点示例
const batchSize = 1000
nodes := make([]*entities.Node, 0, batchSize)
totalNodes := len(allNodes)

for i := 0; i < totalNodes; i += batchSize {
    end := i + batchSize
    if end > totalNodes {
        end = totalNodes
    }
    
    batch := allNodes[i:end]
    ids, err := nodeRepo.CreateBatch(ctx, batch)
    if err != nil {
        log.Printf("批次 %d-%d 失败: %v", i, end, err)
        continue
    }
    log.Printf("批次 %d-%d 成功创建 %d 个节点", i, end, len(ids))
}
```

### 3. 全文搜索索引

创建全文搜索索引以提高文本搜索性能：

```go
// 创建全文搜索索引的Cypher查询
createIndex := `
    CALL db.index.fulltext.createNodeIndex(
        "herbDescriptionIndex",
        ["Herb"],
        ["name", "description", "functions"]
    )
`
_, err := queryRepo.ExecuteCypher(ctx, createIndex, nil)
if err != nil {
    log.Fatalf("创建全文索引失败: %v", err)
}

// 使用全文搜索索引
searchQuery := `
    CALL db.index.fulltext.queryNodes("herbDescriptionIndex", $searchTerm)
    YIELD node, score
    RETURN node.name AS name, node.pinyin AS pinyin, score
    ORDER BY score DESC
    LIMIT 10
`
params := map[string]interface{}{
    "searchTerm": "补气 固表 +黄芪",
}
results, _ := queryRepo.ExecuteCypher(ctx, searchQuery, params)
```

### 4. 向量索引和相似度搜索

设置向量索引以支持高效的相似度搜索：

```go
// 创建向量索引的Cypher查询
createVectorIndex := `
    CREATE VECTOR INDEX herb_vector_index
    FOR (n:Herb)
    ON (n.embedding)
    OPTIONS {indexConfig: {
        metric: "cosine",
        dimensions: 768
    }}
`
_, err := queryRepo.ExecuteCypher(ctx, createVectorIndex, nil)
if err != nil {
    log.Fatalf("创建向量索引失败: %v", err)
}

// 使用向量索引进行相似度搜索
vectorQuery := `
    MATCH (n:Herb)
    WHERE n.embedding IS NOT NULL
    WITH n, vector.similarity(n.embedding, $queryVector) AS score
    WHERE score > 0.7
    RETURN n.name AS name, n.pinyin AS pinyin, score
    ORDER BY score DESC
    LIMIT 10
`
params := map[string]interface{}{
    "queryVector": []float64{0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8},
}
results, _ := queryRepo.ExecuteCypher(ctx, vectorQuery, params)
```

## 常见问题与解决方案

### 1. 处理大规模图谱的性能问题

当图谱规模增大时，查询性能可能下降。以下是一些优化建议：

- **创建适当的索引**：为常用查询条件创建索引
```go
// 创建索引
createIndex := `
    CREATE INDEX herb_name_index FOR (n:Herb) ON (n.name)
`
queryRepo.ExecuteCypher(ctx, createIndex, nil)
```

- **使用EXPLAIN/PROFILE分析查询**：优化慢查询
```go
// 分析查询
explainQuery := `
    EXPLAIN
    MATCH (h:Herb)-[:TREATS]->(s:Symptom)
    WHERE h.name = "黄芪"
    RETURN s.name, count(*)
`
queryRepo.ExecuteCypher(ctx, explainQuery, nil)
```

- **限制查询深度**：特别是对于递归查询
```go
// 限制路径查询深度
paths, err := queryRepo.FindAllPaths(ctx, sourceID, targetID, []string{"CONTAINS", "TREATS"}, 3)
```

- **使用分页**：对大结果集进行分页
```go
// 使用分页查询
pagedResult, err := queryRepo.FindWithPagination(ctx, "Herb", map[string]interface{}{
    "category": "补气药",
}, 1, 20)
```

### 2. 处理并发访问

在并发环境中使用存储库时，应注意：

- 每个请求使用独立的Session
- 长时间运行的操作应设置超时
- 使用连接池管理驱动程序资源

```go
// 创建带有连接池配置的驱动
config := func(conf *neo4j.Config) {
    conf.MaxConnectionPoolSize = 50
    conf.MaxConnectionLifetime = 30 * time.Minute
    conf.ConnectionAcquisitionTimeout = 2 * time.Minute
}
driver, err := neo4j.NewDriver(uri, neo4j.BasicAuth(username, password, ""), config)
```

### 3. 处理复杂的图谱模式

对于复杂的图谱模式匹配，可以使用参数化的Cypher查询：

```go
// 定义复杂查询模板
patternQuery := `
    MATCH (formula:Formula)-[:CONTAINS]->(herb:Herb)
    WHERE formula.name = $formulaName
    WITH formula, collect(herb) AS herbs
    MATCH (herb:Herb)-[:TREATS]->(symptom:Symptom)
    WHERE herb IN herbs
    WITH formula, herbs, symptom, count(herb) AS herbCount
    WHERE herbCount >= $minHerbCount
    RETURN 
        formula.name AS formula,
        symptom.name AS symptom,
        herbCount,
        [herb IN herbs WHERE (herb)-[:TREATS]->(symptom) | herb.name] AS effectiveHerbs
    ORDER BY herbCount DESC
`

// 构建查询参数
params := map[string]interface{}{
    "formulaName": "四君子汤",
    "minHerbCount": 2,
}

// 执行查询
results, err := queryRepo.ExecuteCypher(ctx, patternQuery, params)
```

## 最佳实践

1. **使用存储库接口**：业务逻辑应依赖于接口而非具体实现，便于测试和替换底层存储

2. **结构化查询参数**：避免字符串拼接构建查询，使用参数化查询防止注入攻击

3. **适当的批处理**：对大批量操作使用批处理，但批次不要过大

4. **错误处理**：捕获并处理特定类型的存储错误，如约束冲突、超时等

5. **定期的索引维护**：根据查询模式创建和维护适当的索引

6. **监控查询性能**：使用Neo4j的查询日志和性能工具监控慢查询

7. **图谱数据模型设计**：遵循图谱设计最佳实践，合理设计节点和关系模型

8. **定义清晰的领域实体**：确保Entity对象包含足够的元数据以便于维护

9. **使用事务**：对需要保证原子性的复杂操作使用事务

10. **实现缓存策略**：对频繁访问的数据实现适当的缓存机制