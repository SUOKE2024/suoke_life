# 知识图谱功能文档

## 简介

Med Knowledge Service提供强大的知识图谱功能，支持中医知识的可视化呈现、关系探索和高级查询。知识图谱将中医传统理论的体质、症状、证型等概念与现代医学的生物标志物、疾病等实体进行关联，形成结构化的知识网络，为索克生活平台的智能体提供知识支持。

## 核心特性

- **知识图谱统计**：了解知识库规模和构成
- **知识图谱可视化**：直观展示知识实体和关系
- **路径查找**：发现实体间的隐含关系
- **节点关系查询**：探索特定节点的关联信息
- **知识子图**：以特定实体为中心获取相关知识网络
- **高级Cypher查询**：支持专业用户进行自定义查询

## API接口

### 知识图谱统计

获取整个知识图谱的统计信息，包括节点数量、关系数量、各类型节点和关系的分布情况。

```
GET /api/v1/graph/statistics
```

返回示例：

```json
{
  "node_count": 1245,
  "relationship_count": 3567,
  "node_types": [
    {"type": "Constitution", "count": 9},
    {"type": "Syndrome", "count": 87},
    {"type": "Biomarker", "count": 156},
    {"type": "WesternDisease", "count": 304}
  ],
  "relationship_types": [
    {"type": "INDICATES", "count": 423},
    {"type": "CORRELATES_WITH", "count": 756},
    {"type": "HAS_SYMPTOM", "count": 1203}
  ]
}
```

### 知识图谱可视化

获取知识图谱可视化数据，支持按节点类型和关系类型进行过滤，适用于前端图形化展示。

```
GET /api/v1/graph/visualization?limit=100&node_types[]=Constitution&node_types[]=Syndrome
```

| 参数 | 说明 |
|-----|------|
| limit | 节点限制数量，默认100 |
| node_types | 节点类型过滤，可选 |
| relationship_types | 关系类型过滤，可选 |

返回格式包含节点和链接信息，适合直接用于图形可视化库（如D3.js、ECharts）。

### 路径查找

查找两个节点之间的所有路径，帮助发现实体间的隐含关系。

```
GET /api/v1/graph/paths?start_node_id=123&end_node_id=456&max_depth=3
```

| 参数 | 说明 |
|-----|------|
| start_node_id | 起始节点ID |
| end_node_id | 目标节点ID |
| max_depth | 最大深度，默认4 |

可以发现如"体质-症状-证型-疾病"这样的复杂关联路径。

### 节点关系查询

获取特定节点的所有关系和相关节点。

```
GET /api/v1/graph/nodes/{node_id}/relationships?direction=outgoing&limit=20
```

| 参数 | 说明 |
|-----|------|
| node_id | 节点ID |
| direction | 关系方向：outgoing（出），incoming（入），both（双向，默认） |
| relationship_types | 关系类型过滤，可选 |
| limit | 返回关系数量限制，默认20 |

### 知识子图

获取以特定实体为中心的知识子图，包含相关的所有节点和关系。

```
GET /api/v1/graph/subgraph/{entity_type}/{entity_id}?depth=2&max_nodes=50
```

| 参数 | 说明 |
|-----|------|
| entity_type | 实体类型，如Constitution |
| entity_id | 实体ID |
| depth | 搜索深度，默认2 |
| max_nodes | 最大节点数，默认50 |

适用于探索某个概念（如"气虚质"）相关的所有知识点。

### 获取实体邻居

获取某个实体的直接相邻节点。

```
GET /api/v1/graph/entities/{entity_type}/{entity_id}/neighbors?neighbor_types[]=Biomarker
```

| 参数 | 说明 |
|-----|------|
| entity_type | 实体类型 |
| entity_id | 实体ID |
| neighbor_types | 邻居类型过滤，可选 |

### 获取相关实体

获取与指定实体相关的特定类型的实体列表。

```
GET /api/v1/graph/entities/{entity_type}/{entity_id}/related/{target_type}?relationship_type=INDICATES
```

| 参数 | 说明 |
|-----|------|
| entity_type | 源实体类型 |
| entity_id | 源实体ID |
| target_type | 目标实体类型 |
| relationship_type | 关系类型过滤，可选 |
| limit | 返回数量限制，默认20 |

适用于查询如"与气虚质相关的所有生物标志物"。

### 高级Cypher查询

支持高级用户使用Neo4j的Cypher查询语言进行自定义查询。

```
POST /api/v1/graph/cypher
```

请求体：

```json
{
  "query": "MATCH (c:Constitution)-[:TENDS_TO_DEVELOP]->(s:Syndrome) WHERE c.name = '气虚质' RETURN s.name, s.description",
  "params": {
    "constitutionName": "气虚质"
  }
}
```

**注意**：出于安全考虑，仅支持读取操作，不支持写入、删除等修改操作。

## gRPC接口

知识图谱功能同样通过gRPC接口提供，详见`api/grpc/knowledge.proto`文件中的定义：

```protobuf
service MedKnowledgeService {
  // 知识图谱服务
  rpc GetGraphStatistics(GetGraphStatisticsRequest) returns (GraphStatistics);
  rpc GetGraphVisualizationData(GetGraphVisualizationDataRequest) returns (GraphVisualizationData);
  rpc FindPathBetweenNodes(FindPathBetweenNodesRequest) returns (PathsResult);
  rpc GetNodeRelationships(GetNodeRelationshipsRequest) returns (NodeRelationshipsResult);
  rpc GetKnowledgeSubgraph(GetKnowledgeSubgraphRequest) returns (Subgraph);
  rpc GetEntityNeighbors(GetEntityNeighborsRequest) returns (EntityNeighborsResult);
  rpc GetRelatedEntities(GetRelatedEntitiesRequest) returns (RelatedEntitiesResult);
}
```

## 使用示例

### 前端可视化示例

使用D3.js实现知识图谱可视化：

```javascript
// 获取知识图谱可视化数据
async function fetchGraphData() {
  const response = await fetch('/api/v1/graph/visualization?limit=100');
  return await response.json();
}

// 使用D3.js渲染力导向图
function renderGraph(data) {
  const svg = d3.select("#graph-container")
    .append("svg")
    .attr("width", width)
    .attr("height", height);
    
  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2));
    
  // 绘制链接
  const link = svg.append("g")
    .selectAll("line")
    .data(data.links)
    .enter().append("line")
    .attr("stroke", "#999")
    .attr("stroke-width", 1);
    
  // 绘制节点
  const node = svg.append("g")
    .selectAll("circle")
    .data(data.nodes)
    .enter().append("circle")
    .attr("r", 5)
    .attr("fill", d => getColorByType(d.type))
    .call(drag(simulation));
    
  // 节点标签
  const text = svg.append("g")
    .selectAll("text")
    .data(data.nodes)
    .enter().append("text")
    .text(d => d.label)
    .attr("font-size", 10)
    .attr("dx", 8)
    .attr("dy", ".35em");
    
  // 更新位置
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    
    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
      
    text
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  });
}

// 初始化
fetchGraphData().then(data => renderGraph(data));
```

### 智能体查询示例

索克生活平台的智能体（如小艾）可以使用知识图谱API来回答用户查询：

```python
async def answer_tcm_query(query, knowledge_service):
    """使用知识图谱回答中医相关查询"""
    # 例如：用户问"气虚质容易发展为什么证型"
    
    # 1. 查找气虚质实体
    constitution_id = await find_entity_by_name("气虚质", "Constitution")
    
    # 2. 获取相关证型
    syndromes = await knowledge_service.get_related_entities(
        "Constitution", 
        constitution_id, 
        "Syndrome", 
        "TENDS_TO_DEVELOP", 
        10
    )
    
    # 3. 构建回答
    syndrome_names = [s["name"] for s in syndromes]
    answer = f"气虚质的人容易发展为以下证型：{', '.join(syndrome_names)}。"
    
    return answer
```

## 高级应用

1. **多因素关联分析**：发现体质-症状-证型-生物标志物的多重关联
2. **个性化健康路径分析**：基于用户体质特征，预测可能的健康变化路径
3. **知识图谱推理**：通过现有的知识关系进行知识图谱推理，发现新的知识关联

## 技术实现

知识图谱功能基于Neo4j图数据库实现，主要使用以下技术：

- **Neo4j**：图数据库平台
- **Cypher**：Neo4j的查询语言
- **APOC**：Neo4j的扩展库，提供高级查询能力
- **D3.js/ECharts**：前端可视化库

## 未来扩展计划

1. **知识图谱嵌入**：实现基于TransE、RotatE等模型的知识图谱嵌入，支持相似度搜索
2. **本体推理**：基于OWL本体逻辑实现自动化推理
3. **自动知识抽取**：从医学文献自动抽取知识，扩充知识图谱
4. **多模态知识融合**：整合图像、文本等多模态数据到知识图谱中 