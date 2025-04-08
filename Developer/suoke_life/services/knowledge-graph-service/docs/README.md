# 索克生活知识图谱服务文档

欢迎使用索克生活知识图谱服务文档。本文档提供了知识图谱服务的设计、实现和使用指南，帮助开发者和用户了解和使用知识图谱服务的各项功能。

## 文档目录

### 核心概念与组件

- [知识图谱存储库使用指南](repositories.md) - 详细介绍知识图谱存储库的设计、实现和使用方法
- [知识图谱API服务使用指南](api.md) - 详细介绍知识图谱API的设计和使用方法
- [知识图谱向量化与相似搜索指南](vector_search.md) - 详细介绍向量化和相似搜索的实现与使用

### 数据导入工具

- [知识图谱导入工具使用指南](importers.md) - 详细介绍知识图谱数据导入工具的使用方法
- [知识图谱导入工具解析器使用指南](parsers.md) - 详细介绍导入工具支持的数据格式和解析器

## 整体架构

知识图谱服务采用分层架构设计，主要包括以下几个层次：

1. **数据层**：包含Neo4j图数据库和向量数据存储
2. **存储库层**：抽象数据访问逻辑，提供统一的数据操作接口
3. **服务层**：实现业务逻辑和数据处理服务
4. **API层**：提供RESTful接口，支持外部系统集成
5. **工具层**：提供数据导入、导出和管理工具

![知识图谱服务架构](images/kg_architecture.png)

## 快速开始

### 环境要求

- Go 1.20+
- Neo4j 5.0+
- Docker 20.10+
- 向量化服务（可选）

### 安装与配置

1. 克隆代码库

```bash
git clone https://github.com/suoke-life/knowledge-graph-service.git
cd knowledge-graph-service
```

2. 安装依赖

```bash
go mod download
```

3. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件设置必要的配置
```

4. 运行服务

```bash
go run cmd/api/main.go
```

### 使用Docker

```bash
docker-compose up -d
```

## 数据模型

知识图谱服务的核心数据模型包括：

### 节点类型

- **Herb**: 中药节点
- **Formula**: 方剂节点
- **Symptom**: 症状节点
- **Pattern**: 证候节点
- **Effect**: 功效节点
- **Category**: 分类节点
- **KnowledgeNode**: 知识节点

### 关系类型

- **CONTAINS**: 包含关系（如方剂包含中药）
- **TREATS**: 治疗关系（如中药治疗症状）
- **BELONGS_TO**: 归属关系（如中药属于某分类）
- **HAS_PROPERTY**: 具有属性（如中药具有某功效）
- **SIMILAR_TO**: 相似关系（如中药之间的相似性）

## 核心功能

### 知识管理

- 中医药知识录入、存储和管理
- 知识实体和关系的建立与维护
- 知识图谱的扩展和更新

### 数据查询

- 基于实体和关系的图谱查询
- 复杂路径和模式查询
- 自定义Cypher查询

### 向量搜索

- 内容向量化和索引
- 语义相似搜索
- 多模态内容检索

### 数据导入/导出

- 多格式数据导入
- 批量数据处理
- 知识图谱导出和备份

## 集成指南

### 与前端应用集成

前端应用可以通过RESTful API与知识图谱服务进行交互：

```javascript
// 示例：查询中药信息
async function getHerbInfo(herbName) {
  const response = await fetch(`https://kg-api.suoke.life/api/v1/nodes/search?label=Herb&property=name&value=${encodeURIComponent(herbName)}`);
  const data = await response.json();
  return data;
}
```

### 与RAG系统集成

知识图谱服务可以作为RAG系统的知识源：

```python
# 示例：从知识图谱获取上下文
def get_knowledge_context(query):
    # 向量化查询
    response = requests.post(
        "https://kg-api.suoke.life/api/v1/vectors/text-search",
        json={
            "text": query,
            "label": "KnowledgeNode",
            "field": "content_vector",
            "limit": 10
        }
    )
    results = response.json()["results"]
    
    # 构建上下文
    context = "\n\n".join([node["properties"]["content"] for node in results])
    return context
```

## 常见问题

### Q: 如何优化知识图谱的查询性能？

A: 可以通过创建适当的索引、优化查询模式、使用缓存和监控慢查询来提高性能。详细请参考[知识图谱存储库使用指南](repositories.md)中的性能优化部分。

### Q: 如何处理大规模数据导入？

A: 建议使用批量导入工具，设置合适的批处理大小，并考虑使用并行处理和事务管理。详细请参考[知识图谱导入工具使用指南](importers.md)。

### Q: 向量搜索结果不理想怎么办？

A: 可以尝试使用不同的向量模型、调整索引参数、优化内容预处理或结合传统过滤条件。详细请参考[知识图谱向量化与相似搜索指南](vector_search.md)中的常见问题部分。

## 贡献指南

我们欢迎社区贡献，如果您有兴趣参与开发，请遵循以下步骤：

1. Fork项目仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 联系我们

- 项目负责人：开发团队
- 邮箱：dev@suoke.life
- 网站：[https://suoke.life](https://suoke.life)

## 许可证

索克生活知识图谱服务采用MIT许可证 - 详见 [LICENSE](../LICENSE) 文件