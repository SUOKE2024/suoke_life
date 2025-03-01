import 'dart:convert';
import 'package:logger/logger.dart';
import 'package:uuid/uuid.dart';

import '../../../core/database/database_helper.dart';
import '../../../core/database/database_schema.dart';
import '../../../core/error/exceptions.dart';
import '../../models/knowledge_node_model.dart';
import '../../models/node_relation_model.dart';
import '../knowledge_data_source.dart';

/// 知识图谱本地数据源实现
class KnowledgeLocalDataSource implements KnowledgeDataSource {
  final DatabaseHelper _databaseHelper;
  final Logger _logger;
  final Uuid _uuid = Uuid();
  
  KnowledgeLocalDataSource({
    required DatabaseHelper databaseHelper,
    required Logger logger,
  })  : _databaseHelper = databaseHelper,
        _logger = logger;
  
  @override
  Future<List<KnowledgeNodeModel>> getAllNodes() async {
    try {
      final result = await _databaseHelper.queryAll(DatabaseSchema.tableKnowledgeNodes);
      return result.map((map) => _mapToKnowledgeNodeModel(map)).toList();
    } catch (e) {
      _logger.e('获取所有知识节点失败', error: e);
      throw CacheException(message: '获取所有知识节点失败: $e');
    }
  }
  
  @override
  Future<KnowledgeNodeModel> getNodeById(String nodeId) async {
    try {
      final result = await _databaseHelper.queryOne(
        DatabaseSchema.tableKnowledgeNodes,
        where: 'id = ?',
        whereArgs: [nodeId],
      );
      
      if (result == null) {
        throw CacheException(message: '知识节点不存在: $nodeId');
      }
      
      return _mapToKnowledgeNodeModel(result);
    } catch (e) {
      _logger.e('获取知识节点失败: $nodeId', error: e);
      throw CacheException(message: '获取知识节点失败: $e');
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> getNodesByType(String type) async {
    try {
      final result = await _databaseHelper.query(
        DatabaseSchema.tableKnowledgeNodes,
        where: 'type = ?',
        whereArgs: [type],
      );
      
      return result.map((map) => _mapToKnowledgeNodeModel(map)).toList();
    } catch (e) {
      _logger.e('获取类型知识节点失败: $type', error: e);
      throw CacheException(message: '获取类型知识节点失败: $e');
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> searchNodes(
    String query, {
    List<String>? types,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      String whereClause = 'title LIKE ? OR description LIKE ?';
      List<dynamic> whereArgs = ['%$query%', '%$query%'];
      
      if (types != null && types.isNotEmpty) {
        whereClause += ' AND type IN (${List.filled(types.length, '?').join(',')})';
        whereArgs.addAll(types);
      }
      
      final result = await _databaseHelper.query(
        DatabaseSchema.tableKnowledgeNodes,
        where: whereClause,
        whereArgs: whereArgs,
        limit: limit,
        offset: offset,
      );
      
      return result.map((map) => _mapToKnowledgeNodeModel(map)).toList();
    } catch (e) {
      _logger.e('搜索知识节点失败: $query', error: e);
      throw CacheException(message: '搜索知识节点失败: $e');
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> semanticSearchNodes(
    List<double> queryEmbedding, {
    List<String>? types,
    int limit = 20,
    double minScore = 0.6,
  }) async {
    // 本地数据源不支持向量搜索，返回空结果
    return [];
  }
  
  @override
  Future<KnowledgeNodeModel> saveNode(KnowledgeNodeModel node) async {
    try {
      final nodeMap = _knowledgeNodeModelToMap(node);
      
      // 使用新的ID
      final newId = _uuid.v4();
      final now = DateTime.now().millisecondsSinceEpoch;
      
      final newNodeMap = {
        ...nodeMap,
        'id': newId,
        'created_at': now,
        'updated_at': now,
      };
      
      await _databaseHelper.insert(
        DatabaseSchema.tableKnowledgeNodes,
        newNodeMap,
      );
      
      return _mapToKnowledgeNodeModel(newNodeMap);
    } catch (e) {
      _logger.e('保存知识节点失败', error: e);
      throw CacheException(message: '保存知识节点失败: $e');
    }
  }
  
  @override
  Future<KnowledgeNodeModel> updateNode(KnowledgeNodeModel node) async {
    try {
      final nodeMap = _knowledgeNodeModelToMap(node);
      
      // 更新时间
      final now = DateTime.now().millisecondsSinceEpoch;
      final updatedNodeMap = {
        ...nodeMap,
        'updated_at': now,
      };
      
      await _databaseHelper.update(
        DatabaseSchema.tableKnowledgeNodes,
        updatedNodeMap,
        where: 'id = ?',
        whereArgs: [node.id],
      );
      
      return _mapToKnowledgeNodeModel(updatedNodeMap);
    } catch (e) {
      _logger.e('更新知识节点失败: ${node.id}', error: e);
      throw CacheException(message: '更新知识节点失败: $e');
    }
  }
  
  @override
  Future<void> deleteNode(String nodeId) async {
    try {
      // 删除节点
      await _databaseHelper.delete(
        DatabaseSchema.tableKnowledgeNodes,
        where: 'id = ?',
        whereArgs: [nodeId],
      );
      
      // 删除相关的关系
      await _databaseHelper.delete(
        DatabaseSchema.tableNodeRelations,
        where: 'source_node_id = ? OR target_node_id = ?',
        whereArgs: [nodeId, nodeId],
      );
    } catch (e) {
      _logger.e('删除知识节点失败: $nodeId', error: e);
      throw CacheException(message: '删除知识节点失败: $e');
    }
  }
  
  @override
  Future<List<NodeRelationModel>> getNodeRelations(String nodeId) async {
    try {
      final result = await _databaseHelper.query(
        DatabaseSchema.tableNodeRelations,
        where: 'source_node_id = ? OR target_node_id = ?',
        whereArgs: [nodeId, nodeId],
      );
      
      return result.map((map) => _mapToNodeRelationModel(map)).toList();
    } catch (e) {
      _logger.e('获取节点关系失败: $nodeId', error: e);
      throw CacheException(message: '获取节点关系失败: $e');
    }
  }
  
  @override
  Future<List<NodeRelationModel>> getRelationsByType(String relationType) async {
    try {
      final result = await _databaseHelper.query(
        DatabaseSchema.tableNodeRelations,
        where: 'relation_type = ?',
        whereArgs: [relationType],
      );
      
      return result.map((map) => _mapToNodeRelationModel(map)).toList();
    } catch (e) {
      _logger.e('获取关系类型失败: $relationType', error: e);
      throw CacheException(message: '获取关系类型失败: $e');
    }
  }
  
  @override
  Future<NodeRelationModel> saveRelation(NodeRelationModel relation) async {
    try {
      final relationMap = _nodeRelationModelToMap(relation);
      
      // 使用新的ID
      final newId = _uuid.v4();
      
      final newRelationMap = {
        ...relationMap,
        'id': newId,
      };
      
      await _databaseHelper.insert(
        DatabaseSchema.tableNodeRelations,
        newRelationMap,
      );
      
      return _mapToNodeRelationModel(newRelationMap);
    } catch (e) {
      _logger.e('保存节点关系失败', error: e);
      throw CacheException(message: '保存节点关系失败: $e');
    }
  }
  
  @override
  Future<NodeRelationModel> updateRelation(NodeRelationModel relation) async {
    try {
      final relationMap = _nodeRelationModelToMap(relation);
      
      await _databaseHelper.update(
        DatabaseSchema.tableNodeRelations,
        relationMap,
        where: 'id = ?',
        whereArgs: [relation.id],
      );
      
      return relation;
    } catch (e) {
      _logger.e('更新节点关系失败: ${relation.id}', error: e);
      throw CacheException(message: '更新节点关系失败: $e');
    }
  }
  
  @override
  Future<void> deleteRelation(String relationId) async {
    try {
      await _databaseHelper.delete(
        DatabaseSchema.tableNodeRelations,
        where: 'id = ?',
        whereArgs: [relationId],
      );
    } catch (e) {
      _logger.e('删除节点关系失败: $relationId', error: e);
      throw CacheException(message: '删除节点关系失败: $e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> getKnowledgeGraphStatistics() async {
    try {
      // 获取节点数量
      final nodeCountResult = await _databaseHelper.rawQuery(
        'SELECT COUNT(*) as count FROM ${DatabaseSchema.tableKnowledgeNodes}',
      );
      final nodeCount = nodeCountResult.first['count'] as int;
      
      // 获取关系数量
      final relationCountResult = await _databaseHelper.rawQuery(
        'SELECT COUNT(*) as count FROM ${DatabaseSchema.tableNodeRelations}',
      );
      final relationCount = relationCountResult.first['count'] as int;
      
      // 获取节点类型分布
      final nodeTypesResult = await _databaseHelper.rawQuery(
        'SELECT type, COUNT(*) as count FROM ${DatabaseSchema.tableKnowledgeNodes} GROUP BY type',
      );
      final nodeTypes = nodeTypesResult.map((row) => {
        'type': row['type'],
        'count': row['count'],
      }).toList();
      
      // 获取关系类型分布
      final relationTypesResult = await _databaseHelper.rawQuery(
        'SELECT relation_type, COUNT(*) as count FROM ${DatabaseSchema.tableNodeRelations} GROUP BY relation_type',
      );
      final relationTypes = relationTypesResult.map((row) => {
        'type': row['relation_type'],
        'count': row['count'],
      }).toList();
      
      return {
        'nodeCount': nodeCount,
        'relationCount': relationCount,
        'nodeTypes': nodeTypes,
        'relationTypes': relationTypes,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      _logger.e('获取知识图谱统计失败', error: e);
      throw CacheException(message: '获取知识图谱统计失败: $e');
    }
  }
  
  @override
  Future<List<double>> generateNodeEmbedding(
    String content, {
    String title = '',
    String type = '',
  }) async {
    // 本地数据源不支持生成嵌入向量
    throw UnsupportedError('本地数据源不支持生成嵌入向量');
  }
  
  @override
  Future<bool> syncKnowledgeGraph() async {
    // 本地数据源不支持同步
    return false;
  }
  
  // 辅助方法：将数据库行映射为知识节点模型
  KnowledgeNodeModel _mapToKnowledgeNodeModel(Map<String, dynamic> map) {
    return KnowledgeNodeModel(
      id: map['id'] as String,
      type: map['type'] as String,
      title: map['title'] as String,
      description: map['description'] as String?,
      content: map['content'] as String?,
      createdAt: map['created_at'] as int,
      updatedAt: map['updated_at'] as int,
      metadata: map['metadata'] != null ? map['metadata'] as String : null,
      language: map['language'] as String? ?? 'zh-CN',
    );
  }
  
  // 辅助方法：将知识节点模型转换为数据库行
  Map<String, dynamic> _knowledgeNodeModelToMap(KnowledgeNodeModel model) {
    return {
      'id': model.id,
      'type': model.type,
      'title': model.title,
      'description': model.description,
      'content': model.content,
      'created_at': model.createdAt,
      'updated_at': model.updatedAt,
      'metadata': model.metadata,
      'language': model.language,
    };
  }
  
  // 辅助方法：将数据库行映射为节点关系模型
  NodeRelationModel _mapToNodeRelationModel(Map<String, dynamic> map) {
    return NodeRelationModel(
      id: map['id'] as String,
      sourceNodeId: map['source_node_id'] as String,
      targetNodeId: map['target_node_id'] as String,
      relationType: map['relation_type'] as String,
      weight: map['weight'] != null ? (map['weight'] as num).toDouble() : null,
      metadata: map['metadata'] as String?,
    );
  }
  
  // 辅助方法：将节点关系模型转换为数据库行
  Map<String, dynamic> _nodeRelationModelToMap(NodeRelationModel model) {
    return {
      'id': model.id,
      'source_node_id': model.sourceNodeId,
      'target_node_id': model.targetNodeId,
      'relation_type': model.relationType,
      'weight': model.weight,
      'metadata': model.metadata,
    };
  }
}