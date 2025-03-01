import 'dart:async';

import '../core/agent_microkernel.dart';
import '../collaboration/agent_collaboration.dart';
import '../models/ai_agent.dart';
import '../core/autonomous_learning_system.dart';
import '../rag/rag_service.dart';
import '../../core/utils/logger.dart';

/// 诊断结果置信度
enum DiagnosisConfidenceLevel {
  /// 低置信度
  low,

  /// 中等置信度
  medium,

  /// 高置信度
  high,

  /// 非常高置信度
  veryHigh,
}

/// 诊断结果
class DiagnosisResult {
  /// 诊断ID
  final String id;

  /// 用户ID
  final String userId;

  /// 症状描述
  final String symptoms;

  /// 诊断结果
  final String diagnosis;

  /// 建议处理方案
  final String? recommendation;

  /// 参考资料
  final List<String>? references;

  /// 置信度
  final DiagnosisConfidenceLevel confidenceLevel;

  /// 创建时间
  final DateTime timestamp;

  /// 诊断类型（中医/西医）
  final bool isTraditionalChinese;

  DiagnosisResult({
    required this.id,
    required this.userId,
    required this.symptoms,
    required this.diagnosis,
    this.recommendation,
    this.references,
    required this.confidenceLevel,
    required this.isTraditionalChinese,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'symptoms': symptoms,
      'diagnosis': diagnosis,
      'recommendation': recommendation,
      'references': references,
      'confidenceLevel': confidenceLevel.toString(),
      'timestamp': timestamp.toIso8601String(),
      'isTraditionalChinese': isTraditionalChinese,
    };
  }

  /// 从Map创建
  factory DiagnosisResult.fromMap(Map<String, dynamic> map) {
    return DiagnosisResult(
      id: map['id'],
      userId: map['userId'],
      symptoms: map['symptoms'],
      diagnosis: map['diagnosis'],
      recommendation: map['recommendation'],
      references:
          map['references'] != null
              ? List<String>.from(map['references'])
              : null,
      confidenceLevel: DiagnosisConfidenceLevel.values.firstWhere(
        (e) => e.toString() == map['confidenceLevel'],
        orElse: () => DiagnosisConfidenceLevel.medium,
      ),
      isTraditionalChinese: map['isTraditionalChinese'] ?? false,
      timestamp: DateTime.parse(map['timestamp']),
    );
  }
}

/// 医学诊断代理接口
abstract class MedicalDiagnosisAgent {
  /// 代理ID
  String get id;

  /// 代理名称
  String get name;

  /// 是否支持中医诊断
  bool get supportTraditionalChinese;

  /// 是否支持西医诊断
  bool get supportWesternMedicine;

  /// 添加症状描述
  Future<void> addSymptoms(String userId, String symptoms);

  /// 添加检查结果
  Future<void> addExaminationResult(
    String userId,
    String examType,
    String result,
  );

  /// 添加病史
  Future<void> addMedicalHistory(String userId, String history);

  /// 获取诊断结果
  Future<DiagnosisResult> getDiagnosis(String userId);

  /// 获取诊断建议
  Future<String> getTreatmentSuggestion(
    String userId,
    DiagnosisResult diagnosis,
  );

  /// 获取中医辩证分析
  Future<String> getTCMAnalysis(String userId);

  /// 获取西医病理分析
  Future<String> getWesternMedicalAnalysis(String userId);
}

/// 基础医学诊断代理实现
class BaseMedicalDiagnosisAgent implements MedicalDiagnosisAgent {
  final AIAgent _agent;
  final AutonomousLearningSystem _learningSystem;
  final RAGService _ragService;

  final Map<String, List<String>> _userSymptoms = {};
  final Map<String, Map<String, String>> _userExaminations = {};
  final Map<String, String> _userMedicalHistory = {};

  final AgentCollaborationManager _collaborationManager;

  BaseMedicalDiagnosisAgent(
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
    // 注册联合诊断请求处理器
    _collaborationManager.registerHandler(
      CollaborationRequestType.jointDiagnosis,
      _handleJointDiagnosisRequest,
    );

    // 注册数据共享请求处理器
    _collaborationManager.registerHandler(
      CollaborationRequestType.dataSharing,
      _handleDataSharingRequest,
    );
  }

  /// 处理联合诊断请求
  Future<CollaborationResult> _handleJointDiagnosisRequest(
    CollaborationRequest request,
  ) async {
    try {
      final userId = request.data['userId'] as String;
      final symptoms = request.data['symptoms'] as List<dynamic>;
      final useTCM =
          request.data['useTCM'] as bool? ?? supportTraditionalChinese;

      // 添加症状
      for (final symptom in symptoms) {
        await addSymptoms(userId, symptom.toString());
      }

      // 添加检查结果（如果有）
      if (request.data['examinations'] != null) {
        final examinations =
            request.data['examinations'] as Map<String, dynamic>;
        examinations.forEach((examType, result) async {
          await addExaminationResult(userId, examType, result.toString());
        });
      }

      // 添加病史（如果有）
      if (request.data['medicalHistory'] != null) {
        await addMedicalHistory(
          userId,
          request.data['medicalHistory'].toString(),
        );
      }

      // 获取诊断结果
      final diagnosisResult = await getDiagnosis(userId);

      // 返回诊断结果
      return request.createResponse(
        status: CollaborationResultStatus.success,
        resultData: {'diagnosis': diagnosisResult.toMap()},
      );
    } catch (e) {
      logger.e('处理联合诊断请求失败', error: e);

      return request.createResponse(
        status: CollaborationResultStatus.failure,
        resultData: {},
        message: '处理请求出错: $e',
      );
    }
  }

  /// 处理数据共享请求
  Future<CollaborationResult> _handleDataSharingRequest(
    CollaborationRequest request,
  ) async {
    try {
      // 在实际应用中，此处可以接收其他代理共享的健康数据
      return request.createResponse(
        status: CollaborationResultStatus.success,
        resultData: {'status': 'received'},
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

  @override
  String get id => _agent.id;

  @override
  String get name => _agent.name;

  @override
  bool get supportTraditionalChinese =>
      _agent.hasCapability(AIAgentCapability.healthAdvice) &&
      (_agent.modelConfig['supports_tcm'] == true);

  @override
  bool get supportWesternMedicine =>
      _agent.hasCapability(AIAgentCapability.healthAdvice) &&
      (_agent.modelConfig['supports_western'] == true);

  @override
  Future<void> addSymptoms(String userId, String symptoms) async {
    _userSymptoms.putIfAbsent(userId, () => []).add(symptoms);

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: LearningDataType.text,
        source: LearningDataSource.userInput,
        content: symptoms,
        agentId: id,
        userId: userId,
      ),
    );
  }

  @override
  Future<void> addExaminationResult(
    String userId,
    String examType,
    String result,
  ) async {
    _userExaminations.putIfAbsent(userId, () => {}).addAll({examType: result});

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: LearningDataType.text,
        source: LearningDataSource.userInput,
        content: {'examType': examType, 'result': result},
        agentId: id,
        userId: userId,
      ),
    );
  }

  @override
  Future<void> addMedicalHistory(String userId, String history) async {
    _userMedicalHistory[userId] = history;

    // 记录学习数据
    await _learningSystem.collectData(
      LearningDataItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: LearningDataType.text,
        source: LearningDataSource.userInput,
        content: history,
        agentId: id,
        userId: userId,
      ),
    );
  }

  @override
  Future<DiagnosisResult> getDiagnosis(String userId) async {
    try {
      // 收集用户数据
      final symptoms = _userSymptoms[userId] ?? [];
      final examinations = _userExaminations[userId] ?? {};
      final history = _userMedicalHistory[userId];

      // 判断使用哪种诊断方法
      final useTCM = supportTraditionalChinese;
      final useWestern = supportWesternMedicine;

      String diagnosisResult = '';
      String? recommendation;
      DiagnosisConfidenceLevel confidenceLevel =
          DiagnosisConfidenceLevel.medium;
      List<String> references = [];

      // 构建诊断查询
      final StringBuilder query = StringBuilder();
      query.appendLine('患者症状:');
      for (final symptom in symptoms) {
        query.appendLine('- $symptom');
      }

      if (examinations.isNotEmpty) {
        query.appendLine('\n检查结果:');
        examinations.forEach((key, value) {
          query.appendLine('- $key: $value');
        });
      }

      if (history != null && history.isNotEmpty) {
        query.appendLine('\n病史:');
        query.appendLine(history);
      }

      // 获取相关资料
      final ragResults = await _ragService.query(
        query.toString(),
        collection: useTCM ? 'tcm_knowledge' : 'medical_knowledge',
        limit: 5,
      );

      // 在实际应用中，此处应调用特定的医学诊断模型
      if (useTCM) {
        // 中医诊断逻辑
        diagnosisResult = await _performTCMDiagnosis(
          userId,
          symptoms,
          examinations,
          history,
          ragResults,
        );

        recommendation = await getTreatmentSuggestion(
          userId,
          DiagnosisResult(
            id: 'temp',
            userId: userId,
            symptoms: query.toString(),
            diagnosis: diagnosisResult,
            confidenceLevel: confidenceLevel,
            isTraditionalChinese: true,
          ),
        );
      } else if (useWestern) {
        // 西医诊断逻辑
        diagnosisResult = await _performWesternDiagnosis(
          userId,
          symptoms,
          examinations,
          history,
          ragResults,
        );

        recommendation = await getTreatmentSuggestion(
          userId,
          DiagnosisResult(
            id: 'temp',
            userId: userId,
            symptoms: query.toString(),
            diagnosis: diagnosisResult,
            confidenceLevel: confidenceLevel,
            isTraditionalChinese: false,
          ),
        );
      } else {
        throw Exception('不支持的诊断类型');
      }

      // 从RAG结果中提取参考资料
      for (final ragResult in ragResults) {
        if (ragResult.metadata != null &&
            ragResult.metadata!['source'] != null) {
          references.add(ragResult.metadata!['source']);
        } else {
          // 如果没有source元数据，则使用文档ID作为引用
          references.add('文档ID: ${ragResult.documentId}');
        }
      }

      // 创建诊断结果
      final result = DiagnosisResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        userId: userId,
        symptoms: query.toString(),
        diagnosis: diagnosisResult,
        recommendation: recommendation,
        references: references,
        confidenceLevel: confidenceLevel,
        isTraditionalChinese: useTCM,
      );

      // 记录学习数据
      await _learningSystem.collectData(
        LearningDataItem(
          id: result.id,
          type: LearningDataType.structured,
          source: LearningDataSource.agentGenerated,
          content: result.toMap(),
          agentId: id,
          userId: userId,
        ),
      );

      return result;
    } catch (e, stackTrace) {
      logger.e('诊断失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// 执行中医诊断
  Future<String> _performTCMDiagnosis(
    String userId,
    List<String> symptoms,
    Map<String, String> examinations,
    String? history,
    List<RAGResult> ragResults,
  ) async {
    // 模拟中医辩证诊断过程
    // 实际应用中应对接专业的中医辩证模型

    final StringBuilder diagnosis = StringBuilder();
    diagnosis.appendLine('中医辩证分析：');

    // 简单模拟中医辩证逻辑，实际应根据专业模型实现
    bool hasHeatSymptoms = symptoms.any(
      (s) =>
          s.contains('发热') ||
          s.contains('口干') ||
          s.contains('烦躁') ||
          s.contains('口苦'),
    );

    bool hasColdSymptoms = symptoms.any(
      (s) =>
          s.contains('怕冷') ||
          s.contains('手脚冰凉') ||
          s.contains('无汗') ||
          s.contains('喜热饮'),
    );

    bool hasDeficiencySymptoms = symptoms.any(
      (s) =>
          s.contains('疲劳') ||
          s.contains('乏力') ||
          s.contains('气短') ||
          s.contains('自汗'),
    );

    bool hasExcessSymptoms = symptoms.any(
      (s) =>
          s.contains('胀痛') ||
          s.contains('痰多') ||
          s.contains('便秘') ||
          s.contains('腹胀'),
    );

    // 八纲辨证
    if (hasHeatSymptoms && !hasColdSymptoms) {
      diagnosis.appendLine('热证');
    } else if (hasColdSymptoms && !hasHeatSymptoms) {
      diagnosis.appendLine('寒证');
    } else if (hasHeatSymptoms && hasColdSymptoms) {
      diagnosis.appendLine('寒热错杂');
    }

    if (hasDeficiencySymptoms && !hasExcessSymptoms) {
      diagnosis.appendLine('虚证');
    } else if (hasExcessSymptoms && !hasDeficiencySymptoms) {
      diagnosis.appendLine('实证');
    } else if (hasDeficiencySymptoms && hasExcessSymptoms) {
      diagnosis.appendLine('虚实夹杂');
    }

    // 引用RAG结果补充诊断
    if (ragResults.isNotEmpty) {
      diagnosis.appendLine('\n参考知识库分析：');
      for (int i = 0; i < Math.min(2, ragResults.length); i++) {
        diagnosis.appendLine('- ${ragResults[i].content}');
      }
    }

    return diagnosis.toString();
  }

  /// 执行西医诊断
  Future<String> _performWesternDiagnosis(
    String userId,
    List<String> symptoms,
    Map<String, String> examinations,
    String? history,
    List<RAGResult> ragResults,
  ) async {
    // 模拟西医诊断过程
    // 实际应用中应对接专业的西医诊断模型

    final StringBuilder diagnosis = StringBuilder();
    diagnosis.appendLine('西医临床分析：');

    // 分析症状
    if (symptoms.isNotEmpty) {
      diagnosis.appendLine('根据症状分析：');

      // 实际应用中应使用更复杂的医学知识模型
      List<String> possibleConditions = [];

      if (symptoms.any((s) => s.contains('头痛') || s.contains('头晕'))) {
        possibleConditions.add('可能与神经系统相关');
      }

      if (symptoms.any(
        (s) => s.contains('咳嗽') || s.contains('呼吸困难') || s.contains('胸闷'),
      )) {
        possibleConditions.add('可能与呼吸系统相关');
      }

      if (symptoms.any(
        (s) =>
            s.contains('腹痛') ||
            s.contains('恶心') ||
            s.contains('呕吐') ||
            s.contains('腹泻'),
      )) {
        possibleConditions.add('可能与消化系统相关');
      }

      for (final condition in possibleConditions) {
        diagnosis.appendLine('- $condition');
      }
    }

    // 分析检查结果
    if (examinations.isNotEmpty) {
      diagnosis.appendLine('\n检查结果分析：');
      examinations.forEach((examType, result) {
        diagnosis.appendLine('- $examType: $result');
        // 在实际应用中，应根据检查类型和结果进行专业分析
      });
    }

    // 引用RAG结果补充诊断
    if (ragResults.isNotEmpty) {
      diagnosis.appendLine('\n参考医学文献：');
      for (int i = 0; i < Math.min(2, ragResults.length); i++) {
        diagnosis.appendLine('- ${ragResults[i].content}');
      }
    }

    return diagnosis.toString();
  }

  @override
  Future<String> getTreatmentSuggestion(
    String userId,
    DiagnosisResult diagnosis,
  ) async {
    final StringBuilder suggestion = StringBuilder();

    if (diagnosis.isTraditionalChinese) {
      suggestion.appendLine('中医调理建议：');

      // 在实际应用中，这里应使用专业的中医治疗建议模型
      // 以下是模拟逻辑
      if (diagnosis.diagnosis.contains('热证')) {
        suggestion.appendLine('- 清热解毒类中药调理');
        suggestion.appendLine('- 饮食宜清淡，避免辛辣刺激');
        suggestion.appendLine('- 保持心情舒畅，避免情绪激动');
      } else if (diagnosis.diagnosis.contains('寒证')) {
        suggestion.appendLine('- 温阳散寒类中药调理');
        suggestion.appendLine('- 饮食宜温热，避免生冷');
        suggestion.appendLine('- 注意保暖，避免受凉');
      }

      if (diagnosis.diagnosis.contains('虚证')) {
        suggestion.appendLine('- 补益类中药调理');
        suggestion.appendLine('- 饮食宜营养丰富，易消化');
        suggestion.appendLine('- 适当休息，避免过度劳累');
      } else if (diagnosis.diagnosis.contains('实证')) {
        suggestion.appendLine('- 祛邪类中药调理');
        suggestion.appendLine('- 饮食宜清淡，控制总量');
        suggestion.appendLine('- 适当运动，促进代谢');
      }
    } else {
      suggestion.appendLine('西医治疗建议：');

      // 在实际应用中，这里应使用专业的西医治疗建议模型
      // 以下是模拟逻辑
      if (diagnosis.diagnosis.contains('神经系统')) {
        suggestion.appendLine('- 建议咨询神经内科医生');
        suggestion.appendLine('- 可能需要进行头部CT或MRI检查');
        suggestion.appendLine('- 注意休息，避免过度紧张');
      } else if (diagnosis.diagnosis.contains('呼吸系统')) {
        suggestion.appendLine('- 建议咨询呼吸科医生');
        suggestion.appendLine('- 可能需要进行胸部X光或CT检查');
        suggestion.appendLine('- 保持室内空气流通，避免接触过敏原');
      } else if (diagnosis.diagnosis.contains('消化系统')) {
        suggestion.appendLine('- 建议咨询消化内科医生');
        suggestion.appendLine('- 可能需要进行胃肠道内镜或B超检查');
        suggestion.appendLine('- 饮食规律，避免辛辣刺激食物');
      }
    }

    suggestion.appendLine('\n注意：以上建议仅供参考，具体治疗方案请咨询专业医生。');

    return suggestion.toString();
  }

  @override
  Future<String> getTCMAnalysis(String userId) async {
    if (!supportTraditionalChinese) {
      return '此代理不支持中医辩证分析';
    }

    final symptoms = _userSymptoms[userId] ?? [];
    if (symptoms.isEmpty) {
      return '暂无症状信息，无法进行分析';
    }

    // 在实际应用中，应使用专业的中医辩证模型
    final StringBuilder analysis = StringBuilder();
    analysis.appendLine('中医辩证分析：');

    // 简单模拟中医四诊
    analysis.appendLine('\n望诊：');
    // 实际应基于用户上传的图像或描述
    analysis.appendLine('依据症状描述进行分析，缺乏直接望诊资料');

    analysis.appendLine('\n闻诊：');
    // 实际应基于用户描述的气味等信息
    analysis.appendLine('依据症状描述进行分析，缺乏直接闻诊资料');

    analysis.appendLine('\n问诊：');
    for (final symptom in symptoms) {
      analysis.appendLine('- $symptom');
    }

    analysis.appendLine('\n切诊：');
    // 实际应基于脉象等信息
    analysis.appendLine('依据症状描述进行分析，缺乏直接切诊资料');

    analysis.appendLine('\n辨证论治：');
    // 此处应使用专业的中医辨证模型
    analysis.appendLine('建议由专业中医师进行面诊，完成详细的辨证分析');

    return analysis.toString();
  }

  @override
  Future<String> getWesternMedicalAnalysis(String userId) async {
    if (!supportWesternMedicine) {
      return '此代理不支持西医病理分析';
    }

    final symptoms = _userSymptoms[userId] ?? [];
    final examinations = _userExaminations[userId] ?? {};

    if (symptoms.isEmpty && examinations.isEmpty) {
      return '暂无症状和检查信息，无法进行分析';
    }

    // 在实际应用中，应使用专业的西医诊断模型
    final StringBuilder analysis = StringBuilder();
    analysis.appendLine('西医临床分析：');

    if (symptoms.isNotEmpty) {
      analysis.appendLine('\n症状分析：');
      for (final symptom in symptoms) {
        analysis.appendLine('- $symptom');
      }
    }

    if (examinations.isNotEmpty) {
      analysis.appendLine('\n检查结果分析：');
      examinations.forEach((examType, result) {
        analysis.appendLine('- $examType: $result');
      });
    }

    analysis.appendLine('\n鉴别诊断：');
    // 此处应使用专业的西医诊断模型
    analysis.appendLine('建议由专业医师进行面诊，完成详细的临床分析');

    return analysis.toString();
  }
}

/// 中医诊断代理
class TCMMedicalDiagnosisAgent extends BaseMedicalDiagnosisAgent {
  TCMMedicalDiagnosisAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  /// 中药方剂推荐
  Future<String> recommendHerbalFormula(
    String userId,
    DiagnosisResult diagnosis,
  ) async {
    final StringBuilder recommendation = StringBuilder();
    recommendation.appendLine('中药方剂推荐：');

    // 根据辩证结果推荐合适的中药方剂
    if (diagnosis.diagnosis.contains('热证')) {
      recommendation.appendLine('- 清热解毒类方剂：黄连解毒汤、银翘散等');
    } else if (diagnosis.diagnosis.contains('寒证')) {
      recommendation.appendLine('- 温阳散寒类方剂：桂枝汤、当归四逆汤等');
    }

    if (diagnosis.diagnosis.contains('虚证')) {
      if (diagnosis.diagnosis.contains('气虚')) {
        recommendation.appendLine('- 补气类方剂：四君子汤、补中益气汤等');
      } else if (diagnosis.diagnosis.contains('血虚')) {
        recommendation.appendLine('- 补血类方剂：四物汤、归脾汤等');
      }
    }

    recommendation.appendLine('\n注意：以上方剂推荐仅供参考，实际用药请在中医师指导下进行。');

    return recommendation.toString();
  }
}

/// 西医诊断代理
class WesternMedicalDiagnosisAgent extends BaseMedicalDiagnosisAgent {
  WesternMedicalDiagnosisAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  /// 药物治疗推荐
  Future<String> recommendMedication(
    String userId,
    DiagnosisResult diagnosis,
  ) async {
    final StringBuilder recommendation = StringBuilder();
    recommendation.appendLine('药物治疗推荐：');

    // 根据诊断结果推荐合适的药物
    if (diagnosis.diagnosis.contains('神经系统')) {
      recommendation.appendLine('- 可能需要神经系统用药，如镇痛药、抗焦虑药等');
    } else if (diagnosis.diagnosis.contains('呼吸系统')) {
      recommendation.appendLine('- 可能需要呼吸系统用药，如止咳药、化痰药、支气管扩张药等');
    } else if (diagnosis.diagnosis.contains('消化系统')) {
      recommendation.appendLine('- 可能需要消化系统用药，如胃黏膜保护剂、助消化药等');
    }

    recommendation.appendLine('\n注意：以上药物推荐仅供参考，实际用药请在医师指导下进行。');

    return recommendation.toString();
  }

  /// 检查建议
  Future<String> recommendExaminations(
    String userId,
    DiagnosisResult diagnosis,
  ) async {
    final StringBuilder recommendation = StringBuilder();
    recommendation.appendLine('建议检查项目：');

    // 根据诊断结果推荐合适的检查
    if (diagnosis.diagnosis.contains('神经系统')) {
      recommendation.appendLine('- 神经系统检查：头部CT/MRI、脑电图等');
    } else if (diagnosis.diagnosis.contains('呼吸系统')) {
      recommendation.appendLine('- 呼吸系统检查：胸部X光/CT、肺功能检查等');
    } else if (diagnosis.diagnosis.contains('消化系统')) {
      recommendation.appendLine('- 消化系统检查：胃肠镜、腹部B超、肝功能检查等');
    }

    recommendation.appendLine('\n注意：具体检查项目应由专业医师根据病情决定。');

    return recommendation.toString();
  }
}

/// 综合医学诊断代理（中西医结合）
class IntegratedMedicalDiagnosisAgent extends BaseMedicalDiagnosisAgent {
  IntegratedMedicalDiagnosisAgent(
    AIAgent agent,
    AutonomousLearningSystem learningSystem,
    RAGService ragService,
    AgentMicrokernel microkernel,
  ) : super(agent, learningSystem, ragService, microkernel);

  /// 提供中西医结合诊疗方案
  Future<String> provideIntegratedTreatmentPlan(
    String userId,
    DiagnosisResult diagnosis,
  ) async {
    final StringBuilder plan = StringBuilder();
    plan.appendLine('中西医结合诊疗方案：');

    // 西医治疗方案
    plan.appendLine('\n【西医治疗部分】');
    if (diagnosis.diagnosis.contains('神经系统')) {
      plan.appendLine('- 西医诊疗：神经内科诊疗，可能需要药物治疗和相关神经系统检查');
    } else if (diagnosis.diagnosis.contains('呼吸系统')) {
      plan.appendLine('- 西医诊疗：呼吸科诊疗，可能需要抗炎、平喘等治疗和呼吸系统检查');
    } else if (diagnosis.diagnosis.contains('消化系统')) {
      plan.appendLine('- 西医诊疗：消化内科诊疗，可能需要胃肠道调节药物和消化系统检查');
    }

    // 中医治疗方案
    plan.appendLine('\n【中医调理部分】');
    if (diagnosis.diagnosis.contains('热证')) {
      plan.appendLine('- 中医调理：清热解毒，可采用中药、针灸、推拿等方法');
    } else if (diagnosis.diagnosis.contains('寒证')) {
      plan.appendLine('- 中医调理：温阳散寒，可采用中药、艾灸、热敷等方法');
    }

    if (diagnosis.diagnosis.contains('虚证')) {
      plan.appendLine('- 中医调理：补益调理，可采用中药、针灸、膏方等方法');
    } else if (diagnosis.diagnosis.contains('实证')) {
      plan.appendLine('- 中医调理：祛邪治实，可采用中药、刮痧、拔罐等方法');
    }

    // 生活调理建议
    plan.appendLine('\n【生活调理建议】');
    plan.appendLine('- 饮食调整：根据体质和病情调整饮食结构');
    plan.appendLine('- 作息调整：保持规律作息，充足睡眠');
    plan.appendLine('- 运动建议：适量运动，增强体质');
    plan.appendLine('- 情志调节：保持心情舒畅，避免情绪波动');

    plan.appendLine('\n注意：此方案仅供参考，具体诊疗请在专业医师指导下进行。');

    return plan.toString();
  }
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

/// 数学函数封装
class Math {
  static int min(int a, int b) {
    return a < b ? a : b;
  }
}
