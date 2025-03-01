import 'package:dartz/dartz.dart';

import '../models/knowledge_node_model.dart';
import '../models/node_relation_model.dart';

/// 知识数据源接口
abstract class KnowledgeDataSource {
  /// 获取所有知识节点
  Future<List<KnowledgeNodeModel>> getAllNodes();
  
  /// 根据ID获取知识节点
  Future<KnowledgeNodeModel> getNodeById(String nodeId);
  
  /// 按类型获取知识节点
  Future<List<KnowledgeNodeModel>> getNodesByType(String type);
  
  /// 搜索知识节点
  Future<List<KnowledgeNodeModel>> searchNodes(
    String query, {
    List<String>? types,
    int limit = 20,
    int offset = 0,
  });
  
  /// 语义搜索知识节点
  Future<List<KnowledgeNodeModel>> semanticSearchNodes(
    List<double> queryEmbedding, {
    List<String>? types,
    int limit = 20,
    double minScore = 0.6,
  });
  
  /// 保存知识节点
  Future<KnowledgeNodeModel> saveNode(KnowledgeNodeModel node);
  
  /// 更新知识节点
  Future<KnowledgeNodeModel> updateNode(KnowledgeNodeModel node);
  
  /// 删除知识节点
  Future<void> deleteNode(String nodeId);
  
  /// 获取节点的所有关系
  Future<List<NodeRelationModel>> getNodeRelations(String nodeId);
  
  /// 获取特定类型的节点关系
  Future<List<NodeRelationModel>> getRelationsByType(String relationType);
  
  /// 保存节点关系
  Future<NodeRelationModel> saveRelation(NodeRelationModel relation);
  
  /// 更新节点关系
  Future<NodeRelationModel> updateRelation(NodeRelationModel relation);
  
  /// 删除节点关系
  Future<void> deleteRelation(String relationId);
  
  /// 获取知识图谱统计信息
  Future<Map<String, dynamic>> getKnowledgeGraphStatistics();
  
  /// 生成节点嵌入向量
  Future<List<double>> generateNodeEmbedding(
    String content, {
    String title = '',
    String type = '',
  });
  
  /// 同步知识图谱数据
  Future<bool> syncKnowledgeGraph();
}