import 'package:flutter/foundation.dart';
import '../api/health_check_service.dart';
import '../api/ali_health_api_service.dart';
import '../storage/data_storage_service.dart';
import '../health/health_analyzer_service.dart';
import '../biometric/voice_biometric_service.dart';
import '../../models/health/health_data.dart';

class CoreAlgorithmService {
  final HealthCheckService _healthCheckService;
  final AliHealthApiService _aliHealthApi;
  final DataStorageService _storageService;
  final HealthAnalyzerService _healthAnalyzer;
  final VoiceBiometricService _voiceBiometric;
  final StreamController<Map<String, dynamic>> _analysisResultController = 
      StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get analysisResultStream => _analysisResultController.stream;

  CoreAlgorithmService(
    this._healthCheckService,
    this._aliHealthApi,
    this._storageService,
    this._healthAnalyzer,
    this._voiceBiometric,
  );

  // 生命体征分析
  Future<Map<String, dynamic>> analyzeVitalSigns(CameraImage frame) async {
    try {
      // 将CameraImage转换为临时视频文件
      final videoFile = await _createTempVideoFile(frame);
      
      // 调用阿里云API进行生命体征检测
      final vitalSigns = await _aliHealthApi.checkLifeSigns(videoFile);
      
      // 保存检测结果
      await _storageService.saveHealthData({
        'type': 'vital_signs',
        'data': vitalSigns,
      });

      // 发送分析结果
      _notifyAnalysisResult({
        'type': 'vital_signs',
        'data': vitalSigns,
      });

      return vitalSigns;
    } catch (e) {
      print('生命体征分析失败: $e');
      return {};
    }
  }

  // 情绪分析
  Future<Map<String, dynamic>> analyzeEmotion({
    Map<String, dynamic>? voiceData,
    Map<String, dynamic>? faceData,
    File? videoFile,
  }) async {
    try {
      Map<String, dynamic> emotionResult = {};
      
      // 如果有视频文件，进行抑郁检测
      if (videoFile != null) {
        final depressionResult = await _aliHealthApi.checkDepression(videoFile);
        emotionResult['depression'] = depressionResult;
      }

      // 融合声音和面部表情的情绪分析
      final fusedEmotion = await _fusionEmotionAnalysis(voiceData, faceData);
      emotionResult['emotion'] = fusedEmotion;

      // 保存分析结果
      await _storageService.saveHealthData({
        'type': 'emotion',
        'data': emotionResult,
      });

      // 发送分析结果
      _notifyAnalysisResult({
        'type': 'emotion',
        'data': emotionResult,
      });

      return emotionResult;
    } catch (e) {
      print('情绪分析失败: $e');
      return {};
    }
  }

  // 健康风险评估
  Future<Map<String, dynamic>> assessHealthRisk(Map<String, dynamic> healthData) async {
    try {
      // 综合健康数据进行风险评估
      final riskAssessment = await _healthRiskAnalysis(healthData);
      
      // 如果有面部图像，进行胆固醇检测
      if (healthData['face_image'] != null) {
        final cholesterolResult = await _aliHealthApi.checkCholesterol(
          healthData['face_image'],
        );
        riskAssessment['cholesterol'] = cholesterolResult;
      }

      // 如果有视频数据，进行血压检测
      if (healthData['video_file'] != null) {
        final bloodPressureResult = await _aliHealthApi.checkBloodPressure(
          healthData['video_file'],
        );
        riskAssessment['blood_pressure'] = bloodPressureResult;
      }

      // 保存评估结果
      await _storageService.saveHealthData({
        'type': 'risk_assessment',
        'data': riskAssessment,
      });

      // 发送分析结果
      _notifyAnalysisResult({
        'type': 'risk_assessment',
        'data': riskAssessment,
      });

      return riskAssessment;
    } catch (e) {
      print('健康风险评估失败: $e');
      return {};
    }
  }

  // 生活方式分析
  Future<Map<String, dynamic>> analyzeLifestyle(List<Map<String, dynamic>> healthHistory) async {
    try {
      // 分析历史健康数据，生成生活方式建议
      final lifestyleAnalysis = await _lifestyleAnalysis(healthHistory);
      
      // 如果有失眠相关数据，进行失眠评估
      final insomniaData = healthHistory.where((data) => 
        data['type'] == 'sleep' || data['type'] == 'insomnia'
      ).toList();
      
      if (insomniaData.isNotEmpty) {
        final insomniaResult = await _aliHealthApi.assessInsomnia({
          'sleep_data': insomniaData,
        });
        lifestyleAnalysis['insomnia_assessment'] = insomniaResult;
      }

      // 保存分析结果
      await _storageService.saveHealthData({
        'type': 'lifestyle',
        'data': lifestyleAnalysis,
      });

      // 发送分析结果
      _notifyAnalysisResult({
        'type': 'lifestyle',
        'data': lifestyleAnalysis,
      });

      return lifestyleAnalysis;
    } catch (e) {
      print('生活方式分析失败: $e');
      return {};
    }
  }

  // 综合健康报告生成
  Future<Map<String, dynamic>> generateHealthReport(String userId) async {
    try {
      // 获取最近的健康数据
      final recentHealthData = await _storageService.getHealthDataHistory(
        startDate: DateTime.now().subtract(const Duration(days: 7)),
      );

      // 生成综合报告
      final report = {
        'user_id': userId,
        'timestamp': DateTime.now().toIso8601String(),
        'vital_signs': await _getLatestVitalSigns(recentHealthData),
        'emotion_state': await _getLatestEmotionState(recentHealthData),
        'health_risks': await _getHealthRisks(recentHealthData),
        'lifestyle_suggestions': await _getLifestyleSuggestions(recentHealthData),
      };

      // 保存报告
      await _storageService.saveHealthData({
        'type': 'health_report',
        'data': report,
      });

      return report;
    } catch (e) {
      print('健康报告生成失败: $e');
      return {};
    }
  }

  // 工具方法：创建临时视频文件
  Future<File> _createTempVideoFile(CameraImage frame) async {
    // TODO: 实现CameraImage到��频文件的转换
    throw UnimplementedError();
  }

  // 工具方法：获取最新生命体征
  Future<Map<String, dynamic>> _getLatestVitalSigns(List<Map<String, dynamic>> healthData) async {
    final vitalSignsData = healthData.where((data) => data['type'] == 'vital_signs').toList();
    return vitalSignsData.isNotEmpty ? vitalSignsData.first['data'] : {};
  }

  // 工具方法：获取最新情绪状态
  Future<Map<String, dynamic>> _getLatestEmotionState(List<Map<String, dynamic>> healthData) async {
    final emotionData = healthData.where((data) => data['type'] == 'emotion').toList();
    return emotionData.isNotEmpty ? emotionData.first['data'] : {};
  }

  // 工具方法：获取健康风险
  Future<List<Map<String, dynamic>>> _getHealthRisks(List<Map<String, dynamic>> healthData) async {
    final riskData = healthData.where((data) => data['type'] == 'risk_assessment').toList();
    return riskData.isNotEmpty ? riskData.first['data']['risk_factors'] : [];
  }

  // 工具方法：获取生活方式建议
  Future<List<String>> _getLifestyleSuggestions(List<Map<String, dynamic>> healthData) async {
    final lifestyleData = healthData.where((data) => data['type'] == 'lifestyle').toList();
    return lifestyleData.isNotEmpty ? 
      lifestyleData.first['data']['improvement_suggestions'] : [];
  }

  // 数���分析结果通知
  void _notifyAnalysisResult(Map<String, dynamic> result) {
    _analysisResultController.add(result);
  }

  void dispose() {
    _analysisResultController.close();
  }

  Future<Map<String, dynamic>> performComprehensiveAnalysis({
    required HealthData healthData,
    List<int>? voiceData,
  }) async {
    try {
      // 健康数据分析
      final healthAnalysis = await _healthAnalyzer.analyzeHealthData(healthData);
      
      // 如果有语音数据，进行语音生物特征分析
      Map<String, dynamic>? voiceAnalysis;
      if (voiceData != null) {
        voiceAnalysis = await _voiceBiometric.analyzeVoiceBiometrics(voiceData);
      }
      
      // AI辅助诊断
      final aiDiagnosis = await _performAIDiagnosis(
        healthAnalysis: healthAnalysis,
        voiceAnalysis: voiceAnalysis,
      );
      
      // 生成健康报告
      final healthReport = await _healthAnalyzer.generateHealthReport({
        'healthAnalysis': healthAnalysis,
        'voiceAnalysis': voiceAnalysis,
        'aiDiagnosis': aiDiagnosis,
      });
      
      return {
        'timestamp': DateTime.now().toIso8601String(),
        'healthAnalysis': healthAnalysis,
        'voiceAnalysis': voiceAnalysis,
        'aiDiagnosis': aiDiagnosis,
        'healthReport': healthReport,
      };
    } catch (e) {
      debugPrint('Comprehensive analysis failed: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _performAIDiagnosis({
    required Map<String, dynamic> healthAnalysis,
    Map<String, dynamic>? voiceAnalysis,
  }) async {
    try {
      // 整合所有分析数据
      final analysisData = {
        'healthMetrics': healthAnalysis['vitalSigns'],
        'lifestyleFactors': healthAnalysis['lifestyle'],
        'healthRisks': healthAnalysis['risks'],
        'voiceMetrics': voiceAnalysis?['voiceFeatures'],
        'emotionalState': voiceAnalysis?['emotionalState'],
      };
      
      // 调用AI诊断API
      final diagnosisResult = await _aliHealthApi.performAIDiagnosis(analysisData);
      
      // 生成健康建议
      final healthAdvice = await _generateHealthAdvice(diagnosisResult);
      
      return {
        'diagnosis': diagnosisResult,
        'advice': healthAdvice,
        'confidence': diagnosisResult['confidenceScore'],
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('AI diagnosis failed: $e');
      rethrow;
    }
  }

  Future<List<String>> _generateHealthAdvice(Map<String, dynamic> diagnosis) async {
    try {
      return await _aliHealthApi.generateHealthAdvice(diagnosis);
    } catch (e) {
      debugPrint('Health advice generation failed: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> analyzeTrends(String userId, Duration period) async {
    try {
      final historicalData = await _aliHealthApi.getHistoricalData(userId, period);
      return await _aliHealthApi.analyzeTrends(historicalData);
    } catch (e) {
      debugPrint('Trend analysis failed: $e');
      rethrow;
    }
  }
} 