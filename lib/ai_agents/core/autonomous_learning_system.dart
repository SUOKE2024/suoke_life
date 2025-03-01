import 'dart:typed_data';
import 'package:flutter/foundation.dart';

/// 学习数据类型
enum LearningDataType {
  /// 文本数据
  text,
  
  /// 图像数据
  image,
  
  /// 音频数据
  audio,
  
  /// 视频数据
  video,
  
  /// 结构化数据
  structured,
  
  /// 多模态数据
  multimodal,
}

/// 学习数据源
enum LearningDataSource {
  /// 用户输入
  userInput,
  
  /// 代理生成
  agentGenerated,
  
  /// 系统日志
  systemLog,
  
  /// 外部API
  externalApi,
  
  /// 知识库
  knowledgeBase,
  
  /// 传感器
  sensor,
}

/// 学习回馈类型
enum LearningFeedbackType {
  /// 显式用户反馈
  explicitUserFeedback,
  
  /// 隐式用户反馈（如点击、时间、重复查询等）
  implicitUserFeedback,
  
  /// 系统评估
  systemEvaluation,
  
  /// 代理自评估
  agentSelfEvaluation,
  
  /// 外部专家评估
  externalExpertEvaluation,
}

/// 学习数据项
class LearningDataItem {
  /// 数据ID
  final String id;
  
  /// 数据类型
  final LearningDataType type;
  
  /// 数据源
  final LearningDataSource source;
  
  /// 数据内容
  final dynamic content;
  
  /// 数据标签/注释
  final Map<String, dynamic>? annotations;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 相关代理ID
  final String? agentId;
  
  /// 用户ID
  final String? userId;
  
  /// 会话ID
  final String? sessionId;
  
  LearningDataItem({
    required this.id,
    required this.type,
    required this.source,
    required this.content,
    this.annotations,
    DateTime? createdAt,
    this.agentId,
    this.userId,
    this.sessionId,
  }) : createdAt = createdAt ?? DateTime.now();
}

/// 学习回馈
class LearningFeedback {
  /// 回馈ID
  final String id;
  
  /// 回馈类型
  final LearningFeedbackType type;
  
  /// 回馈内容
  final dynamic content;
  
  /// 相关数据项ID
  final String? dataItemId;
  
  /// 相关代理ID
  final String? agentId;
  
  /// 用户ID
  final String? userId;
  
  /// 会话ID
  final String? sessionId;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 评分（如果适用）
  final double? rating;
  
  LearningFeedback({
    required this.id,
    required this.type,
    required this.content,
    this.dataItemId,
    this.agentId,
    this.userId,
    this.sessionId,
    DateTime? createdAt,
    this.rating,
  }) : createdAt = createdAt ?? DateTime.now();
}

/// 学习模型状态
enum LearningModelState {
  /// 初始状态
  initial,
  
  /// 训练中
  training,
  
  /// 评估中
  evaluating,
  
  /// 部署中
  deploying,
  
  /// 活跃中
  active,
  
  /// 已归档
  archived,
}

/// 学习模型信息
class LearningModelInfo {
  /// 模型ID
  final String id;
  
  /// 模型名称
  final String name;
  
  /// 模型版本
  final String version;
  
  /// 模型状态
  final LearningModelState state;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  /// 相关代理ID
  final String? agentId;
  
  /// 模型描述
  final String? description;
  
  /// 模型参数
  final Map<String, dynamic>? parameters;
  
  /// 模型性能指标
  final Map<String, dynamic>? metrics;
  
  LearningModelInfo({
    required this.id,
    required this.name,
    required this.version,
    required this.state,
    required this.createdAt,
    required this.updatedAt,
    this.agentId,
    this.description,
    this.parameters,
    this.metrics,
  });
}

/// 学习数据源类型
enum LearningDataSourceType {
  userInteraction,
  externalKnowledge,
  systemFeedback,
  performanceMetrics,
}

/// 学习事件
class LearningEvent {
  final String id;
  final DateTime timestamp;
  final String agentId;
  final LearningDataSourceType sourceType;
  final Map<String, dynamic> data;
  final double? importance;
  
  LearningEvent({
    required this.id,
    required this.timestamp,
    required this.agentId,
    required this.sourceType,
    required this.data,
    this.importance,
  });
}

/// 知识单元
class KnowledgeUnit {
  final String id;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String domain;
  final String concept;
  final Map<String, dynamic> attributes;
  final double confidence;
  final List<String> relatedKnowledgeIds;
  
  KnowledgeUnit({
    required this.id,
    required this.createdAt,
    required this.updatedAt,
    required this.domain,
    required this.concept,
    required this.attributes,
    required this.confidence,
    required this.relatedKnowledgeIds,
  });
}

/// 学习模式
enum LearningMode {
  passive,  // 被动学习，只在明确指示时学习
  active,   // 主动学习，在有新数据时学习
  proactive // 前瞻性学习，主动寻找学习机会
}

/// 自主学习系统接口
abstract class AutonomousLearningSystem {
  /// 当前学习模式
  LearningMode get currentLearningMode;
  
  /// 设置学习模式
  Future<void> setLearningMode(LearningMode mode);
  
  /// 处理学习事件
  Future<void> processLearningEvent(LearningEvent event);
  
  /// 批量处理学习事件
  Future<void> processBatchLearningEvents(List<LearningEvent> events);
  
  /// 获取特定领域的知识
  Future<List<KnowledgeUnit>> getKnowledgeByDomain(String domain);
  
  /// 获取特定概念的知识
  Future<List<KnowledgeUnit>> getKnowledgeByConcept(String concept);
  
  /// 获取相关知识
  Future<List<KnowledgeUnit>> getRelatedKnowledge(String knowledgeId);
  
  /// 添加新知识
  Future<String> addKnowledge(KnowledgeUnit knowledge);
  
  /// 更新知识
  Future<void> updateKnowledge(KnowledgeUnit knowledge);
  
  /// 删除知识
  Future<void> deleteKnowledge(String knowledgeId);
  
  /// 获取学习统计信息
  Future<Map<String, dynamic>> getLearningStatistics();
  
  /// 执行知识迁移
  Future<void> performKnowledgeTransfer(String sourceDomain, String targetDomain);
  
  /// 优化知识结构
  Future<void> optimizeKnowledgeStructure();
  
  /// 生成学习报告
  Future<String> generateLearningReport();
  
  /// 收集学习数据
  Future<String> collectData(LearningDataItem dataItem);
  
  /// 收集学习回馈
  Future<String> collectFeedback(LearningFeedback feedback);
  
  /// 分析学习数据
  Future<Map<String, dynamic>> analyzeData(String dataId);
  
  /// 训练模型
  Future<LearningModelInfo> trainModel({
    required String modelName,
    required String agentId,
    Map<String, dynamic>? parameters,
    List<String>? dataIds,
  });
  
  /// 评估模型
  Future<Map<String, dynamic>> evaluateModel(String modelId, {
    List<String>? testDataIds,
    Map<String, dynamic>? evaluationParameters,
  });
  
  /// 部署模型
  Future<bool> deployModel(String modelId, {
    String? targetAgentId,
    Map<String, dynamic>? deploymentParameters,
  });
  
  /// 归档模型
  Future<bool> archiveModel(String modelId);
  
  /// 获取模型信息
  Future<LearningModelInfo> getModelInfo(String modelId);
  
  /// 列出模型
  Future<List<LearningModelInfo>> listModels({
    String? agentId,
    LearningModelState? state,
  });
  
  /// 导出模型
  Future<Uint8List> exportModel(String modelId);
  
  /// 导入模型
  Future<String> importModel(Uint8List modelData, {
    String? modelName,
    String? agentId,
  });
  
  /// 获取学习数据统计
  Future<Map<String, dynamic>> getDataStatistics({
    DateTime? startDate,
    DateTime? endDate,
    String? agentId,
    String? userId,
  });
  
  /// 获取学习回馈统计
  Future<Map<String, dynamic>> getFeedbackStatistics({
    DateTime? startDate,
    DateTime? endDate,
    String? agentId,
    String? userId,
  });
  
  /// 获取模型性能历史
  Future<List<Map<String, dynamic>>> getModelPerformanceHistory(String modelId);
  
  /// 获取代理学习曲线
  Future<Map<String, List<dynamic>>> getAgentLearningCurve(String agentId);
}

/// 默认自主学习系统实现
class DefaultAutonomousLearningSystem implements AutonomousLearningSystem {
  final Map<String, LearningDataItem> _dataItems = {};
  final Map<String, LearningFeedback> _feedbacks = {};
  final Map<String, LearningModelInfo> _models = {};
  final List<LearningEvent> _events = [];
  final Map<String, KnowledgeUnit> _knowledgeUnits = {};
  LearningMode _currentMode = LearningMode.active;
  
  // 单例实现
  static final DefaultAutonomousLearningSystem _instance = DefaultAutonomousLearningSystem._internal();
  
  factory DefaultAutonomousLearningSystem() => _instance;
  
  DefaultAutonomousLearningSystem._internal();
  
  @override
  LearningMode get currentLearningMode => _currentMode;
  
  @override
  Future<void> setLearningMode(LearningMode mode) async {
    _currentMode = mode;
    debugPrint('Learning mode set to: ${mode.name}');
  }
  
  @override
  Future<void> processLearningEvent(LearningEvent event) async {
    // 添加事件到历史记录
    _events.add(event);
    
    // 根据学习模式决定是否立即处理
    if (_currentMode == LearningMode.passive) {
      debugPrint('Event ${event.id} stored but not processed (passive mode)');
      return;
    }
    
    // 处理事件并提取知识
    await _extractKnowledgeFromEvent(event);
    
    debugPrint('Processed learning event: ${event.id}');
  }
  
  @override
  Future<void> processBatchLearningEvents(List<LearningEvent> events) async {
    for (final event in events) {
      await processLearningEvent(event);
    }
  }
  
  @override
  Future<List<KnowledgeUnit>> getKnowledgeByDomain(String domain) async {
    return _knowledgeUnits.values
        .where((unit) => unit.domain == domain)
        .toList();
  }
  
  @override
  Future<List<KnowledgeUnit>> getKnowledgeByConcept(String concept) async {
    return _knowledgeUnits.values
        .where((unit) => unit.concept == concept)
        .toList();
  }
  
  @override
  Future<List<KnowledgeUnit>> getRelatedKnowledge(String knowledgeId) async {
    final unit = _knowledgeUnits[knowledgeId];
    if (unit == null) return [];
    
    return unit.relatedKnowledgeIds
        .map((id) => _knowledgeUnits[id])
        .whereType<KnowledgeUnit>()
        .toList();
  }
  
  @override
  Future<String> addKnowledge(KnowledgeUnit knowledge) async {
    _knowledgeUnits[knowledge.id] = knowledge;
    debugPrint('Added knowledge unit: ${knowledge.id}');
    return knowledge.id;
  }
  
  @override
  Future<void> updateKnowledge(KnowledgeUnit knowledge) async {
    if (_knowledgeUnits.containsKey(knowledge.id)) {
      _knowledgeUnits[knowledge.id] = knowledge;
      debugPrint('Updated knowledge unit: ${knowledge.id}');
    } else {
      debugPrint('Knowledge unit not found: ${knowledge.id}');
    }
  }
  
  @override
  Future<void> deleteKnowledge(String knowledgeId) async {
    _knowledgeUnits.remove(knowledgeId);
    debugPrint('Deleted knowledge unit: $knowledgeId');
  }
  
  @override
  Future<Map<String, dynamic>> getLearningStatistics() async {
    // 计算基本统计信息
    final eventsBySource = <LearningDataSourceType, int>{};
    for (final event in _events) {
      eventsBySource[event.sourceType] = (eventsBySource[event.sourceType] ?? 0) + 1;
    }
    
    final knowledgeByDomain = <String, int>{};
    for (final unit in _knowledgeUnits.values) {
      knowledgeByDomain[unit.domain] = (knowledgeByDomain[unit.domain] ?? 0) + 1;
    }
    
    return {
      'totalEvents': _events.length,
      'totalKnowledgeUnits': _knowledgeUnits.length,
      'eventsBySource': eventsBySource.map((k, v) => MapEntry(k.name, v)),
      'knowledgeByDomain': knowledgeByDomain,
      'averageConfidence': _calculateAverageConfidence(),
      'lastUpdated': DateTime.now().toIso8601String(),
    };
  }
  
  @override
  Future<void> performKnowledgeTransfer(String sourceDomain, String targetDomain) async {
    final sourceKnowledge = await getKnowledgeByDomain(sourceDomain);
    
    // 简单实现：复制知识并修改领域
    for (final unit in sourceKnowledge) {
      final newId = 'transferred_${unit.id}';
      final newUnit = KnowledgeUnit(
        id: newId,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        domain: targetDomain,
        concept: unit.concept,
        attributes: Map.from(unit.attributes),
        confidence: unit.confidence * 0.8, // 降低一些置信度
        relatedKnowledgeIds: List.from(unit.relatedKnowledgeIds)..add(unit.id),
      );
      
      await addKnowledge(newUnit);
    }
    
    debugPrint('Transferred ${sourceKnowledge.length} knowledge units from $sourceDomain to $targetDomain');
  }
  
  @override
  Future<void> optimizeKnowledgeStructure() async {
    // 简单实现：合并相似概念，移除低置信度知识
    final lowConfidenceIds = <String>[];
    
    for (final unit in _knowledgeUnits.values) {
      if (unit.confidence < 0.3) {
        lowConfidenceIds.add(unit.id);
      }
    }
    
    for (final id in lowConfidenceIds) {
      await deleteKnowledge(id);
    }
    
    debugPrint('Optimized knowledge structure: removed ${lowConfidenceIds.length} low confidence units');
  }
  
  @override
  Future<String> generateLearningReport() async {
    final stats = await getLearningStatistics();
    
    // 生成简单报告
    final report = StringBuffer();
    report.writeln('# 自主学习系统报告');
    report.writeln('生成时间: ${DateTime.now().toIso8601String()}');
    report.writeln();
    report.writeln('## 统计信息');
    report.writeln('- 总学习事件数: ${stats['totalEvents']}');
    report.writeln('- 总知识单元数: ${stats['totalKnowledgeUnits']}');
    report.writeln('- 平均置信度: ${stats['averageConfidence']}');
    report.writeln();
    
    report.writeln('## 按来源的事件分布');
    (stats['eventsBySource'] as Map<String, dynamic>).forEach((source, count) {
      report.writeln('- $source: $count');
    });
    report.writeln();
    
    report.writeln('## 按领域的知识分布');
    (stats['knowledgeByDomain'] as Map<String, dynamic>).forEach((domain, count) {
      report.writeln('- $domain: $count');
    });
    
    return report.toString();
  }
  
  @override
  Future<String> collectData(LearningDataItem dataItem) async {
    _dataItems[dataItem.id] = dataItem;
    return dataItem.id;
  }
  
  @override
  Future<String> collectFeedback(LearningFeedback feedback) async {
    _feedbacks[feedback.id] = feedback;
    return feedback.id;
  }
  
  @override
  Future<Map<String, dynamic>> analyzeData(String dataId) async {
    final dataItem = _dataItems[dataId];
    if (dataItem == null) {
      throw Exception('Data item not found: $dataId');
    }
    
    // 简单的分析示例
    return {
      'data_id': dataId,
      'data_type': dataItem.type.toString(),
      'source': dataItem.source.toString(),
      'created_at': dataItem.createdAt.toIso8601String(),
      'has_annotations': dataItem.annotations != null,
    };
  }
  
  @override
  Future<LearningModelInfo> trainModel({
    required String modelName,
    required String agentId,
    Map<String, dynamic>? parameters,
    List<String>? dataIds,
  }) async {
    final modelId = 'model_${DateTime.now().millisecondsSinceEpoch}';
    final now = DateTime.now();
    
    final modelInfo = LearningModelInfo(
      id: modelId,
      name: modelName,
      version: '1.0.0',
      state: LearningModelState.training,
      createdAt: now,
      updatedAt: now,
      agentId: agentId,
      parameters: parameters,
      description: 'Trained model for agent $agentId',
    );
    
    _models[modelId] = modelInfo;
    
    // 模拟训练过程
    await Future.delayed(const Duration(seconds: 2));
    
    // 更新模型状态
    final updatedModelInfo = LearningModelInfo(
      id: modelId,
      name: modelName,
      version: '1.0.0',
      state: LearningModelState.active,
      createdAt: modelInfo.createdAt,
      updatedAt: DateTime.now(),
      agentId: agentId,
      parameters: parameters,
      description: 'Trained model for agent $agentId',
      metrics: {
        'accuracy': 0.85,
        'loss': 0.15,
        'training_time_ms': 2000,
      },
    );
    
    _models[modelId] = updatedModelInfo;
    
    return updatedModelInfo;
  }
  
  @override
  Future<Map<String, dynamic>> evaluateModel(String modelId, {
    List<String>? testDataIds,
    Map<String, dynamic>? evaluationParameters,
  }) async {
    final model = _models[modelId];
    if (model == null) {
      throw Exception('Model not found: $modelId');
    }
    
    // 模拟评估过程
    await Future.delayed(const Duration(seconds: 1));
    
    // 更新模型状态
    final updatedModel = LearningModelInfo(
      id: model.id,
      name: model.name,
      version: model.version,
      state: LearningModelState.active,
      createdAt: model.createdAt,
      updatedAt: DateTime.now(),
      agentId: model.agentId,
      parameters: model.parameters,
      description: model.description,
      metrics: {
        'accuracy': 0.87,
        'precision': 0.86,
        'recall': 0.85,
        'f1_score': 0.855,
      },
    );
    
    _models[modelId] = updatedModel;
    
    return updatedModel.metrics ?? {};
  }
  
  @override
  Future<bool> deployModel(String modelId, {
    String? targetAgentId,
    Map<String, dynamic>? deploymentParameters,
  }) async {
    final model = _models[modelId];
    if (model == null) {
      throw Exception('Model not found: $modelId');
    }
    
    // 模拟部署过程
    await Future.delayed(const Duration(seconds: 1));
    
    final updatedModel = LearningModelInfo(
      id: model.id,
      name: model.name,
      version: model.version,
      state: LearningModelState.active,
      createdAt: model.createdAt,
      updatedAt: DateTime.now(),
      agentId: targetAgentId ?? model.agentId,
      parameters: model.parameters,
      description: model.description,
      metrics: model.metrics,
    );
    
    _models[modelId] = updatedModel;
    
    return true;
  }
  
  @override
  Future<bool> archiveModel(String modelId) async {
    final model = _models[modelId];
    if (model == null) {
      throw Exception('Model not found: $modelId');
    }
    
    final updatedModel = LearningModelInfo(
      id: model.id,
      name: model.name,
      version: model.version,
      state: LearningModelState.archived,
      createdAt: model.createdAt,
      updatedAt: DateTime.now(),
      agentId: model.agentId,
      parameters: model.parameters,
      description: model.description,
      metrics: model.metrics,
    );
    
    _models[modelId] = updatedModel;
    
    return true;
  }
  
  @override
  Future<LearningModelInfo> getModelInfo(String modelId) async {
    final model = _models[modelId];
    if (model == null) {
      throw Exception('Model not found: $modelId');
    }
    
    return model;
  }
  
  @override
  Future<List<LearningModelInfo>> listModels({
    String? agentId,
    LearningModelState? state,
  }) async {
    return _models.values.where((model) {
      if (agentId != null && model.agentId != agentId) {
        return false;
      }
      
      if (state != null && model.state != state) {
        return false;
      }
      
      return true;
    }).toList();
  }
  
  @override
  Future<Uint8List> exportModel(String modelId) async {
    final model = _models[modelId];
    if (model == null) {
      throw Exception('Model not found: $modelId');
    }
    
    // 模拟模型导出
    // 实际应用中，这里应该将模型序列化为二进制数据
    return Uint8List.fromList([0, 1, 2, 3, 4]);
  }
  
  @override
  Future<String> importModel(Uint8List modelData, {
    String? modelName,
    String? agentId,
  }) async {
    // 模拟模型导入
    final modelId = 'imported_model_${DateTime.now().millisecondsSinceEpoch}';
    final now = DateTime.now();
    
    final modelInfo = LearningModelInfo(
      id: modelId,
      name: modelName ?? 'Imported Model',
      version: '1.0.0',
      state: LearningModelState.active,
      createdAt: now,
      updatedAt: now,
      agentId: agentId,
      description: 'Imported model',
    );
    
    _models[modelId] = modelInfo;
    
    return modelId;
  }
  
  @override
  Future<Map<String, dynamic>> getDataStatistics({
    DateTime? startDate,
    DateTime? endDate,
    String? agentId,
    String? userId,
  }) async {
    // 过滤数据
    final filteredData = _dataItems.values.where((data) {
      if (startDate != null && data.createdAt.isBefore(startDate)) {
        return false;
      }
      
      if (endDate != null && data.createdAt.isAfter(endDate)) {
        return false;
      }
      
      if (agentId != null && data.agentId != agentId) {
        return false;
      }
      
      if (userId != null && data.userId != userId) {
        return false;
      }
      
      return true;
    }).toList();
    
    // 计算统计信息
    final typeCount = <LearningDataType, int>{};
    final sourceCount = <LearningDataSource, int>{};
    
    for (final data in filteredData) {
      typeCount[data.type] = (typeCount[data.type] ?? 0) + 1;
      sourceCount[data.source] = (sourceCount[data.source] ?? 0) + 1;
    }
    
    return {
      'total_count': filteredData.length,
      'type_distribution': typeCount.map((key, value) => MapEntry(key.toString(), value)),
      'source_distribution': sourceCount.map((key, value) => MapEntry(key.toString(), value)),
      'time_range': {
        'start': filteredData.isEmpty ? null : filteredData.map((e) => e.createdAt).reduce((a, b) => a.isBefore(b) ? a : b).toIso8601String(),
        'end': filteredData.isEmpty ? null : filteredData.map((e) => e.createdAt).reduce((a, b) => a.isAfter(b) ? a : b).toIso8601String(),
      },
    };
  }
  
  @override
  Future<Map<String, dynamic>> getFeedbackStatistics({
    DateTime? startDate,
    DateTime? endDate,
    String? agentId,
    String? userId,
  }) async {
    // 过滤回馈
    final filteredFeedback = _feedbacks.values.where((feedback) {
      if (startDate != null && feedback.createdAt.isBefore(startDate)) {
        return false;
      }
      
      if (endDate != null && feedback.createdAt.isAfter(endDate)) {
        return false;
      }
      
      if (agentId != null && feedback.agentId != agentId) {
        return false;
      }
      
      if (userId != null && feedback.userId != userId) {
        return false;
      }
      
      return true;
    }).toList();
    
    // 计算统计信息
    final typeCount = <LearningFeedbackType, int>{};
    final ratingDistribution = <int, int>{};
    
    for (final feedback in filteredFeedback) {
      typeCount[feedback.type] = (typeCount[feedback.type] ?? 0) + 1;
      
      if (feedback.rating != null) {
        final ratingBucket = feedback.rating!.round();
        ratingDistribution[ratingBucket] = (ratingDistribution[ratingBucket] ?? 0) + 1;
      }
    }
    
    double? averageRating;
    if (filteredFeedback.any((f) => f.rating != null)) {
      final ratings = filteredFeedback.where((f) => f.rating != null).map((f) => f.rating!).toList();
      averageRating = ratings.reduce((a, b) => a + b) / ratings.length;
    }
    
    return {
      'total_count': filteredFeedback.length,
      'type_distribution': typeCount.map((key, value) => MapEntry(key.toString(), value)),
      'rating_distribution': ratingDistribution,
      'average_rating': averageRating,
      'time_range': {
        'start': filteredFeedback.isEmpty ? null : filteredFeedback.map((e) => e.createdAt).reduce((a, b) => a.isBefore(b) ? a : b).toIso8601String(),
        'end': filteredFeedback.isEmpty ? null : filteredFeedback.map((e) => e.createdAt).reduce((a, b) => a.isAfter(b) ? a : b).toIso8601String(),
      },
    };
  }
  
  @override
  Future<List<Map<String, dynamic>>> getModelPerformanceHistory(String modelId) async {
    // 模拟模型性能历史
    final model = _models[modelId];
    if (model == null) {
      throw Exception('Model not found: $modelId');
    }
    
    // 生成模拟数据
    final startDate = model.createdAt;
    final endDate = DateTime.now();
    final dayDiff = endDate.difference(startDate).inDays;
    
    final history = <Map<String, dynamic>>[];
    for (int i = 0; i <= dayDiff; i++) {
      final date = startDate.add(Duration(days: i));
      
      // 随机生成性能指标，但确保有上升趋势
      final progress = i / (dayDiff > 0 ? dayDiff : 1);
      final accuracy = 0.7 + (0.2 * progress) + (0.05 * (i % 2 == 0 ? 1 : -1) * progress);
      
      history.add({
        'date': date.toIso8601String(),
        'metrics': {
          'accuracy': accuracy.clamp(0.0, 1.0),
          'loss': (1 - accuracy).clamp(0.0, 1.0),
        },
      });
    }
    
    return history;
  }
  
  @override
  Future<Map<String, List<dynamic>>> getAgentLearningCurve(String agentId) async {
    // 获取代理相关的所有模型
    final agentModels = await listModels(agentId: agentId);
    
    if (agentModels.isEmpty) {
      return {
        'dates': <String>[],
        'accuracy': <double>[],
        'user_satisfaction': <double>[],
      };
    }
    
    // 生成模拟数据
    final startDate = agentModels.map((m) => m.createdAt).reduce((a, b) => a.isBefore(b) ? a : b);
    final endDate = DateTime.now();
    final dayDiff = endDate.difference(startDate).inDays;
    
    final dates = <String>[];
    final accuracy = <double>[];
    final userSatisfaction = <double>[];
    
    for (int i = 0; i <= dayDiff; i++) {
      final date = startDate.add(Duration(days: i));
      dates.add(date.toIso8601String());
      
      // 模拟学习曲线，随时间增长而提高
      final progress = i / (dayDiff > 0 ? dayDiff : 1);
      
      // 引入一些随机波动，但保持总体上升趋势
      final random = (i % 3 - 1) * 0.02;
      
      accuracy.add((0.7 + (0.25 * progress) + random).clamp(0.0, 1.0));
      userSatisfaction.add((0.65 + (0.3 * progress) + random).clamp(0.0, 1.0));
    }
    
    return {
      'dates': dates,
      'accuracy': accuracy,
      'user_satisfaction': userSatisfaction,
    };
  }
  
  // 私有辅助方法
  
  /// 从事件中提取知识
  Future<void> _extractKnowledgeFromEvent(LearningEvent event) async {
    // 实际实现中，这里应该有复杂的知识提取逻辑
    // 简化实现：从事件数据创建一个知识单元
    
    if (event.data.containsKey('domain') && event.data.containsKey('concept')) {
      final knowledgeId = 'knowledge_${event.id}';
      final knowledge = KnowledgeUnit(
        id: knowledgeId,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        domain: event.data['domain'],
        concept: event.data['concept'],
        attributes: Map.from(event.data)..remove('domain')..remove('concept'),
        confidence: event.importance ?? 0.5,
        relatedKnowledgeIds: [],
      );
      
      await addKnowledge(knowledge);
    }
  }
  
  /// 计算平均置信度
  double _calculateAverageConfidence() {
    if (_knowledgeUnits.isEmpty) return 0.0;
    
    final sum = _knowledgeUnits.values.fold<double>(
      0.0, 
      (sum, unit) => sum + unit.confidence
    );
    
    return sum / _knowledgeUnits.length;
  }
} 