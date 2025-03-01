import 'dart:async';

import '../core/agent_microkernel.dart';
import '../models/ai_agent.dart';
import '../core/autonomous_learning_system.dart';
import '../rag/rag_service.dart';
import '../collaboration/agent_collaboration.dart';
import '../../core/utils/logger.dart';

/// 健康数据类型
enum HealthDataType {
  /// 营养摄入数据
  nutrition,

  /// 运动数据
  exercise,

  /// 睡眠数据
  sleep,

  /// 体重数据
  weight,

  /// 心率数据
  heartRate,

  /// 血压数据
  bloodPressure,

  /// 血糖数据
  bloodGlucose,

  /// 情绪数据
  mood,

  /// 水分摄入
  waterIntake,
}

/// 健康状态评级
enum HealthStatusRating {
  /// 需要注意
  needsAttention,

  /// 正常范围
  normal,

  /// 良好状态
  good,

  /// 优秀状态
  excellent,
}

/// 健康数据记录
class HealthDataRecord {
  /// 记录ID
  final String id;

  /// 用户ID
  final String userId;

  /// 数据类型
  final HealthDataType type;

  /// 数据值
  final dynamic value;

  /// 单位
  final String? unit;

  /// 记录时间
  final DateTime timestamp;

  /// 备注
  final String? notes;

  HealthDataRecord({
    required this.id,
    required this.userId,
    required this.type,
    required this.value,
    this.unit,
    DateTime? timestamp,
    this.notes,
  }) : timestamp = timestamp ?? DateTime.now();

  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'type': type.toString(),
      'value': value,
      'unit': unit,
      'timestamp': timestamp.toIso8601String(),
      'notes': notes,
    };
  }

  /// 从Map创建
  factory HealthDataRecord.fromMap(Map<String, dynamic> map) {
    return HealthDataRecord(
      id: map['id'],
      userId: map['userId'],
      type: HealthDataType.values.firstWhere(
        (e) => e.toString() == map['type'],
        orElse: () => HealthDataType.nutrition,
      ),
      value: map['value'],
      unit: map['unit'],
      timestamp: DateTime.parse(map['timestamp']),
      notes: map['notes'],
    );
  }
}

/// 健康目标
class HealthGoal {
  /// 目标ID
  final String id;

  /// 用户ID
  final String userId;

  /// 目标类型
  final HealthDataType type;

  /// 目标值
  final dynamic targetValue;

  /// 单位
  final String? unit;

  /// 开始时间
  final DateTime startDate;

  /// 结束时间
  final DateTime targetDate;

  /// 目标描述
  final String description;

  /// 是否已完成
  bool completed;

  /// 进度（0-100）
  double progress;

  HealthGoal({
    required this.id,
    required this.userId,
    required this.type,
    required this.targetValue,
    this.unit,
    required this.startDate,
    required this.targetDate,
    required this.description,
    this.completed = false,
    this.progress = 0.0,
  });

  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'type': type.toString(),
      'targetValue': targetValue,
      'unit': unit,
      'startDate': startDate.toIso8601String(),
      'targetDate': targetDate.toIso8601String(),
      'description': description,
      'completed': completed,
      'progress': progress,
    };
  }

  /// 从Map创建
  factory HealthGoal.fromMap(Map<String, dynamic> map) {
    return HealthGoal(
      id: map['id'],
      userId: map['userId'],
      type: HealthDataType.values.firstWhere(
        (e) => e.toString() == map['type'],
        orElse: () => HealthDataType.nutrition,
      ),
      targetValue: map['targetValue'],
      unit: map['unit'],
      startDate: DateTime.parse(map['startDate']),
      targetDate: DateTime.parse(map['targetDate']),
      description: map['description'],
      completed: map['completed'] ?? false,
      progress: (map['progress'] ?? 0.0).toDouble(),
    );
  }
}

/// 健康建议
class HealthRecommendation {
  /// 建议ID
  final String id;

  /// 用户ID
  final String userId;

  /// 建议类型
  final HealthDataType type;

  /// 建议内容
  final String content;

  /// 建议原因
  final String reason;

  /// 优先级（1-10，10为最高）
  final int priority;

  /// 创建时间
  final DateTime createdAt;

  HealthRecommendation({
    required this.id,
    required this.userId,
    required this.type,
    required this.content,
    required this.reason,
    required this.priority,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'type': type.toString(),
      'content': content,
      'reason': reason,
      'priority': priority,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  /// 从Map创建
  factory HealthRecommendation.fromMap(Map<String, dynamic> map) {
    return HealthRecommendation(
      id: map['id'],
      userId: map['userId'],
      type: HealthDataType.values.firstWhere(
        (e) => e.toString() == map['type'],
        orElse: () => HealthDataType.nutrition,
      ),
      content: map['content'],
      reason: map['reason'],
      priority: map['priority'] ?? 5,
      createdAt: DateTime.parse(map['createdAt']),
    );
  }
}

/// 健康状态报告
class HealthStatusReport {
  /// 报告ID
  final String id;

  /// 用户ID
  final String userId;

  /// 整体健康评分（0-100）
  final double overallScore;

  /// 营养状态评级
  final HealthStatusRating nutritionStatus;

  /// 运动状态评级
  final HealthStatusRating exerciseStatus;

  /// 睡眠状态评级
  final HealthStatusRating sleepStatus;

  /// 压力与情绪状态评级
  final HealthStatusRating stressStatus;

  /// 报告内容摘要
  final String summary;

  /// 报告详细内容
  final Map<String, dynamic> details;

  /// 建议列表
  final List<HealthRecommendation> recommendations;

  /// 创建时间
  final DateTime createdAt;

  HealthStatusReport({
    required this.id,
    required this.userId,
    required this.overallScore,
    required this.nutritionStatus,
    required this.exerciseStatus,
    required this.sleepStatus,
    required this.stressStatus,
    required this.summary,
    required this.details,
    required this.recommendations,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'overallScore': overallScore,
      'nutritionStatus': nutritionStatus.toString(),
      'exerciseStatus': exerciseStatus.toString(),
      'sleepStatus': sleepStatus.toString(),
      'stressStatus': stressStatus.toString(),
      'summary': summary,
      'details': details,
      'recommendations': recommendations.map((r) => r.toMap()).toList(),
      'createdAt': createdAt.toIso8601String(),
    };
  }
}

/// 健康管理代理接口
abstract class HealthManagementAgent {
  /// 代理ID
  String get id;

  /// 代理名称
  String get name;

  /// 记录健康数据
  Future<String> recordHealthData(HealthDataRecord record);

  /// 批量记录健康数据
  Future<List<String>> recordHealthDataBatch(List<HealthDataRecord> records);

  /// 获取健康数据记录
  Future<List<HealthDataRecord>> getHealthData(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
  });

  /// 创建健康目标
  Future<String> createHealthGoal(HealthGoal goal);

  /// 更新健康目标进度
  Future<void> updateGoalProgress(String goalId, double progress);

  /// 完成健康目标
  Future<void> completeGoal(String goalId);

  /// 获取用户健康目标
  Future<List<HealthGoal>> getUserGoals(String userId, {bool? active});

  /// 生成营养建议
  Future<HealthRecommendation> generateNutritionRecommendation(String userId);

  /// 生成运动建议
  Future<HealthRecommendation> generateExerciseRecommendation(String userId);

  /// 生成睡眠建议
  Future<HealthRecommendation> generateSleepRecommendation(String userId);

  /// 生成健康状态报告
  Future<HealthStatusReport> generateHealthReport(String userId);
}

/// 基础健康管理代理实现
class BaseHealthManagementAgent implements HealthManagementAgent {
  final AIAgent _agent;
  final AutonomousLearningSystem _learningSystem;
  final RAGService _ragService;

  final Map<String, List<HealthDataRecord>> _healthData = {};
  final Map<String, List<HealthGoal>> _healthGoals = {};

  final AgentCollaborationManager _collaborationManager;

  BaseHealthManagementAgent(
    this._agent,
    this._learningSystem,
    this._ragService,
    AgentMicrokernel microkernel,
  ) : _collaborationManager = AgentCollaborationManager(
        microkernel,
        _agent.id,
      ) {
    _initializeCollaborationHandlers();
  }

  /// 初始化协作处理器
  void _initializeCollaborationHandlers() {
    // 注册数据共享请求处理器
    _collaborationManager.registerHandler(
      CollaborationRequestType.dataSharing,
      _handleDataSharingRequest,
    );

    // 注册分析请求处理器
    _collaborationManager.registerHandler(
      CollaborationRequestType.analysis,
      _handleAnalysisRequest,
    );
  }

  /// 处理数据共享请求
  Future<CollaborationResult> _handleDataSharingRequest(
    CollaborationRequest request,
  ) async {
    try {
      final dataType = request.data['dataType'];
      final userId = request.data['userId'];

      if (dataType == 'health_records') {
        // 获取用户健康记录
        final recordType = request.data['recordType'];
        final healthData = await getHealthData(
          userId,
          _parseHealthDataType(recordType),
          startDate:
              request.data['startDate'] != null
                  ? DateTime.parse(request.data['startDate'])
                  : null,
          endDate:
              request.data['endDate'] != null
                  ? DateTime.parse(request.data['endDate'])
                  : null,
        );

        // 转换为可共享的格式
        final shareableData =
            healthData.map((record) => record.toMap()).toList();

        return request.createResponse(
          status: CollaborationResultStatus.success,
          resultData: {
            'healthData': shareableData,
            'dataType': dataType,
            'recordType': recordType,
          },
        );
      } else if (dataType == 'health_goals') {
        // 获取用户健康目标
        final active = request.data['active'] as bool?;
        final goals = await getUserGoals(userId, active: active);

        // 转换为可共享的格式
        final shareableGoals = goals.map((goal) => goal.toMap()).toList();

        return request.createResponse(
          status: CollaborationResultStatus.success,
          resultData: {'healthGoals': shareableGoals, 'dataType': dataType},
        );
      }

      return request.createResponse(
        status: CollaborationResultStatus.failure,
        resultData: {},
        message: '不支持的数据类型: $dataType',
      );
    } catch (e) {
      logger.e('处理数据共享请求失败', error: e);

      return request.createResponse(
        status: CollaborationResultStatus.failure,
        resultData: {},
        message: '处理请求出错: $e',
      );
    }
  }

  /// 处理分析请求
  Future<CollaborationResult> _handleAnalysisRequest(
    CollaborationRequest request,
  ) async {
    try {
      final analysisType = request.data['analysisType'];
      final userId = request.data['userId'];

      if (analysisType == 'nutrition_analysis') {
        // 生成营养分析
        final recommendation = await generateNutritionRecommendation(userId);

        return request.createResponse(
          status: CollaborationResultStatus.success,
          resultData: {
            'recommendation': recommendation.toMap(),
            'analysisType': analysisType,
          },
        );
      } else if (analysisType == 'exercise_analysis') {
        // 生成运动分析
        final recommendation = await generateExerciseRecommendation(userId);

        return request.createResponse(
          status: CollaborationResultStatus.success,
          resultData: {
            'recommendation': recommendation.toMap(),
            'analysisType': analysisType,
          },
        );
      } else if (analysisType == 'sleep_analysis') {
        // 生成睡眠分析
        final recommendation = await generateSleepRecommendation(userId);

        return request.createResponse(
          status: CollaborationResultStatus.success,
          resultData: {
            'recommendation': recommendation.toMap(),
            'analysisType': analysisType,
          },
        );
      }

      return request.createResponse(
        status: CollaborationResultStatus.failure,
        resultData: {},
        message: '不支持的分析类型: $analysisType',
      );
    } catch (e) {
      logger.e('处理分析请求失败', error: e);

      return request.createResponse(
        status: CollaborationResultStatus.failure,
        resultData: {},
        message: '处理请求出错: $e',
      );
    }
  }

  /// 解析健康数据类型
  HealthDataType _parseHealthDataType(String typeStr) {
    return HealthDataType.values.firstWhere(
      (type) => type.toString().split('.').last == typeStr,
      orElse: () => HealthDataType.nutrition,
    );
  }

  @override
  String get id => _agent.id;

  @override
  String get name => _agent.name;

  @override
  Future<String> recordHealthData(HealthDataRecord record) async {
    _healthData.putIfAbsent(record.userId, () => []).add(record);

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: record.id,
        type: LearningDataType.structured,
        source: LearningDataSource.userInput,
        content: record.toMap(),
        agentId: id,
        userId: record.userId,
      ),
    );

    return record.id;
  }

  @override
  Future<List<String>> recordHealthDataBatch(
    List<HealthDataRecord> records,
  ) async {
    final ids = <String>[];

    for (final record in records) {
      ids.add(await recordHealthData(record));
    }

    return ids;
  }

  @override
  Future<List<HealthDataRecord>> getHealthData(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final userRecords = _healthData[userId] ?? [];

    return userRecords.where((record) {
      if (record.type != type) return false;

      if (startDate != null && record.timestamp.isBefore(startDate))
        return false;
      if (endDate != null && record.timestamp.isAfter(endDate)) return false;

      return true;
    }).toList();
  }

  @override
  Future<String> createHealthGoal(HealthGoal goal) async {
    _healthGoals.putIfAbsent(goal.userId, () => []).add(goal);

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: goal.id,
        type: LearningDataType.structured,
        source: LearningDataSource.userInput,
        content: goal.toMap(),
        agentId: id,
        userId: goal.userId,
      ),
    );

    return goal.id;
  }

  @override
  Future<void> updateGoalProgress(String goalId, double progress) async {
    for (final goals in _healthGoals.values) {
      for (final goal in goals) {
        if (goal.id == goalId) {
          goal.progress = progress.clamp(0.0, 100.0);
          if (goal.progress >= 100.0) {
            goal.completed = true;
          }
          return;
        }
      }
    }

    throw Exception('Goal not found: $goalId');
  }

  @override
  Future<void> completeGoal(String goalId) async {
    for (final goals in _healthGoals.values) {
      for (final goal in goals) {
        if (goal.id == goalId) {
          goal.completed = true;
          goal.progress = 100.0;
          return;
        }
      }
    }

    throw Exception('Goal not found: $goalId');
  }

  @override
  Future<List<HealthGoal>> getUserGoals(String userId, {bool? active}) async {
    final goals = _healthGoals[userId] ?? [];

    if (active == null) {
      return goals;
    }

    return goals.where((goal) => goal.completed != active).toList();
  }

  @override
  Future<HealthRecommendation> generateNutritionRecommendation(
    String userId,
  ) async {
    // 获取用户的营养数据
    final nutritionData = await getHealthData(
      userId,
      HealthDataType.nutrition,
      startDate: DateTime.now().subtract(const Duration(days: 7)),
    );

    // 使用RAG服务获取相关营养知识
    final ragResults = await _ragService.query(
      '健康均衡饮食推荐',
      collection: 'nutrition_knowledge',
      limit: 3,
    );

    // 在实际应用中，应使用更复杂的营养分析模型
    final String content;
    final String reason;

    if (nutritionData.isEmpty) {
      // 如果没有数据，提供通用建议
      content = '增加蔬果摄入量，每天至少摄入五份蔬菜水果，多样化搭配食材，保证充足蛋白质摄入。';
      reason = '均衡的营养摄入是健康的基础。';
    } else {
      // 简单分析数据，实际应用中应更复杂
      content = '根据您的饮食记录，建议适当增加优质蛋白质摄入，每天保证摄入足够的膳食纤维。';
      reason = '您的食物摄入结构需要更加均衡。';
    }

    // 创建建议
    final recommendation = HealthRecommendation(
      id: 'rec_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      type: HealthDataType.nutrition,
      content: content,
      reason: reason,
      priority: 7,
    );

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: recommendation.id,
        type: LearningDataType.structured,
        source: LearningDataSource.agentGenerated,
        content: recommendation.toMap(),
        agentId: id,
        userId: userId,
      ),
    );

    return recommendation;
  }

  @override
  Future<HealthRecommendation> generateExerciseRecommendation(
    String userId,
  ) async {
    // 获取用户的运动数据
    final exerciseData = await getHealthData(
      userId,
      HealthDataType.exercise,
      startDate: DateTime.now().subtract(const Duration(days: 7)),
    );

    // 使用RAG服务获取相关运动知识
    final ragResults = await _ragService.query(
      '适合日常的运动方案',
      collection: 'exercise_knowledge',
      limit: 3,
    );

    // 在实际应用中，应使用更复杂的运动分析模型
    final String content;
    final String reason;

    if (exerciseData.isEmpty) {
      // 如果没有数据，提供通用建议
      content = '建议每周进行至少150分钟中等强度有氧运动，如快走、游泳或骑自行车，并加入两天力量训练。';
      reason = '规律的体育锻炼有助于维持健康体重和降低慢性疾病风险。';
    } else {
      // 简单分析数据，实际应用中应更复杂
      content = '根据您的运动记录，建议增加力量训练的比例，每周安排2-3次，每次30分钟的力量训练。';
      reason = '力量训练有助于提高基础代谢率和肌肉力量。';
    }

    // 创建建议
    final recommendation = HealthRecommendation(
      id: 'rec_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      type: HealthDataType.exercise,
      content: content,
      reason: reason,
      priority: 6,
    );

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: recommendation.id,
        type: LearningDataType.structured,
        source: LearningDataSource.agentGenerated,
        content: recommendation.toMap(),
        agentId: id,
        userId: userId,
      ),
    );

    return recommendation;
  }

  @override
  Future<HealthRecommendation> generateSleepRecommendation(
    String userId,
  ) async {
    // 获取用户的睡眠数据
    final sleepData = await getHealthData(
      userId,
      HealthDataType.sleep,
      startDate: DateTime.now().subtract(const Duration(days: 7)),
    );

    // 使用RAG服务获取相关睡眠知识
    final ragResults = await _ragService.query(
      '健康睡眠建议',
      collection: 'sleep_knowledge',
      limit: 3,
    );

    // 在实际应用中，应使用更复杂的睡眠分析模型
    final String content;
    final String reason;

    if (sleepData.isEmpty) {
      // 如果没有数据，提供通用建议
      content = '成年人应保证每晚7-9小时的睡眠，建立规律的睡眠时间，睡前1小时避免使用电子设备。';
      reason = '充足的睡眠是身体恢复和精神健康的关键。';
    } else {
      // 简单分析数据，实际应用中应更复杂
      content = '根据您的睡眠记录，建议将睡觉时间提前30分钟，保持睡前环境安静，温度适宜。';
      reason = '提高睡眠质量有助于提升日间能量水平和认知功能。';
    }

    // 创建建议
    final recommendation = HealthRecommendation(
      id: 'rec_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      type: HealthDataType.sleep,
      content: content,
      reason: reason,
      priority: 8,
    );

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: recommendation.id,
        type: LearningDataType.structured,
        source: LearningDataSource.agentGenerated,
        content: recommendation.toMap(),
        agentId: id,
        userId: userId,
      ),
    );

    return recommendation;
  }

  /// 请求医学诊断
  Future<DiagnosisResult?> requestMedicalDiagnosis({
    required String userId,
    required String targetAgentId,
    required List<String> symptoms,
    Map<String, String>? examinations,
    String? medicalHistory,
    bool useTCM = true,
  }) async {
    try {
      // 准备请求数据
      final requestData = {
        'userId': userId,
        'symptoms': symptoms,
        'useTCM': useTCM,
      };

      // 添加可选数据
      if (examinations != null) {
        requestData['examinations'] = examinations;
      }

      if (medicalHistory != null) {
        requestData['medicalHistory'] = medicalHistory;
      }

      // 创建联合诊断请求
      final request = _collaborationManager.createJointDiagnosisRequest(
        targetAgentId: targetAgentId,
        data: requestData,
        context: {
          'purpose': 'health_report_diagnosis',
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      // 发送请求
      final result = await _collaborationManager.sendCollaborationRequest(
        request,
      );

      // 处理结果
      if (result.isSuccess) {
        // 从结果中提取诊断结果
        final diagnosisMap = result.data['diagnosis'] as Map<String, dynamic>;

        // 转换为DiagnosisResult对象
        return DiagnosisResult.fromMap(diagnosisMap);
      } else {
        logger.w('请求医学诊断失败: ${result.message}');
        return null;
      }
    } catch (e) {
      logger.e('请求医学诊断出错', error: e);
      return null;
    }
  }

  /// 共享健康数据
  Future<bool> shareHealthData({
    required String userId,
    required String targetAgentId,
    required HealthDataType dataType,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 获取健康数据
      final healthData = await getHealthData(
        userId,
        dataType,
        startDate: startDate,
        endDate: endDate,
      );

      // 创建数据共享请求
      final request = _collaborationManager.createDataSharingRequest(
        targetAgentId: targetAgentId,
        data: {
          'dataType': 'health_records',
          'recordType': dataType.toString().split('.').last,
          'userId': userId,
          'startDate': startDate?.toIso8601String(),
          'endDate': endDate?.toIso8601String(),
          'records': healthData.map((record) => record.toMap()).toList(),
        },
      );

      // 发送请求
      final result = await _collaborationManager.sendCollaborationRequest(
        request,
      );

      return result.isSuccess;
    } catch (e) {
      logger.e('共享健康数据失败', error: e);
      return false;
    }
  }

  @override
  Future<HealthStatusReport> generateHealthReport(String userId) async {
    try {
      // 收集用户数据
      final nutritionData = await getHealthData(
        userId,
        HealthDataType.nutrition,
        startDate: DateTime.now().subtract(const Duration(days: 30)),
      );

      final exerciseData = await getHealthData(
        userId,
        HealthDataType.exercise,
        startDate: DateTime.now().subtract(const Duration(days: 30)),
      );

      final sleepData = await getHealthData(
        userId,
        HealthDataType.sleep,
        startDate: DateTime.now().subtract(const Duration(days: 30)),
      );

      final moodData = await getHealthData(
        userId,
        HealthDataType.mood,
        startDate: DateTime.now().subtract(const Duration(days: 30)),
      );

      // 生成各方面建议
      final nutritionRecommendation = await generateNutritionRecommendation(
        userId,
      );
      final exerciseRecommendation = await generateExerciseRecommendation(
        userId,
      );
      final sleepRecommendation = await generateSleepRecommendation(userId);

      // 尝试获取医学诊断
      DiagnosisResult? medicalDiagnosis;
      String? medicalAdvice;

      // 查找可用的医学诊断代理
      // 实际项目中应使用代理注册表查找代理
      const tcmDiagnosisAgentId = 'tcm_diagnosis';

      // 从用户的健康记录中提取症状
      final symptoms = _extractSymptoms(
        nutritionData,
        exerciseData,
        sleepData,
        moodData,
      );

      if (symptoms.isNotEmpty) {
        // 请求医学诊断
        medicalDiagnosis = await requestMedicalDiagnosis(
          userId: userId,
          targetAgentId: tcmDiagnosisAgentId,
          symptoms: symptoms,
          useTCM: true, // 使用中医诊断
        );

        if (medicalDiagnosis != null) {
          medicalAdvice = medicalDiagnosis.recommendation;
        }
      }

      // 在实际应用中，应使用专业的健康评估模型
      // 这里使用简化的评分和状态评级计算

      // 评估营养状态
      final nutritionRating =
          nutritionData.isEmpty
              ? HealthStatusRating.normal
              : HealthStatusRating.good;

      // 评估运动状态
      final exerciseRating =
          exerciseData.isEmpty
              ? HealthStatusRating.needsAttention
              : HealthStatusRating.normal;

      // 评估睡眠状态
      final sleepRating =
          sleepData.isEmpty
              ? HealthStatusRating.normal
              : HealthStatusRating.good;

      // 评估压力状态
      final stressRating =
          moodData.isEmpty
              ? HealthStatusRating.normal
              : HealthStatusRating.good;

      // 计算整体健康评分（0-100）
      final overallScore = _calculateOverallScore(
        nutritionRating,
        exerciseRating,
        sleepRating,
        stressRating,
      );

      // 创建详细报告
      final details = <String, dynamic>{
        'nutrition': {
          'dataCount': nutritionData.length,
          'status': nutritionRating.toString(),
          'details': nutritionData.isEmpty ? '暂无数据' : '数据分析结果',
        },
        'exercise': {
          'dataCount': exerciseData.length,
          'status': exerciseRating.toString(),
          'details': exerciseData.isEmpty ? '暂无数据' : '数据分析结果',
        },
        'sleep': {
          'dataCount': sleepData.length,
          'status': sleepRating.toString(),
          'details': sleepData.isEmpty ? '暂无数据' : '数据分析结果',
        },
        'stress': {
          'dataCount': moodData.length,
          'status': stressRating.toString(),
          'details': moodData.isEmpty ? '暂无数据' : '数据分析结果',
        },
      };

      // 如果有医学诊断，添加到详细报告中
      if (medicalDiagnosis != null) {
        details['medical_diagnosis'] = {
          'diagnosis': medicalDiagnosis.diagnosis,
          'confidence': medicalDiagnosis.confidenceLevel.toString(),
          'recommendation': medicalDiagnosis.recommendation,
          'is_tcm': medicalDiagnosis.isTraditionalChinese,
        };
      }

      // 生成报告摘要
      final summary = _generateReportSummary(
        overallScore,
        nutritionRating,
        exerciseRating,
        sleepRating,
        stressRating,
        medicalAdvice: medicalAdvice,
      );

      // 收集所有建议
      final allRecommendations = [
        nutritionRecommendation,
        exerciseRecommendation,
        sleepRecommendation,
      ];

      // 如果有医学建议，创建一个健康建议对象
      if (medicalAdvice != null) {
        final medicalRecommendation = HealthRecommendation(
          id: 'med_rec_${DateTime.now().millisecondsSinceEpoch}',
          userId: userId,
          type: HealthDataType.nutrition, // 使用统一的类型
          content: medicalAdvice,
          reason: medicalDiagnosis?.diagnosis ?? '基于医学诊断的建议',
          priority: 9, // 医学建议优先级高
        );
        allRecommendations.add(medicalRecommendation);
      }

      // 创建健康状态报告
      final report = HealthStatusReport(
        id: 'report_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        overallScore: overallScore,
        nutritionStatus: nutritionRating,
        exerciseStatus: exerciseRating,
        sleepStatus: sleepRating,
        stressStatus: stressRating,
        summary: summary,
        details: details,
        recommendations: allRecommendations,
      );

      // 记录学习数据
      await _learningSystem.collectData(
        LearningDataItem(
          id: report.id,
          type: LearningDataType.structured,
          source: LearningDataSource.agentGenerated,
          content: report.toMap(),
          agentId: id,
          userId: userId,
        ),
      );

      return report;
    } catch (e, stackTrace) {
      logger.e('生成健康报告失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// 从健康数据中提取可能的症状
  List<String> _extractSymptoms(
    List<HealthDataRecord> nutritionData,
    List<HealthDataRecord> exerciseData,
    List<HealthDataRecord> sleepData,
    List<HealthDataRecord> moodData,
  ) {
    final symptoms = <String>[];

    // 从睡眠数据中提取可能的症状
    if (sleepData.isNotEmpty) {
      // 检查睡眠时长
      final recentSleepData = sleepData.take(7).toList(); // 取最近7条记录
      if (recentSleepData.length >= 3) {
        // 计算平均睡眠时长
        final avgSleepHours =
            recentSleepData
                .map((record) => (record.value as num).toDouble())
                .reduce((a, b) => a + b) /
            recentSleepData.length;

        if (avgSleepHours < 6) {
          symptoms.add('睡眠不足，平均每晚睡眠时间少于6小时');
        } else if (avgSleepHours > 9) {
          symptoms.add('睡眠过多，平均每晚睡眠时间超过9小时');
        }
      }
    }

    // 从情绪数据中提取可能的症状
    if (moodData.isNotEmpty) {
      // 检查情绪波动
      final negativeMoods =
          moodData.where((record) {
            final moodValue = record.value;
            return moodValue is String &&
                (moodValue.contains('焦虑') ||
                    moodValue.contains('抑郁') ||
                    moodValue.contains('烦躁'));
          }).toList();

      if (negativeMoods.length > moodData.length / 2) {
        symptoms.add('负面情绪较多，可能存在心理压力');
      }
    }

    // 从营养数据中提取可能的症状
    if (nutritionData.isNotEmpty) {
      // 检查饮食规律性
      final irregularMeals =
          nutritionData.where((record) {
            return record.notes != null &&
                (record.notes!.contains('不规律') || record.notes!.contains('跳过'));
          }).toList();

      if (irregularMeals.length > nutritionData.length / 3) {
        symptoms.add('饮食不规律，经常跳过正餐');
      }
    }

    // 从运动数据中提取可能的症状
    if (exerciseData.isEmpty) {
      symptoms.add('缺乏运动');
    } else {
      // 检查运动强度
      final lowIntensityExercises =
          exerciseData.where((record) {
            return record.notes != null && record.notes!.contains('低强度');
          }).toList();

      if (lowIntensityExercises.length == exerciseData.length) {
        symptoms.add('运动强度不足');
      }
    }

    return symptoms;
  }

  /// 计算整体健康评分
  double _calculateOverallScore(
    HealthStatusRating nutritionRating,
    HealthStatusRating exerciseRating,
    HealthStatusRating sleepRating,
    HealthStatusRating stressRating,
  ) {
    // 将评级转换为分数（0-25）
    double nutritionScore = _ratingToScore(nutritionRating);
    double exerciseScore = _ratingToScore(exerciseRating);
    double sleepScore = _ratingToScore(sleepRating);
    double stressScore = _ratingToScore(stressRating);

    // 计算总分（0-100）
    return nutritionScore + exerciseScore + sleepScore + stressScore;
  }

  /// 将评级转换为分数
  double _ratingToScore(HealthStatusRating rating) {
    switch (rating) {
      case HealthStatusRating.needsAttention:
        return 10.0;
      case HealthStatusRating.normal:
        return 15.0;
      case HealthStatusRating.good:
        return 20.0;
      case HealthStatusRating.excellent:
        return 25.0;
    }
  }

  /// 生成报告摘要
  String _generateReportSummary(
    double overallScore,
    HealthStatusRating nutritionRating,
    HealthStatusRating exerciseRating,
    HealthStatusRating sleepRating,
    HealthStatusRating stressRating, {
    String? medicalAdvice,
  }) {
    final StringBuilder summary = StringBuilder();

    if (overallScore >= 80) {
      summary.appendLine('您的整体健康状况良好。继续保持当前的健康生活方式，并考虑一些微小的改进以达到最佳状态。');
    } else if (overallScore >= 60) {
      summary.appendLine('您的整体健康状况处于正常范围，但有改进空间。关注报告中的建议以提升您的健康水平。');
    } else {
      summary.appendLine('您的健康状况需要更多关注。请认真查看报告中的建议，并考虑咨询专业医疗人员。');
    }

    summary.appendLine('\n主要发现：');

    // 添加各方面分析
    if (nutritionRating == HealthStatusRating.needsAttention) {
      summary.appendLine('- 您的营养状况需要改善，建议更加关注饮食均衡。');
    }

    if (exerciseRating == HealthStatusRating.needsAttention) {
      summary.appendLine('- 您的运动量不足，增加日常活动和有规律的锻炼非常重要。');
    }

    if (sleepRating == HealthStatusRating.needsAttention) {
      summary.appendLine('- 您的睡眠质量有待提高，良好的睡眠对整体健康至关重要。');
    }

    if (stressRating == HealthStatusRating.needsAttention) {
      summary.appendLine('- 您的压力水平较高，寻找有效的减压方法会对健康有很大帮助。');
    }

    // 如果有医学建议，添加到摘要中
    if (medicalAdvice != null && medicalAdvice.isNotEmpty) {
      summary.appendLine('\n医学建议：');
      summary.appendLine(medicalAdvice);
    }

    return summary.toString();
  }
}

/// 营养管理代理
class NutritionManagementAgent extends BaseHealthManagementAgent {
  NutritionManagementAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  // 可以添加特定于营养管理的方法
}

/// 运动管理代理
class ExerciseManagementAgent extends BaseHealthManagementAgent {
  ExerciseManagementAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  // 可以添加特定于运动管理的方法
}

/// 睡眠管理代理
class SleepManagementAgent extends BaseHealthManagementAgent {
  SleepManagementAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  // 可以添加特定于睡眠管理的方法
}

/// 心理健康管理代理
class MentalHealthManagementAgent extends BaseHealthManagementAgent {
  MentalHealthManagementAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  // 可以添加特定于心理健康管理的方法
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
