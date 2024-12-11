import 'package:flutter/foundation.dart';
import 'ai_consultation_assistant_service.dart';
import 'coze_service.dart';

enum ConsultationType {
  generalConsultation,    // 一般会诊
  emergencyConsultation,  // 急诊会诊
  followUpConsultation,   // 复诊会诊
  specialistConsultation, // 专家会诊
}

class ConsultationRequest {
  final String patientId;
  final ConsultationType type;
  final String symptoms;
  final DateTime scheduledTime;
  final DateTime requestTime;

  ConsultationRequest({
    required this.patientId,
    required this.type,
    required this.symptoms,
    required this.scheduledTime,
  }) : requestTime = DateTime.now();

  Map<String, dynamic> toJson() => {
    'patientId': patientId,
    'type': type.toString(),
    'symptoms': symptoms,
    'scheduledTime': scheduledTime.toIso8601String(),
    'requestTime': requestTime.toIso8601String(),
  };
}

class ConsultationResult {
  final String consultationId;
  final ConsultationAnalysis analysis;
  final List<String> matchedExperts;
  final DateTime scheduledTime;
  final String zoomLink;

  ConsultationResult({
    required this.consultationId,
    required this.analysis,
    required this.matchedExperts,
    required this.scheduledTime,
    required this.zoomLink,
  });

  Map<String, dynamic> toJson() => {
    'consultationId': consultationId,
    'analysis': analysis.toJson(),
    'matchedExperts': matchedExperts,
    'scheduledTime': scheduledTime.toIso8601String(),
    'zoomLink': zoomLink,
  };
}

class ConsultationService extends GetxController {
  final AIConsultationAssistantService _aiAssistant;
  final List<ConsultationResult> _consultations = [];

  ConsultationService({
    CozeService? cozeService,
  }) : _aiAssistant = AIConsultationAssistantService(
         cozeService ?? CozeService(botId: 'your_bot_id', token: 'your_token'),
       );

  List<ConsultationResult> get consultations => List.unmodifiable(_consultations);

  Stream<ConsultationAnalysis> get analysisStream => _aiAssistant.analysisStream;

  Future<ConsultationResult> submitRequest(ConsultationRequest request) async {
    try {
      // 1. AI分析症状
      final analysis = await _aiAssistant.analyzeSymptoms(request.symptoms);

      // 2. 根据分析结果匹配专家
      final experts = await _aiAssistant.matchExperts(analysis);

      // 3. 创建会诊结果
      final result = ConsultationResult(
        consultationId: DateTime.now().millisecondsSinceEpoch.toString(),
        analysis: analysis,
        matchedExperts: experts,
        scheduledTime: request.scheduledTime,
        zoomLink: 'https://zoom.us/j/${DateTime.now().millisecondsSinceEpoch}',
      );

      // 4. 保存会诊记录
      _consultations.add(result);
      
      // 5. 通知监听器
      update();

      return result;
    } catch (e) {
      debugPrint('提交会诊请求失败: $e');
      rethrow;
    }
  }

  Future<List<ConsultationResult>> getConsultationHistory(String patientId) async {
    // TODO: 实现从后端获取历史记录
    return _consultations.where((c) => true).toList();
  }

  void dispose() {
    _aiAssistant.dispose();
    super.dispose();
  }
} 