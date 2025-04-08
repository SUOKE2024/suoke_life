//------------------------------------------------------
// 知识图谱服务 - Neo4j数据库模式
// 此文件定义Neo4j数据库索引和约束
//------------------------------------------------------

// 节点约束
// 为所有节点创建ID唯一性约束
CREATE CONSTRAINT node_id_unique IF NOT EXISTS
FOR (n:Node) REQUIRE n.id IS UNIQUE;

// 为所有节点创建名称唯一性约束
CREATE CONSTRAINT node_name_unique IF NOT EXISTS
FOR (n:Node) REQUIRE n.name IS UNIQUE;

// 为TCM节点创建ID唯一性约束
CREATE CONSTRAINT tcm_node_id_unique IF NOT EXISTS
FOR (n:TCMNode) REQUIRE n.id IS UNIQUE;

// 关系ID索引（Neo4j 4.4版本不支持关系约束，只能创建索引）
CREATE INDEX relationship_id_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.id);

// 节点索引
// 为节点创建类别索引，提升按类别查询的性能
CREATE INDEX node_category_index IF NOT EXISTS
FOR (n:Node) ON (n.category);

// 为TCM节点创建子类型索引
CREATE INDEX tcm_node_subtype_index IF NOT EXISTS
FOR (n:TCMNode) ON (n.tcm_sub_type);

// 为TCM节点创建分类索引
CREATE INDEX tcm_node_classification_index IF NOT EXISTS
FOR (n:TCMNode) ON (n.classification);

// 为节点创建向量索引
CREATE INDEX node_vector_index IF NOT EXISTS
FOR (n:Node) ON (n.vector);

// 全文搜索索引
// 为节点名称创建全文搜索索引
CALL db.index.fulltext.createNodeIndex(
  "node_name_fulltext",
  ["Node"],
  ["name", "description"]
);

// 为中医节点创建全文搜索索引
CALL db.index.fulltext.createNodeIndex(
  "tcm_node_fulltext",
  ["TCMNode"],
  ["name", "description", "properties"]
);

// 关系索引
// 为关系类型创建索引
CREATE INDEX relationship_type_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.type);

// 为关系权重创建索引
CREATE INDEX relationship_weight_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.weight);

// 为关系时间戳创建索引
CREATE INDEX relationship_timestamp_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.timestamp);

// 显示数据库模式
CALL db.schema.visualization(); 