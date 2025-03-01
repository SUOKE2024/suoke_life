import 'dart:async';
import 'dart:math';
import 'dart:convert';
import 'dart:collection';

import '../entities/knowledge_node.dart';
import '../entities/knowledge_relation.dart';
import '../../core/storage/database_helper.dart';
import '../../core/utils/logger.dart';

/// 知识图谱存储库接口
abstract class KnowledgeGraphRepository {
  /// 获取所有知识节点
  Future<List<KnowledgeNode>> getAllNodes();

  /// 根据ID获取节点
  Future<KnowledgeNode?> getNodeById(String id);

  /// 根据主题获取节点
  Future<List<KnowledgeNode>> getNodesByTopic(String topic);

  /// 根据类型获取节点
  Future<List<KnowledgeNode>> getNodesByType(String type);

  /// 添加节点
  Future<String> addNode(KnowledgeNode node);

  /// 更新节点
  Future<bool> updateNode(KnowledgeNode node);

  /// 删除节点
  Future<bool> deleteNode(String id);

  /// 获取所有关系
  Future<List<KnowledgeRelation>> getAllRelations();

  /// 根据ID获取关系
  Future<KnowledgeRelation?> getRelationById(String id);

  /// 获取源节点的所有关系
  Future<List<KnowledgeRelation>> getRelationsBySourceId(String sourceId);

  /// 获取目标节点的所有关系
  Future<List<KnowledgeRelation>> getRelationsByTargetId(String targetId);

  /// 获取指定节点相关的所有关系（源或目标）
  Future<List<KnowledgeRelation>> getRelationsByNodeId(String nodeId);

  /// 根据关系类型获取关系
  Future<List<KnowledgeRelation>> getRelationsByType(String type);

  /// 添加关系
  Future<String> addRelation(KnowledgeRelation relation);

  /// 更新关系
  Future<bool> updateRelation(KnowledgeRelation relation);

  /// 删除关系
  Future<bool> deleteRelation(String id);

  /// 搜索知识图谱
  Future<Map<String, dynamic>> searchKnowledgeGraph(
    String query, {
    int limit = 10,
  });

  /// 获取关联节点（相邻节点和关系）
  Future<Map<String, dynamic>> getRelatedNodes(String nodeId, {int depth = 1});

  /// 获取节点的子图（包括所有子节点和关系）
  Future<Map<String, dynamic>> getSubgraph(
    String rootNodeId, {
    int maxDepth = 3,
  });

  /// 同步数据到云端
  Future<bool> syncToCloud();

  /// 从云端同步数据
  Future<bool> syncFromCloud();
}

/// 本地知识图谱存储库实现
class LocalKnowledgeGraphRepository implements KnowledgeGraphRepository {
  final DatabaseHelper _dbHelper;

  // 内存缓存
  final Map<String, KnowledgeNode> _nodeCache = {};
  final Map<String, KnowledgeRelation> _relationCache = {};

  // 同步状态跟踪
  bool _isSyncing = false;
  DateTime? _lastSyncTime;

  LocalKnowledgeGraphRepository(this._dbHelper);

  /// 确保表已创建
  Future<void> _ensureTablesExist() async {
    final db = await _dbHelper.database;

    // 创建节点表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS knowledge_nodes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        topic TEXT,
        description TEXT,
        data TEXT,
        x REAL,
        y REAL,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        sync_status TEXT DEFAULT 'pending'
      )
    ''');

    // 创建关系表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS knowledge_relations (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        weight REAL,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        sync_status TEXT DEFAULT 'pending',
        FOREIGN KEY (source_id) REFERENCES knowledge_nodes (id) ON DELETE CASCADE,
        FOREIGN KEY (target_id) REFERENCES knowledge_nodes (id) ON DELETE CASCADE
      )
    ''');

    // 创建同步日志表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS sync_operations (
        id TEXT PRIMARY KEY,
        operation_type TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        data TEXT,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT
      )
    ''');

    // 创建索引
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_nodes_type ON knowledge_nodes (type)',
    );
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_nodes_topic ON knowledge_nodes (topic)',
    );
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_relations_source ON knowledge_relations (source_id)',
    );
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_relations_target ON knowledge_relations (target_id)',
    );
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_relations_type ON knowledge_relations (type)',
    );
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_operations (status)',
    );
  }

  @override
  Future<List<KnowledgeNode>> getAllNodes() async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query('knowledge_nodes');
    final nodes =
        results.map((row) {
          final node = KnowledgeNode.fromMap(row);
          _nodeCache[node.id] = node; // 更新缓存
          return node;
        }).toList();

    return nodes;
  }

  @override
  Future<KnowledgeNode?> getNodeById(String id) async {
    // 先检查缓存
    if (_nodeCache.containsKey(id)) {
      return _nodeCache[id];
    }

    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_nodes',
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );

    if (results.isEmpty) {
      return null;
    }

    final node = KnowledgeNode.fromMap(results.first);
    _nodeCache[id] = node; // 更新缓存
    return node;
  }

  @override
  Future<List<KnowledgeNode>> getNodesByTopic(String topic) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_nodes',
      where: 'topic = ?',
      whereArgs: [topic],
    );

    final nodes =
        results.map((row) {
          final node = KnowledgeNode.fromMap(row);
          _nodeCache[node.id] = node; // 更新缓存
          return node;
        }).toList();

    return nodes;
  }

  @override
  Future<List<KnowledgeNode>> getNodesByType(String type) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_nodes',
      where: 'type = ?',
      whereArgs: [type],
    );

    final nodes =
        results.map((row) {
          final node = KnowledgeNode.fromMap(row);
          _nodeCache[node.id] = node; // 更新缓存
          return node;
        }).toList();

    return nodes;
  }

  @override
  Future<String> addNode(KnowledgeNode node) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final now = DateTime.now().toIso8601String();
    final nodeId =
        node.id.isEmpty
            ? 'node_${DateTime.now().millisecondsSinceEpoch}'
            : node.id;

    final nodeMap =
        node.copyWith(id: nodeId, updatedAt: now, createdAt: now).toMap();

    await db.insert('knowledge_nodes', nodeMap);

    // 添加同步操作记录
    await _recordSyncOperation('create', 'node', nodeId, nodeMap);

    // 更新缓存
    final newNode = node.copyWith(id: nodeId);
    _nodeCache[nodeId] = newNode;

    return nodeId;
  }

  @override
  Future<bool> updateNode(KnowledgeNode node) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 检查节点是否存在
    final existingNode = await getNodeById(node.id);
    if (existingNode == null) {
      return false;
    }

    final now = DateTime.now().toIso8601String();
    final nodeMap =
        node
            .copyWith(updatedAt: now, createdAt: existingNode.createdAt)
            .toMap();

    final count = await db.update(
      'knowledge_nodes',
      nodeMap,
      where: 'id = ?',
      whereArgs: [node.id],
    );

    if (count > 0) {
      // 添加同步操作记录
      await _recordSyncOperation('update', 'node', node.id, nodeMap);

      // 更新缓存
      _nodeCache[node.id] = node.copyWith(updatedAt: now);
      return true;
    }

    return false;
  }

  @override
  Future<bool> deleteNode(String id) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 查询节点是否存在
    final existingNode = await getNodeById(id);
    if (existingNode == null) {
      return false;
    }

    // 删除相关的关系
    await db.delete(
      'knowledge_relations',
      where: 'source_id = ? OR target_id = ?',
      whereArgs: [id, id],
    );

    // 删除节点
    final count = await db.delete(
      'knowledge_nodes',
      where: 'id = ?',
      whereArgs: [id],
    );

    if (count > 0) {
      // 添加同步操作记录
      await _recordSyncOperation('delete', 'node', id, {'id': id});

      // 更新缓存
      _nodeCache.remove(id);

      // 清理关系缓存（与该节点相关的关系）
      _relationCache.removeWhere(
        (key, relation) => relation.sourceId == id || relation.targetId == id,
      );

      return true;
    }

    return false;
  }

  @override
  Future<List<KnowledgeRelation>> getAllRelations() async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query('knowledge_relations');
    final relations =
        results.map((row) {
          final relation = KnowledgeRelation.fromMap(row);
          _relationCache[relation.id] = relation; // 更新缓存
          return relation;
        }).toList();

    return relations;
  }

  @override
  Future<KnowledgeRelation?> getRelationById(String id) async {
    // 先检查缓存
    if (_relationCache.containsKey(id)) {
      return _relationCache[id];
    }

    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_relations',
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );

    if (results.isEmpty) {
      return null;
    }

    final relation = KnowledgeRelation.fromMap(results.first);
    _relationCache[id] = relation; // 更新缓存
    return relation;
  }

  @override
  Future<List<KnowledgeRelation>> getRelationsBySourceId(
    String sourceId,
  ) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_relations',
      where: 'source_id = ?',
      whereArgs: [sourceId],
    );

    final relations =
        results.map((row) {
          final relation = KnowledgeRelation.fromMap(row);
          _relationCache[relation.id] = relation; // 更新缓存
          return relation;
        }).toList();

    return relations;
  }

  @override
  Future<List<KnowledgeRelation>> getRelationsByTargetId(
    String targetId,
  ) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_relations',
      where: 'target_id = ?',
      whereArgs: [targetId],
    );

    final relations =
        results.map((row) {
          final relation = KnowledgeRelation.fromMap(row);
          _relationCache[relation.id] = relation; // 更新缓存
          return relation;
        }).toList();

    return relations;
  }

  @override
  Future<List<KnowledgeRelation>> getRelationsByNodeId(String nodeId) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_relations',
      where: 'source_id = ? OR target_id = ?',
      whereArgs: [nodeId, nodeId],
    );

    final relations =
        results.map((row) {
          final relation = KnowledgeRelation.fromMap(row);
          _relationCache[relation.id] = relation; // 更新缓存
          return relation;
        }).toList();

    return relations;
  }

  @override
  Future<List<KnowledgeRelation>> getRelationsByType(String type) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    final results = await db.query(
      'knowledge_relations',
      where: 'type = ?',
      whereArgs: [type],
    );

    final relations =
        results.map((row) {
          final relation = KnowledgeRelation.fromMap(row);
          _relationCache[relation.id] = relation; // 更新缓存
          return relation;
        }).toList();

    return relations;
  }

  @override
  Future<String> addRelation(KnowledgeRelation relation) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 验证源节点和目标节点是否存在
    final sourceNode = await getNodeById(relation.sourceId);
    final targetNode = await getNodeById(relation.targetId);

    if (sourceNode == null || targetNode == null) {
      throw Exception('源节点或目标节点不存在');
    }

    final now = DateTime.now().toIso8601String();
    final relationId =
        relation.id.isEmpty
            ? 'rel_${DateTime.now().millisecondsSinceEpoch}'
            : relation.id;

    final relationMap =
        relation
            .copyWith(id: relationId, updatedAt: now, createdAt: now)
            .toMap();

    await db.insert('knowledge_relations', relationMap);

    // 添加同步操作记录
    await _recordSyncOperation('create', 'relation', relationId, relationMap);

    // 更新缓存
    final newRelation = relation.copyWith(id: relationId);
    _relationCache[relationId] = newRelation;

    return relationId;
  }

  @override
  Future<bool> updateRelation(KnowledgeRelation relation) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 检查关系是否存在
    final existingRelation = await getRelationById(relation.id);
    if (existingRelation == null) {
      return false;
    }

    // 验证源节点和目标节点是否存在
    final sourceNode = await getNodeById(relation.sourceId);
    final targetNode = await getNodeById(relation.targetId);

    if (sourceNode == null || targetNode == null) {
      return false;
    }

    final now = DateTime.now().toIso8601String();
    final relationMap =
        relation
            .copyWith(updatedAt: now, createdAt: existingRelation.createdAt)
            .toMap();

    final count = await db.update(
      'knowledge_relations',
      relationMap,
      where: 'id = ?',
      whereArgs: [relation.id],
    );

    if (count > 0) {
      // 添加同步操作记录
      await _recordSyncOperation(
        'update',
        'relation',
        relation.id,
        relationMap,
      );

      // 更新缓存
      _relationCache[relation.id] = relation.copyWith(updatedAt: now);
      return true;
    }

    return false;
  }

  @override
  Future<bool> deleteRelation(String id) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 检查关系是否存在
    final existingRelation = await getRelationById(id);
    if (existingRelation == null) {
      return false;
    }

    // 删除关系
    final count = await db.delete(
      'knowledge_relations',
      where: 'id = ?',
      whereArgs: [id],
    );

    if (count > 0) {
      // 添加同步操作记录
      await _recordSyncOperation('delete', 'relation', id, {'id': id});

      // 更新缓存
      _relationCache.remove(id);
      return true;
    }

    return false;
  }

  @override
  Future<Map<String, dynamic>> searchKnowledgeGraph(
    String query, {
    int limit = 10,
  }) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 搜索节点
    final nodeResults = await db.query(
      'knowledge_nodes',
      where: 'name LIKE ? OR description LIKE ?',
      whereArgs: ['%$query%', '%$query%'],
      limit: limit,
    );

    final nodes = nodeResults.map((row) => KnowledgeNode.fromMap(row)).toList();

    // 获取节点ID列表
    final nodeIds = nodes.map((node) => node.id).toList();

    // 如果没有匹配的节点，返回空结果
    if (nodeIds.isEmpty) {
      return {'nodes': [], 'relations': []};
    }

    // 构建IN查询参数
    final placeholders = nodeIds.map((_) => '?').join(',');

    // 查询与匹配节点相关的关系
    final relationResults = await db.query(
      'knowledge_relations',
      where: 'source_id IN ($placeholders) OR target_id IN ($placeholders)',
      whereArgs: [...nodeIds, ...nodeIds],
    );

    final relations =
        relationResults.map((row) => KnowledgeRelation.fromMap(row)).toList();

    // 更新缓存
    for (final node in nodes) {
      _nodeCache[node.id] = node;
    }

    for (final relation in relations) {
      _relationCache[relation.id] = relation;
    }

    return {'nodes': nodes, 'relations': relations};
  }

  @override
  Future<Map<String, dynamic>> getRelatedNodes(
    String nodeId, {
    int depth = 1,
  }) async {
    await _ensureTablesExist();

    final db = await _dbHelper.database;

    // 获取指定节点
    final centerNode = await getNodeById(nodeId);
    if (centerNode == null) {
      return {'nodes': [], 'relations': []};
    }

    final Set<String> nodeIds = {nodeId};
    final Set<String> relationIds = {};
    final Map<String, KnowledgeNode> nodesToReturn = {nodeId: centerNode};
    final Map<String, KnowledgeRelation> relationsToReturn = {};

    // 广度优先搜索相关节点
    for (int i = 0; i < depth; i++) {
      final currentNodeIds = List<String>.from(nodeIds);

      for (final currentNodeId in currentNodeIds) {
        // 获取相关关系
        final relations = await getRelationsByNodeId(currentNodeId);

        for (final relation in relations) {
          if (relationIds.contains(relation.id)) {
            continue;
          }

          relationIds.add(relation.id);
          relationsToReturn[relation.id] = relation;

          // 处理源节点
          if (relation.sourceId != currentNodeId &&
              !nodeIds.contains(relation.sourceId)) {
            final sourceNode = await getNodeById(relation.sourceId);
            if (sourceNode != null) {
              nodeIds.add(relation.sourceId);
              nodesToReturn[relation.sourceId] = sourceNode;
            }
          }

          // 处理目标节点
          if (relation.targetId != currentNodeId &&
              !nodeIds.contains(relation.targetId)) {
            final targetNode = await getNodeById(relation.targetId);
            if (targetNode != null) {
              nodeIds.add(relation.targetId);
              nodesToReturn[relation.targetId] = targetNode;
            }
          }
        }
      }
    }

    return {
      'nodes': nodesToReturn.values.toList(),
      'relations': relationsToReturn.values.toList(),
    };
  }

  @override
  Future<Map<String, dynamic>> getSubgraph(
    String rootNodeId, {
    int maxDepth = 3,
  }) async {
    await _ensureTablesExist();

    final db = _dbHelper.database;
    if (db == null) {
      return {'nodes': [], 'relations': []};
    }

    // 获取根节点
    final rootNode = await getNodeById(rootNodeId);
    if (rootNode == null) {
      return {'nodes': [], 'relations': []};
    }

    final Set<String> nodeIds = {rootNodeId};
    final Set<String> relationIds = {};
    final Map<String, KnowledgeNode> nodesToReturn = {rootNodeId: rootNode};
    final Map<String, KnowledgeRelation> relationsToReturn = {};

    // 广度优先搜索构建子图
    final Queue<Map<String, dynamic>> queue = Queue();
    queue.add({'id': rootNodeId, 'depth': 0});

    while (queue.isNotEmpty) {
      final current = queue.removeFirst();
      final currentNodeId = current['id'] as String;
      final currentDepth = current['depth'] as int;

      if (currentDepth >= maxDepth) {
        continue;
      }

      // 获取源自该节点的关系
      final outgoingRelations = await getRelationsBySourceId(currentNodeId);

      for (final relation in outgoingRelations) {
        if (relationIds.contains(relation.id)) {
          continue;
        }

        relationIds.add(relation.id);
        relationsToReturn[relation.id] = relation;

        // 处理目标节点
        if (!nodeIds.contains(relation.targetId)) {
          final targetNode = await getNodeById(relation.targetId);
          if (targetNode != null) {
            nodeIds.add(relation.targetId);
            nodesToReturn[relation.targetId] = targetNode;
            queue.add({'id': relation.targetId, 'depth': currentDepth + 1});
          }
        }
      }
    }

    return {
      'nodes': nodesToReturn.values.toList(),
      'relations': relationsToReturn.values.toList(),
    };
  }

  /// 记录同步操作
  Future<void> _recordSyncOperation(
    String operationType,
    String entityType,
    String entityId,
    Map<String, dynamic> data,
  ) async {
    final db = await _dbHelper.database;

    final now = DateTime.now().toIso8601String();
    final operationId = 'sync_${DateTime.now().millisecondsSinceEpoch}';

    await db.insert('sync_operations', {
      'id': operationId,
      'operation_type': operationType,
      'entity_type': entityType,
      'entity_id': entityId,
      'data': jsonEncode(data),
      'status': 'pending',
      'created_at': now,
      'updated_at': now,
    });
  }

  @override
  Future<bool> syncToCloud() async {
    // 防止并发同步
    if (_isSyncing) {
      return false;
    }

    _isSyncing = true;

    try {
      await _ensureTablesExist();

      final db = await _dbHelper.database;

      // 获取待同步的操作
      final operations = await db.query(
        'sync_operations',
        where: 'status = ?',
        whereArgs: ['pending'],
        orderBy: 'created_at ASC',
      );

      if (operations.isEmpty) {
        logger.i('没有待同步的操作');
        _isSyncing = false;
        return true;
      }

      logger.i('开始同步 ${operations.length} 个操作到云端');

      // TODO: 实现与云服务的实际API交互
      // 这里是模拟同步过程
      await Future.delayed(const Duration(seconds: 1));

      // 模拟同步成功（实际项目中应该是批量发送到云端）
      final now = DateTime.now().toIso8601String();
      for (final operation in operations) {
        await db.update(
          'sync_operations',
          {'status': 'synced', 'updated_at': now},
          where: 'id = ?',
          whereArgs: [operation['id']],
        );
      }

      // 更新最后同步时间
      _lastSyncTime = DateTime.now();

      logger.i('成功同步 ${operations.length} 个操作到云端');
      _isSyncing = false;
      return true;
    } catch (e) {
      logger.e('同步到云端失败: $e');
      _isSyncing = false;
      return false;
    }
  }

  @override
  Future<bool> syncFromCloud() async {
    // 防止并发同步
    if (_isSyncing) {
      return false;
    }

    _isSyncing = true;

    try {
      await _ensureTablesExist();

      final db = _dbHelper.database;
      if (db == null) {
        _isSyncing = false;
        return false;
      }

      // TODO: 实现从云端拉取更新的实际API交互
      // 这里是模拟同步过程
      await Future.delayed(const Duration(seconds: 1));

      // 模拟从云端获取更新
      final fakeCloudData = _generateFakeCloudData();

      // 处理更新的节点
      for (final node in fakeCloudData['nodes'] as List<KnowledgeNode>) {
        final existingNode = await getNodeById(node.id);

        if (existingNode == null) {
          // 新增节点
          await addNode(node);
        } else if (node.updatedAt != null &&
            existingNode.updatedAt != null &&
            DateTime.parse(
              node.updatedAt!,
            ).isAfter(DateTime.parse(existingNode.updatedAt!))) {
          // 云端版本更新，更新本地
          await updateNode(node);
        }
      }

      // 处理更新的关系
      for (final relation
          in fakeCloudData['relations'] as List<KnowledgeRelation>) {
        final existingRelation = await getRelationById(relation.id);

        if (existingRelation == null) {
          // 新增关系
          await addRelation(relation);
        } else if (relation.updatedAt != null &&
            existingRelation.updatedAt != null &&
            DateTime.parse(
              relation.updatedAt!,
            ).isAfter(DateTime.parse(existingRelation.updatedAt!))) {
          // 云端版本更新，更新本地
          await updateRelation(relation);
        }
      }

      // 更新最后同步时间
      _lastSyncTime = DateTime.now();

      logger.i('成功从云端同步数据');
      _isSyncing = false;
      return true;
    } catch (e) {
      logger.e('从云端同步失败: $e');
      _isSyncing = false;
      return false;
    }
  }

  /// 生成模拟云端数据（仅用于演示）
  Map<String, dynamic> _generateFakeCloudData() {
    // 为演示创建一些测试数据
    final nodes = <KnowledgeNode>[
      KnowledgeNode(
        id: 'cloud_node_1',
        name: '云端演示节点1',
        type: '云数据',
        topic: '同步测试',
        description: '这是从云端同步的演示节点',
        createdAt: DateTime.now().toIso8601String(),
        updatedAt: DateTime.now().toIso8601String(),
      ),
      KnowledgeNode(
        id: 'cloud_node_2',
        name: '云端演示节点2',
        type: '云数据',
        topic: '同步测试',
        description: '这是从云端同步的另一个演示节点',
        createdAt: DateTime.now().toIso8601String(),
        updatedAt: DateTime.now().toIso8601String(),
      ),
    ];

    final relations = <KnowledgeRelation>[
      KnowledgeRelation(
        id: 'cloud_rel_1',
        sourceId: 'cloud_node_1',
        targetId: 'cloud_node_2',
        type: '关联',
        description: '这是一个云端演示关系',
        createdAt: DateTime.now().toIso8601String(),
        updatedAt: DateTime.now().toIso8601String(),
      ),
    ];

    return {'nodes': nodes, 'relations': relations};
  }
}

// 队列实现（用于BFS）
class Queue<T> {
  final List<T> _list = [];

  void add(T item) => _list.add(item);
  T removeFirst() => _list.removeAt(0);
  bool get isEmpty => _list.isEmpty;
  bool get isNotEmpty => !isEmpty;
}
