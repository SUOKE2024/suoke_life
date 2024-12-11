import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/message.dart';
import 'coze_service.dart';

class ConsultationAnalysis {
  final String condition;
  final double urgencyScore;
  final List<String> suggestedDepartments;
  final List<String> requiredExpertise;
  final String aiSummary;

  ConsultationAnalysis({
    required this.condition,
    required this.urgencyScore,
    required this.suggestedDepartments,
    required this.requiredExpertise,
    required this.aiSummary,
  });

  Map<String, dynamic> toJson() => {
    'condition': condition,
    'urgencyScore': urgencyScore,
    'suggestedDepartments': suggestedDepartments,
    'requiredExpertise': requiredExpertise,
    'aiSummary': aiSummary,
  };
}

class AIConsultationAssistantService {
  final CozeService _cozeService;
  final _analysisController = StreamController<ConsultationAnalysis>.broadcast();

  AIConsultationAssistantService(this._cozeService);

  Stream<ConsultationAnalysis> get analysisStream => _analysisController.stream;

  Future<ConsultationAnalysis> analyzeSymptoms(String symptoms) async {
    try {
      // 构建提示词
      final prompt = '''
分析以下症状描述,提供专业医疗建议:

$symptoms

请提供以下信息:
1. 初步诊断
2. 紧急程度(0-1)
3. 建议就诊科室
4. 所需专家专长
5. AI总结建议
''';

      // 调用AI服务
      final response = await _cozeService.sendMessage(prompt);
      
      // 解析AI响应
      final analysis = _parseAIResponse(response);
      
      // 发送分析结果到流
      _analysisController.add(analysis);
      
      return analysis;
    } catch (e) {
      debugPrint('症状分析失败: $e');
      rethrow;
    }
  }

  ConsultationAnalysis _parseAIResponse(String response) {
    // TODO: 实现更复杂的响应解析逻辑
    return ConsultationAnalysis(
      condition: '待确认',
      urgencyScore: 0.5,
      suggestedDepartments: ['内科'],
      requiredExpertise: ['全科医学'],
      aiSummary: response,
    );
  }

  Future<List<String>> matchExperts(ConsultationAnalysis analysis) async {
    try {
      // 构建专家匹配提示词
      final prompt = '''
根据以下分析结果推荐最合适的专家:

${analysis.toJson()}

请列出3-5位最合适的专家ID。
''';

      // 调用AI服务
      final response = await _cozeService.sendMessage(prompt);
      
      // 解析专家列表
      return _parseExpertList(response);
    } catch (e) {
      debugPrint('专家匹配失败: $e');
      rethrow;
    }
  }

  List<String> _parseExpertList(String response) {
    // TODO: 实现专家列表解析逻辑
    return ['expert_001', 'expert_002', 'expert_003'];
  }

  void dispose() {
    _analysisController.close();
  }
} 