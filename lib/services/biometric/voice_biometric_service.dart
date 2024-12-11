import 'dart:async';
import 'package:flutter/foundation.dart';
import '../api/ali_health_api_service.dart';

class VoiceBiometricService {
  final AliHealthApiService _healthApiService;
  
  VoiceBiometricService(this._healthApiService);

  Future<Map<String, dynamic>> analyzeVoiceBiometrics(List<int> audioData) async {
    try {
      // 语音特征提取
      final voiceFeatures = await _extractVoiceFeatures(audioData);
      
      // 情绪状态分析
      final emotionalState = await _analyzeEmotionalState(voiceFeatures);
      
      // 健康状态评估
      final healthAssessment = await _assessHealthFromVoice(voiceFeatures);
      
      return {
        'voiceFeatures': voiceFeatures,
        'emotionalState': emotionalState,
        'healthAssessment': healthAssessment,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('Voice biometric analysis failed: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _extractVoiceFeatures(List<int> audioData) async {
    return await _healthApiService.extractVoiceFeatures(audioData);
  }

  Future<Map<String, dynamic>> _analyzeEmotionalState(Map<String, dynamic> voiceFeatures) async {
    return await _healthApiService.analyzeEmotionalState(voiceFeatures);
  }

  Future<Map<String, dynamic>> _assessHealthFromVoice(Map<String, dynamic> voiceFeatures) async {
    return await _healthApiService.assessHealthFromVoice(voiceFeatures);
  }

  Future<bool> verifyVoiceIdentity(List<int> audioData, String userId) async {
    try {
      final verificationResult = await _healthApiService.verifyVoiceIdentity(audioData, userId);
      return verificationResult['isMatch'] == true;
    } catch (e) {
      debugPrint('Voice identity verification failed: $e');
      rethrow;
    }
  }

  Future<String> enrollVoicePrint(List<int> audioData, String userId) async {
    try {
      final enrollmentResult = await _healthApiService.enrollVoicePrint(audioData, userId);
      return enrollmentResult['voicePrintId'];
    } catch (e) {
      debugPrint('Voice print enrollment failed: $e');
      rethrow;
    }
  }
} 