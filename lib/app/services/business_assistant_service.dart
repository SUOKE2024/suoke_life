import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'ai_service.dart';

class BusinessAssistantService extends GetxService {
  final StorageService _storageService = Get.find();
  final AiService _aiService = Get.find();

  // 商业分析
  Future<Map<String, dynamic>> analyzeMarket(String industry) async {
    try {
      return await _aiService.queryKnowledge(
        'analyze_market',
        parameters: {'industry': industry},
      );
    } catch (e) {
      rethrow;
    }
  }

  // 商业决策支持
  Future<Map<String, dynamic>> getBusinessDecision(Map<String, dynamic> data) async {
    try {
      return await _aiService.queryKnowledge(
        'business_decision',
        parameters: data,
      );
    } catch (e) {
      rethrow;
    }
  }

  // 商业报告生成
  Future<Map<String, dynamic>> generateBusinessReport(Map<String, dynamic> data) async {
    try {
      return await _aiService.queryKnowledge(
        'generate_business_report',
        parameters: data,
      );
    } catch (e) {
      rethrow;
    }
  }

  // 商业风险评估
  Future<Map<String, dynamic>> assessBusinessRisk(Map<String, dynamic> data) async {
    try {
      return await _aiService.queryKnowledge(
        'assess_business_risk',
        parameters: data,
      );
    } catch (e) {
      rethrow;
    }
  }
} 