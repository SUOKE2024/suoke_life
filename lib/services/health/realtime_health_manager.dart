import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../models/health/health_data.dart';
import '../api/ali_health_api_service.dart';
import 'health_analyzer_service.dart';

class RealtimeHealthManager {
  final AliHealthApiService _healthApiService;
  final HealthAnalyzerService _healthAnalyzer;
  
  final _healthDataController = StreamController<HealthData>.broadcast();
  final _analysisResultController = StreamController<Map<String, dynamic>>.broadcast();
  
  Timer? _updateTimer;
  bool _isMonitoring = false;
  
  Stream<HealthData> get healthDataStream => _healthDataController.stream;
  Stream<Map<String, dynamic>> get analysisResultStream => _analysisResultController.stream;
  
  RealtimeHealthManager(this._healthApiService, this._healthAnalyzer);

  Future<void> startMonitoring({Duration updateInterval = const Duration(seconds: 30)}) async {
    if (_isMonitoring) return;
    
    _isMonitoring = true;
    await _updateHealthData();
    
    _updateTimer = Timer.periodic(updateInterval, (_) async {
      await _updateHealthData();
    });
  }

  Future<void> stopMonitoring() async {
    _updateTimer?.cancel();
    _isMonitoring = false;
  }

  Future<void> _updateHealthData() async {
    try {
      // 获取最新的健康数据
      final healthData = await _fetchLatestHealthData();
      _healthDataController.add(healthData);
      
      // 分析健康数据
      final analysisResult = await _healthAnalyzer.analyzeHealthData(healthData);
      _analysisResultController.add(analysisResult);
      
      // 检查是否需要发出健康警告
      await _checkHealthAlerts(analysisResult);
      
    } catch (e) {
      debugPrint('Health data update failed: $e');
    }
  }

  Future<HealthData> _fetchLatestHealthData() async {
    try {
      final vitalSigns = await _healthApiService.getLatestVitalSigns();
      final lifestyle = await _healthApiService.getLatestLifestyleData();
      final metrics = await _healthApiService.getLatestHealthMetrics();
      
      return HealthData(
        timestamp: DateTime.now(),
        vitalSigns: vitalSigns,
        lifestyle: lifestyle,
        metrics: metrics,
      );
    } catch (e) {
      debugPrint('Failed to fetch latest health data: $e');
      rethrow;
    }
  }

  Future<void> _checkHealthAlerts(Map<String, dynamic> analysisResult) async {
    final risks = analysisResult['risks'] as Map<String, dynamic>?;
    if (risks == null) return;
    
    for (final risk in risks.entries) {
      if (risk.value['level'] == 'high' || risk.value['level'] == 'danger') {
        await _sendHealthAlert(risk.key, risk.value);
      }
    }
  }

  Future<void> _sendHealthAlert(String riskType, Map<String, dynamic> riskData) async {
    try {
      await _healthApiService.sendHealthAlert({
        'type': riskType,
        'level': riskData['level'],
        'description': riskData['description'],
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      debugPrint('Failed to send health alert: $e');
    }
  }

  Future<void> updateVoiceData(List<int> voiceData) async {
    try {
      final voiceAnalysis = await _healthApiService.analyzeVoiceData(voiceData);
      final currentHealthData = await _fetchLatestHealthData();
      
      // 更新健康数据中的语音分析结果
      final updatedHealthData = HealthData(
        timestamp: DateTime.now(),
        vitalSigns: currentHealthData.vitalSigns,
        lifestyle: currentHealthData.lifestyle,
        metrics: {
          ...currentHealthData.metrics,
          'voiceAnalysis': voiceAnalysis,
        },
      );
      
      _healthDataController.add(updatedHealthData);
      
      // 重新分析更新后的健康数据
      final analysisResult = await _healthAnalyzer.analyzeHealthData(updatedHealthData);
      _analysisResultController.add(analysisResult);
      
    } catch (e) {
      debugPrint('Voice data update failed: $e');
    }
  }

  void dispose() {
    _updateTimer?.cancel();
    _healthDataController.close();
    _analysisResultController.close();
  }
} 