import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
// import 'package:get_it/get_it.dart';

import '../base/agent.dart';
import '../base/agent_event.dart';
import '../base/agent_interface.dart';
import '../security/security_framework.dart';
import '../learning/learning_system.dart';
import 'health_management_agent.dart';
import '../rag/rag_service.dart';
import '../../providers/ai_core_providers.dart';

/// 知识图谱节点类型
enum GraphNodeType {
  /// 概念节点
  concept,
  
  /// 实体节点
  entity,
  
  /// 症状节点
  symptom,
  
  /// 疾病节点
  disease,
  
  /// 治疗方法节点
  treatment,
  
  /// 药物节点
  medicine,
  
  /// 食物节点
  food,
  
  /// 营养素节点
  nutrient,
  
  /// 运动节点
  exercise,
}

/// 知识图谱关系类型
enum GraphRelationType {
  /// 上位概念关系
  isA,
  
  /// 部分整体关系
  partOf,
  
  /// 具有属性关系
  hasProperty,
  
  /// 引起症状关系
  causes,
  
  /// 治疗疾病关系
  treats,
  
  /// 预防疾病关系
  prevents,
  
  /// 加重症状关系
  worsens,
  
  /// 缓解症状关系
  alleviates,
  
  /// 含有成分关系
  contains,
  
  /// 功效作用关系
  affects,
  
  /// 相互作用关系
  interactsWith,
  
  /// 禁忌关系
  contraindicatedWith,
}

/// 知识图谱来源
enum GraphDataSource {
  /// 中医理论
  traditionalChineseMedicine,
  
  /// 西医理论
  westernMedicine,
  
  /// 医学研究
  medicalResearch,
  
  /// 营养学
  nutritionScience,
  
  /// 药理学
  pharmacology,
  
  /// 用户数据
  userData,
  
  /// 外部API
  externalApi,
}

/// 知识图谱可信度
enum ConfidenceLevel {
  /// 低可信度
  low,
  
  /// 中等可信度
  medium,
  
  /// 高可信度
  high,
  
  /// 确定事实
  certain,
}

/// 知识图谱节点
class GraphNode {
  /// 节点ID
  final String id;
  
  /// 节点类型
  final GraphNodeType type;
  
  /// 节点名称
  final String name;
  
  /// 节点描述
  final String? description;
  
  /// 节点属性
  final Map<String, dynamic> attributes;
  
  /// 节点来源
  final GraphDataSource source;
  
  /// 可信度
  final ConfidenceLevel confidence;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  GraphNode({
    required this.id,
    required this.type,
    required this.name,
    this.description,
    Map<String, dynamic>? attributes,
    required this.source,
    required this.confidence,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : 
    attributes = attributes ?? {},
    createdAt = createdAt ?? DateTime.now(),
    updatedAt = updatedAt ?? DateTime.now();
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'type': type.toString(),
      'name': name,
      'description': description,
      'attributes': attributes,
      'source': source.toString(),
      'confidence': confidence.toString(),
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }
  
  /// 从Map创建
  factory GraphNode.fromMap(Map<String, dynamic> map) {
    return GraphNode(
      id: map['id'],
      type: GraphNodeType.values.firstWhere(
        (e) => e.toString() == map['type'],
        orElse: () => GraphNodeType.concept,
      ),
      name: map['name'],
      description: map['description'],
      attributes: map['attributes'] ?? {},
      source: GraphDataSource.values.firstWhere(
        (e) => e.toString() == map['source'],
        orElse: () => GraphDataSource.traditionalChineseMedicine,
      ),
      confidence: ConfidenceLevel.values.firstWhere(
        (e) => e.toString() == map['confidence'],
        orElse: () => ConfidenceLevel.medium,
      ),
      createdAt: DateTime.parse(map['createdAt']),
      updatedAt: DateTime.parse(map['updatedAt']),
    );
  }
}

/// 知识图谱关系
class GraphRelation {
  /// 关系ID
  final String id;
  
  /// 源节点ID
  final String sourceNodeId;
  
  /// 目标节点ID
  final String targetNodeId;
  
  /// 关系类型
  final GraphRelationType type;
  
  /// 关系描述
  final String? description;
  
  /// 关系属性
  final Map<String, dynamic> attributes;
  
  /// 数据来源
  final GraphDataSource source;
  
  /// 可信度
  final ConfidenceLevel confidence;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  GraphRelation({
    required this.id,
    required this.sourceNodeId,
    required this.targetNodeId,
    required this.type,
    this.description,
    Map<String, dynamic>? attributes,
    required this.source,
    required this.confidence,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : 
    attributes = attributes ?? {},
    createdAt = createdAt ?? DateTime.now(),
    updatedAt = updatedAt ?? DateTime.now();
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'sourceNodeId': sourceNodeId,
      'targetNodeId': targetNodeId,
      'type': type.toString(),
      'description': description,
      'attributes': attributes,
      'source': source.toString(),
      'confidence': confidence.toString(),
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }
  
  /// 从Map创建
  factory GraphRelation.fromMap(Map<String, dynamic> map) {
    return GraphRelation(
      id: map['id'],
      sourceNodeId: map['sourceNodeId'],
      targetNodeId: map['targetNodeId'],
      type: GraphRelationType.values.firstWhere(
        (e) => e.toString() == map['type'],
        orElse: () => GraphRelationType.isA,
      ),
      description: map['description'],
      attributes: map['attributes'] ?? {},
      source: GraphDataSource.values.firstWhere(
        (e) => e.toString() == map['source'],
        orElse: () => GraphDataSource.traditionalChineseMedicine,
      ),
      confidence: ConfidenceLevel.values.firstWhere(
        (e) => e.toString() == map['confidence'],
        orElse: () => ConfidenceLevel.medium,
      ),
      createdAt: DateTime.parse(map['createdAt']),
      updatedAt: DateTime.parse(map['updatedAt']),
    );
  }
}

/// 知识图谱查询结果
class GraphQueryResult {
  /// 节点列表
  final List<GraphNode> nodes;
  
  /// 关系列表
  final List<GraphRelation> relations;
  
  /// 查询时间
  final DateTime timestamp;
  
  /// 查询摘要
  final String? summary;
  
  GraphQueryResult({
    required this.nodes,
    required this.relations,
    DateTime? timestamp,
    this.summary,
  }) : timestamp = timestamp ?? DateTime.now();
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'nodes': nodes.map((n) => n.toMap()).toList(),
      'relations': relations.map((r) => r.toMap()).toList(),
      'timestamp': timestamp.toIso8601String(),
      'summary': summary,
    };
  }
}

/// 知识图谱路径
class GraphPath {
  /// 路径ID
  final String id;
  
  /// 路径中的节点ID列表
  final List<String> nodeIds;
  
  /// 路径中的关系ID列表
  final List<String> relationIds;
  
  /// 路径描述
  final String? description;
  
  /// 创建时间
  final DateTime createdAt;
  
  GraphPath({
    required this.id,
    required this.nodeIds,
    required this.relationIds,
    this.description,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();
  
  /// 路径长度
  int get length => relationIds.length;
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'nodeIds': nodeIds,
      'relationIds': relationIds,
      'description': description,
      'createdAt': createdAt.toIso8601String(),
    };
  }
}

/// 知识图谱代理接口
abstract class KnowledgeGraphAgent extends AgentInterface {
  /// 代理ID
  String get id;
  
  /// 代理名称
  String get name;
  
  /// 添加节点
  Future<String> addNode(GraphNode node);
  
  /// 批量添加节点
  Future<List<String>> addNodes(List<GraphNode> nodes);
  
  /// 添加关系
  Future<String> addRelation(GraphRelation relation);
  
  /// 批量添加关系
  Future<List<String>> addRelations(List<GraphRelation> relations);
  
  /// 更新节点
  Future<void> updateNode(GraphNode node);
  
  /// 更新关系
  Future<void> updateRelation(GraphRelation relation);
  
  /// 删除节点
  Future<void> deleteNode(String nodeId);
  
  /// 删除关系
  Future<void> deleteRelation(String relationId);
  
  /// 获取节点
  Future<GraphNode?> getNode(String nodeId);
  
  /// 获取关系
  Future<GraphRelation?> getRelation(String relationId);
  
  /// 查找节点
  Future<List<GraphNode>> findNodes({
    String? name,
    GraphNodeType? type,
    Map<String, dynamic>? attributes,
    GraphDataSource? source,
  });
  
  /// 查找关系
  Future<List<GraphRelation>> findRelations({
    String? sourceNodeId,
    String? targetNodeId,
    GraphRelationType? type,
    GraphDataSource? source,
  });
  
  /// 获取节点的出边关系
  Future<List<GraphRelation>> getOutgoingRelations(String nodeId);
  
  /// 获取节点的入边关系
  Future<List<GraphRelation>> getIncomingRelations(String nodeId);
  
  /// 获取两节点间的最短路径
  Future<GraphPath?> findShortestPath(String sourceNodeId, String targetNodeId);
  
  /// 执行图谱查询
  Future<GraphQueryResult> query(String queryText);
  
  /// 基于文本自动提取知识
  Future<GraphQueryResult> extractKnowledge(String text);
  
  /// 合并知识图谱
  Future<void> mergeGraphs(GraphQueryResult otherGraph);
  
  /// 生成知识图谱摘要
  Future<String> generateGraphSummary(GraphQueryResult graph);
  
  /// 可视化知识图谱
  Future<Map<String, dynamic>> visualizeGraph(GraphQueryResult graph);
}

/// 知识图谱代理实现
class KnowledgeGraphAgentImpl extends Agent implements KnowledgeGraphAgent {
  final SecurityFramework _securityFramework;
  final LearningSystem _learningSystem;
  final RAGService _ragService;
  
  // 存储
  final Map<String, GraphNode> _nodes = {};
  final Map<String, GraphRelation> _relations = {};
  
  // 统计
  int _totalEntitiesCreated = 0;
  int _totalRelationshipsCreated = 0;
  int _totalQueries = 0;
  
  KnowledgeGraphAgentImpl({
    required SecurityFramework securityFramework,
    required LearningSystem learningSystem,
    required RAGService ragService,
  }) : 
    _securityFramework = securityFramework,
    _learningSystem = learningSystem,
    _ragService = ragService,
    super(id: 'knowledge_graph_agent');
  
  @override
  String get id => id;
  
  @override
  String get name => name;
  
  @override
  Future<String> addNode(GraphNode node) async {
    _nodes[node.id] = node;
    
    // 记录学习数据
    await _learningSystem.collectData(LearningDataItem(
      id: node.id,
      type: LearningDataType.structured,
      source: LearningDataSource.agentGenerated,
      content: node.toMap(),
      agentId: id,
    ));
    
    return node.id;
  }
  
  @override
  Future<List<String>> addNodes(List<GraphNode> nodes) async {
    final ids = <String>[];
    
    for (final node in nodes) {
      ids.add(await addNode(node));
    }
    
    return ids;
  }
  
  @override
  Future<String> addRelation(GraphRelation relation) async {
    // 确保源节点和目标节点存在
    if (!_nodes.containsKey(relation.sourceNodeId)) {
      throw Exception('Source node not found: ${relation.sourceNodeId}');
    }
    
    if (!_nodes.containsKey(relation.targetNodeId)) {
      throw Exception('Target node not found: ${relation.targetNodeId}');
    }
    
    _relations[relation.id] = relation;
    
    // 记录学习数据
    await _learningSystem.collectData(LearningDataItem(
      id: relation.id,
      type: LearningDataType.structured,
      source: LearningDataSource.agentGenerated,
      content: relation.toMap(),
      agentId: id,
    ));
    
    return relation.id;
  }
  
  @override
  Future<List<String>> addRelations(List<GraphRelation> relations) async {
    final ids = <String>[];
    
    for (final relation in relations) {
      ids.add(await addRelation(relation));
    }
    
    return ids;
  }
  
  @override
  Future<void> updateNode(GraphNode node) async {
    if (!_nodes.containsKey(node.id)) {
      throw Exception('Node not found: ${node.id}');
    }
    
    _nodes[node.id] = node;
  }
  
  @override
  Future<void> updateRelation(GraphRelation relation) async {
    if (!_relations.containsKey(relation.id)) {
      throw Exception('Relation not found: ${relation.id}');
    }
    
    _relations[relation.id] = relation;
  }
  
  @override
  Future<void> deleteNode(String nodeId) async {
    if (!_nodes.containsKey(nodeId)) {
      throw Exception('Node not found: $nodeId');
    }
    
    // 删除与该节点相关的所有关系
    _relations.removeWhere((_, relation) => 
      relation.sourceNodeId == nodeId || relation.targetNodeId == nodeId
    );
    
    _nodes.remove(nodeId);
  }
  
  @override
  Future<void> deleteRelation(String relationId) async {
    if (!_relations.containsKey(relationId)) {
      throw Exception('Relation not found: $relationId');
    }
    
    _relations.remove(relationId);
  }
  
  @override
  Future<GraphNode?> getNode(String nodeId) async {
    return _nodes[nodeId];
  }
  
  @override
  Future<GraphRelation?> getRelation(String relationId) async {
    return _relations[relationId];
  }
  
  @override
  Future<List<GraphNode>> findNodes({
    String? name,
    GraphNodeType? type,
    Map<String, dynamic>? attributes,
    GraphDataSource? source,
  }) async {
    return _nodes.values.where((node) {
      if (name != null && !node.name.toLowerCase().contains(name.toLowerCase())) {
        return false;
      }
      
      if (type != null && node.type != type) {
        return false;
      }
      
      if (source != null && node.source != source) {
        return false;
      }
      
      if (attributes != null) {
        for (final entry in attributes.entries) {
          if (!node.attributes.containsKey(entry.key) || 
              node.attributes[entry.key] != entry.value) {
            return false;
          }
        }
      }
      
      return true;
    }).toList();
  }
  
  @override
  Future<List<GraphRelation>> findRelations({
    String? sourceNodeId,
    String? targetNodeId,
    GraphRelationType? type,
    GraphDataSource? source,
  }) async {
    return _relations.values.where((relation) {
      if (sourceNodeId != null && relation.sourceNodeId != sourceNodeId) {
        return false;
      }
      
      if (targetNodeId != null && relation.targetNodeId != targetNodeId) {
        return false;
      }
      
      if (type != null && relation.type != type) {
        return false;
      }
      
      if (source != null && relation.source != source) {
        return false;
      }
      
      return true;
    }).toList();
  }
  
  @override
  Future<List<GraphRelation>> getOutgoingRelations(String nodeId) async {
    return findRelations(sourceNodeId: nodeId);
  }
  
  @override
  Future<List<GraphRelation>> getIncomingRelations(String nodeId) async {
    return findRelations(targetNodeId: nodeId);
  }
  
  @override
  Future<GraphPath?> findShortestPath(String sourceNodeId, String targetNodeId) async {
    // 检查节点是否存在
    if (!_nodes.containsKey(sourceNodeId)) {
      throw Exception('Source node not found: $sourceNodeId');
    }
    
    if (!_nodes.containsKey(targetNodeId)) {
      throw Exception('Target node not found: $targetNodeId');
    }
    
    // 实现广度优先搜索算法寻找最短路径
    final queue = <List<String>>[];
    final visited = <String>{};
    final pathRelations = <String, String>{}; // 节点到关系的映射
    
    queue.add([sourceNodeId]);
    visited.add(sourceNodeId);
    
    while (queue.isNotEmpty) {
      final path = queue.removeAt(0);
      final currentNodeId = path.last;
      
      if (currentNodeId == targetNodeId) {
        // 找到路径，构建GraphPath对象
        final nodeIds = path;
        final relationIds = <String>[];
        
        for (int i = 0; i < nodeIds.length - 1; i++) {
          final relationId = pathRelations[nodeIds[i] + '->' + nodeIds[i + 1]];
          if (relationId != null) {
            relationIds.add(relationId);
          }
        }
        
        return GraphPath(
          id: 'path_${DateTime.now().millisecondsSinceEpoch}',
          nodeIds: nodeIds,
          relationIds: relationIds,
          description: '从 ${_nodes[sourceNodeId]?.name} 到 ${_nodes[targetNodeId]?.name} 的路径',
        );
      }
      
      // 获取当前节点的所有出边
      final outgoingRelations = await getOutgoingRelations(currentNodeId);
      
      for (final relation in outgoingRelations) {
        final nextNodeId = relation.targetNodeId;
        
        if (!visited.contains(nextNodeId)) {
          visited.add(nextNodeId);
          
          final newPath = List<String>.from(path);
          newPath.add(nextNodeId);
          queue.add(newPath);
          
          // 记录路径关系
          pathRelations[currentNodeId + '->' + nextNodeId] = relation.id;
        }
      }
    }
    
    // 没有找到路径
    return null;
  }
  
  @override
  Future<GraphQueryResult> query(String queryText) async {
    try {
      // 使用RAG服务获取相关知识
      final ragResults = await _ragService.query(
        queryText,
        collection: 'knowledge_graph',
        limit: 10,
      );
      
      // 处理查询，这里简化处理为关键词匹配
      // 在实际应用中，应该实现更复杂的语义查询
      final keywords = queryText.toLowerCase().split(' ')
        .where((word) => word.length > 3)
        .toList();
      
      // 查找匹配的节点
      final matchedNodes = <GraphNode>[];
      
      for (final node in _nodes.values) {
        bool matches = false;
        
        for (final keyword in keywords) {
          if (node.name.toLowerCase().contains(keyword) || 
              (node.description?.toLowerCase().contains(keyword) ?? false)) {
            matches = true;
            break;
          }
        }
        
        if (matches) {
          matchedNodes.add(node);
        }
      }
      
      // 获取节点间的关系
      final matchedRelations = <GraphRelation>[];
      final nodeIds = matchedNodes.map((n) => n.id).toSet();
      
      for (final relation in _relations.values) {
        if (nodeIds.contains(relation.sourceNodeId) && 
            nodeIds.contains(relation.targetNodeId)) {
          matchedRelations.add(relation);
        }
      }
      
      // 生成查询结果摘要
      String? summary;
      if (matchedNodes.isNotEmpty) {
        summary = '找到 ${matchedNodes.length} 个相关概念和 ${matchedRelations.length} 个关系。';
        
        if (matchedNodes.length <= 3) {
          summary += ' 包括: ' + matchedNodes.map((n) => n.name).join(', ');
        }
      } else {
        summary = '未找到与查询相关的概念。';
      }
      
      return GraphQueryResult(
        nodes: matchedNodes,
        relations: matchedRelations,
        summary: summary,
      );
    } catch (e, stackTrace) {
      logger.e('知识图谱查询失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<GraphQueryResult> extractKnowledge(String text) async {
    try {
      // 在实际应用中，应使用NLP模型进行命名实体识别和关系提取
      // 这里简化处理，使用关键词匹配
      
      final nodes = <GraphNode>[];
      final relations = <GraphRelation>[];
      
      // 使用RAG服务获取相关知识模板
      final ragResults = await _ragService.query(
        '知识提取: $text',
        collection: 'knowledge_templates',
        limit: 5,
      );
      
      // 模拟提取几个概念
      const conceptTypes = [
        GraphNodeType.concept,
        GraphNodeType.entity,
        GraphNodeType.symptom,
        GraphNodeType.disease,
      ];
      
      final sentences = text.split('. ');
      
      for (int i = 0; i < sentences.length; i++) {
        final sentence = sentences[i];
        final words = sentence.split(' ');
        
        for (int j = 0; j < words.length; j++) {
          if (words[j].length > 4) {
            // 提取概念节点
            final nodeId = 'node_${DateTime.now().millisecondsSinceEpoch}_$j';
            final nodeType = conceptTypes[i % conceptTypes.length];
            
            final node = GraphNode(
              id: nodeId,
              type: nodeType,
              name: words[j],
              source: GraphDataSource.userData,
              confidence: ConfidenceLevel.medium,
            );
            
            nodes.add(node);
            
            // 如果有前一个节点，创建关系
            if (j > 0 && words[j - 1].length > 4) {
              final prevNodeId = 'node_${DateTime.now().millisecondsSinceEpoch}_${j-1}';
              
              final relation = GraphRelation(
                id: 'rel_${DateTime.now().millisecondsSinceEpoch}_$j',
                sourceNodeId: prevNodeId,
                targetNodeId: nodeId,
                type: GraphRelationType.isA,
                source: GraphDataSource.userData,
                confidence: ConfidenceLevel.low,
              );
              
              relations.add(relation);
            }
          }
        }
      }
      
      // 提取完成后，可以考虑添加到图谱中
      // 但这里仅返回结果，不自动添加
      
      return GraphQueryResult(
        nodes: nodes,
        relations: relations,
        summary: '从文本中提取了 ${nodes.length} 个概念和 ${relations.length} 个关系。',
      );
    } catch (e, stackTrace) {
      logger.e('知识提取失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> mergeGraphs(GraphQueryResult otherGraph) async {
    // 添加新节点
    for (final node in otherGraph.nodes) {
      if (!_nodes.containsKey(node.id)) {
        await addNode(node);
      } else {
        // 可以实现更复杂的合并逻辑，如比较可信度等
        final existingNode = _nodes[node.id]!;
        if (node.confidence.index > existingNode.confidence.index) {
          await updateNode(node);
        }
      }
    }
    
    // 添加新关系
    for (final relation in otherGraph.relations) {
      if (!_relations.containsKey(relation.id)) {
        try {
          await addRelation(relation);
        } catch (e) {
          // 如果源节点或目标节点不存在，忽略该关系
          logger.w('合并图谱时跳过关系: ${relation.id}，原因: $e');
        }
      } else {
        // 可以实现更复杂的合并逻辑
        final existingRelation = _relations[relation.id]!;
        if (relation.confidence.index > existingRelation.confidence.index) {
          await updateRelation(relation);
        }
      }
    }
  }
  
  @override
  Future<String> generateGraphSummary(GraphQueryResult graph) async {
    final nodes = graph.nodes;
    final relations = graph.relations;
    
    final StringBuilder summary = StringBuilder();
    
    if (nodes.isEmpty) {
      return '知识图谱为空。';
    }
    
    // 统计各类型节点数量
    final nodeTypeCounts = <GraphNodeType, int>{};
    for (final node in nodes) {
      nodeTypeCounts[node.type] = (nodeTypeCounts[node.type] ?? 0) + 1;
    }
    
    // 统计各类型关系数量
    final relationTypeCounts = <GraphRelationType, int>{};
    for (final relation in relations) {
      relationTypeCounts[relation.type] = (relationTypeCounts[relation.type] ?? 0) + 1;
    }
    
    // 生成摘要
    summary.appendLine('知识图谱包含 ${nodes.length} 个节点和 ${relations.length} 个关系。');
    
    if (nodeTypeCounts.isNotEmpty) {
      summary.appendLine('\n节点类型统计:');
      nodeTypeCounts.forEach((type, count) {
        summary.appendLine('- ${_typeToChineseName(type)}: $count 个');
      });
    }
    
    if (relationTypeCounts.isNotEmpty) {
      summary.appendLine('\n关系类型统计:');
      relationTypeCounts.forEach((type, count) {
        summary.appendLine('- ${_relationToChineseName(type)}: $count 个');
      });
    }
    
    // 找出核心概念（连接最多的节点）
    if (nodes.isNotEmpty && relations.isNotEmpty) {
      final nodeDegrees = <String, int>{};
      
      for (final relation in relations) {
        nodeDegrees[relation.sourceNodeId] = (nodeDegrees[relation.sourceNodeId] ?? 0) + 1;
        nodeDegrees[relation.targetNodeId] = (nodeDegrees[relation.targetNodeId] ?? 0) + 1;
      }
      
      final sortedNodes = nodes.where((n) => nodeDegrees.containsKey(n.id)).toList()
        ..sort((a, b) => (nodeDegrees[b.id] ?? 0).compareTo(nodeDegrees[a.id] ?? 0));
      
      if (sortedNodes.isNotEmpty) {
        final topNodes = sortedNodes.take(3).toList();
        
        summary.appendLine('\n核心概念:');
        for (final node in topNodes) {
          summary.appendLine('- ${node.name} (关联度: ${nodeDegrees[node.id]})');
        }
      }
    }
    
    return summary.toString();
  }
  
  /// 节点类型转中文名称
  String _typeToChineseName(GraphNodeType type) {
    switch (type) {
      case GraphNodeType.concept: return '概念';
      case GraphNodeType.entity: return '实体';
      case GraphNodeType.symptom: return '症状';
      case GraphNodeType.disease: return '疾病';
      case GraphNodeType.treatment: return '治疗方法';
      case GraphNodeType.medicine: return '药物';
      case GraphNodeType.food: return '食物';
      case GraphNodeType.nutrient: return '营养素';
      case GraphNodeType.exercise: return '运动';
    }
  }
  
  /// 关系类型转中文名称
  String _relationToChineseName(GraphRelationType type) {
    switch (type) {
      case GraphRelationType.isA: return '是一种';
      case GraphRelationType.partOf: return '是...的一部分';
      case GraphRelationType.hasProperty: return '具有属性';
      case GraphRelationType.causes: return '引起';
      case GraphRelationType.treats: return '治疗';
      case GraphRelationType.prevents: return '预防';
      case GraphRelationType.worsens: return '加重';
      case GraphRelationType.alleviates: return '缓解';
      case GraphRelationType.contains: return '含有';
      case GraphRelationType.affects: return '影响';
      case GraphRelationType.interactsWith: return '相互作用';
      case GraphRelationType.contraindicatedWith: return '禁忌';
    }
  }
  
  @override
  Future<Map<String, dynamic>> visualizeGraph(GraphQueryResult graph) async {
    // 在实际应用中，这里应该生成可视化数据
    // 例如适用于D3.js或ECharts的格式
    
    final nodes = graph.nodes.map((node) => {
      'id': node.id,
      'name': node.name,
      'type': node.type.toString(),
      'symbolSize': node.type == GraphNodeType.concept ? 30 : 20,
      'category': node.type.index,
    }).toList();
    
    final links = graph.relations.map((relation) => {
      'source': relation.sourceNodeId,
      'target': relation.targetNodeId,
      'name': relation.type.toString(),
      'value': relation.description ?? _relationToChineseName(relation.type),
    }).toList();
    
    final categories = GraphNodeType.values.map((type) => {
      'name': _typeToChineseName(type),
    }).toList();
    
    return {
      'nodes': nodes,
      'links': links,
      'categories': categories,
    };
  }
}

/// 中医知识图谱代理
class TCMKnowledgeGraphAgent extends KnowledgeGraphAgentImpl {
  TCMKnowledgeGraphAgent(
    SecurityFramework securityFramework, 
    LearningSystem learningSystem,
    RAGService ragService,
  ) : super(
       securityFramework: securityFramework, 
       learningSystem: learningSystem,
       ragService: ragService,
      );
  
  // 可以添加特定于中医知识图谱的方法
}

/// 西医知识图谱代理
class WesternMedicalKnowledgeGraphAgent extends KnowledgeGraphAgentImpl {
  WesternMedicalKnowledgeGraphAgent(
    SecurityFramework securityFramework, 
    LearningSystem learningSystem,
    RAGService ragService,
  ) : super(
       securityFramework: securityFramework, 
       learningSystem: learningSystem,
       ragService: ragService,
      );
  
  // 可以添加特定于西医知识图谱的方法
}

/// 药食知识图谱代理
class MedicinalFoodKnowledgeGraphAgent extends KnowledgeGraphAgentImpl {
  MedicinalFoodKnowledgeGraphAgent(
    SecurityFramework securityFramework, 
    LearningSystem learningSystem,
    RAGService ragService,
  ) : super(
       securityFramework: securityFramework, 
       learningSystem: learningSystem,
       ragService: ragService,
      );
  
  // 可以添加特定于药食知识图谱的方法
}

/// 字符串构建器
class StringBuilder {
  final List<String> _lines = [];
  
  void appendLine(String line) {
    _lines.add(line);
  }
  
  @override
  String toString() {
    return _lines.join('\n');
  }
}

/// RAG服务Provider
final ragServiceProvider = Provider<RAGService>((ref) {
  // 不再使用GetIt，直接使用ai_core_providers中定义的ragServiceProvider
  return ref.watch(ai_core_providers.ragServiceProvider);
});

/// 知识图谱代理Provider
final knowledgeGraphAgentProvider = Provider<KnowledgeGraphAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  return KnowledgeGraphAgentImpl(
    securityFramework: securityFramework,
    learningSystem: learningSystem,
    ragService: ragService,
  );
});

/// 中医知识图谱代理Provider
final tcmKnowledgeGraphAgentProvider = Provider<KnowledgeGraphAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  return TCMKnowledgeGraphAgent(
    securityFramework,
    learningSystem,
    ragService,
  );
});

/// 西医知识图谱代理Provider
final westernMedicalKnowledgeGraphAgentProvider = Provider<KnowledgeGraphAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  return WesternMedicalKnowledgeGraphAgent(
    securityFramework,
    learningSystem,
    ragService,
  );
});

/// 药食知识图谱代理Provider
final medicinalFoodKnowledgeGraphAgentProvider = Provider<KnowledgeGraphAgent>((ref) {
  final securityFramework = ref.watch(securityFrameworkProvider);
  final learningSystem = ref.watch(learningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  return MedicinalFoodKnowledgeGraphAgent(
    securityFramework,
    learningSystem,
    ragService,
  );
});

/// 安全框架Provider（如果尚未在其他地方定义）
final securityFrameworkProvider = Provider<SecurityFramework>((ref) {
  return SecurityFramework();
});

/// 学习系统Provider（如果尚未在其他地方定义）
final learningSystemProvider = Provider<LearningSystem>((ref) {
  return LearningSystem();
}); 
