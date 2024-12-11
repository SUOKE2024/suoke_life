import 'package:flutter/foundation.dart';
import '../api/ali_health_api_service.dart';
import '../../models/health/health_data.dart';

class HealthAnalyzerService {
  final AliHealthApiService _healthApiService;

  HealthAnalyzerService(this._healthApiService);

  Future<Map<String, dynamic>> analyzeHealthData(HealthData healthData) async {
    try {
      // 基础健康指标分析
      final vitalSignsAnalysis = await _analyzeVitalSigns(healthData);
      
      // 生活方式分析
      final lifestyleAnalysis = await _analyzeLifestylePatterns(healthData);
      
      // 健康风险评估
      final riskAssessment = await _assessHealthRisks(healthData);
      
      // 整合分析结果
      return {
        'vitalSigns': vitalSignsAnalysis,
        'lifestyle': lifestyleAnalysis,
        'risks': riskAssessment,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('Health analysis failed: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _analyzeVitalSigns(HealthData data) async {
    final apiResponse = await _healthApiService.analyzeVitalSigns(data);
    return apiResponse;
  }

  Future<Map<String, dynamic>> _analyzeLifestylePatterns(HealthData data) async {
    final apiResponse = await _healthApiService.analyzeLifestylePatterns(data);
    return apiResponse;
  }

  Future<Map<String, dynamic>> _assessHealthRisks(HealthData data) async {
    final apiResponse = await _healthApiService.assessHealthRisks(data);
    return apiResponse;
  }

  Future<String> generateHealthReport(Map<String, dynamic> analysisResults) async {
    try {
      return await _healthApiService.generateHealthReport(analysisResults);
    } catch (e) {
      debugPrint('Health report generation failed: $e');
      rethrow;
    }
  }
} 