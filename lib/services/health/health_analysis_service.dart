import 'package:health/health.dart';
import 'health_service.dart';

class HealthAnalysisService {
  final HealthService _healthService;

  HealthAnalysisService(this._healthService);

  Future<Map<String, dynamic>> analyzeHealthData(DateTime date) async {
    final startTime = DateTime(date.year, date.month, date.day);
    final endTime = startTime.add(const Duration(days: 1));

    try {
      // 获取健康数据
      final healthData = await _healthService.getHealthData(startTime, endTime);
      final sleepDuration = await _healthService.getSleepDuration(date);

      // 分析结果
      final analysis = <String, dynamic>{
        'date': date.toIso8601String(),
        'metrics': <String, dynamic>{},
        'warnings': <String>[],
        'suggestions': <String>[],
      };

      // 分析步数
      final steps = healthData[HealthDataType.STEPS] ?? 0;
      analysis['metrics']['steps'] = {
        'value': steps,
        'status': _analyzeSteps(steps),
      };

      // 分析心率
      final heartRate = healthData[HealthDataType.HEART_RATE];
      if (heartRate != null) {
        analysis['metrics']['heartRate'] = {
          'value': heartRate,
          'status': _analyzeHeartRate(heartRate),
        };
      }

      // 分析血压
      final systolic = healthData[HealthDataType.BLOOD_PRESSURE_SYSTOLIC];
      final diastolic = healthData[HealthDataType.BLOOD_PRESSURE_DIASTOLIC];
      if (systolic != null && diastolic != null) {
        analysis['metrics']['bloodPressure'] = {
          'systolic': systolic,
          'diastolic': diastolic,
          'status': _analyzeBloodPressure(systolic, diastolic),
        };
      }

      // 分析血氧
      final spo2 = healthData[HealthDataType.BLOOD_OXYGEN];
      if (spo2 != null) {
        analysis['metrics']['bloodOxygen'] = {
          'value': spo2,
          'status': _analyzeBloodOxygen(spo2),
        };
      }

      // 分析睡眠
      analysis['metrics']['sleep'] = {
        'duration': sleepDuration.inMinutes,
        'status': _analyzeSleep(sleepDuration),
      };

      // 生成建议
      analysis['suggestions'] = _generateSuggestions(analysis['metrics']);

      return analysis;
    } catch (e) {
      print('Error analyzing health data: $e');
      throw Exception('健康数据分析失败');
    }
  }

  String _analyzeSteps(double steps) {
    if (steps >= 10000) return 'excellent';
    if (steps >= 7500) return 'good';
    if (steps >= 5000) return 'fair';
    return 'poor';
  }

  String _analyzeHeartRate(double bpm) {
    if (bpm >= 60 && bpm <= 100) return 'normal';
    if (bpm < 60) return 'low';
    return 'high';
  }

  String _analyzeBloodPressure(double systolic, double diastolic) {
    if (systolic < 120 && diastolic < 80) return 'normal';
    if (systolic < 130 && diastolic < 85) return 'elevated';
    return 'high';
  }

  String _analyzeBloodOxygen(double spo2) {
    if (spo2 >= 95) return 'normal';
    if (spo2 >= 90) return 'concerning';
    return 'critical';
  }

  String _analyzeSleep(Duration duration) {
    final hours = duration.inHours;
    if (hours >= 7 && hours <= 9) return 'optimal';
    if (hours >= 6) return 'suboptimal';
    return 'insufficient';
  }

  List<String> _generateSuggestions(Map<String, dynamic> metrics) {
    final suggestions = <String>[];

    // 步数建议
    if (metrics['steps']?['status'] == 'poor') {
      suggestions.add('建议增加日常活动量,每天步行至少30分钟');
    }

    // 心率建议
    if (metrics['heartRate']?['status'] == 'high') {
      suggestions.add('心率偏高,建议放松休息,必要时咨询医生');
    }

    // 血压建议
    if (metrics['bloodPressure']?['status'] == 'high') {
      suggestions.add('血压偏高,建议限制盐分摄入,规律运动');
    }

    // 血氧建议
    if (metrics['bloodOxygen']?['status'] == 'concerning') {
      suggestions.add('血氧饱和度偏低,建议进行深呼吸练习');
    }

    // 睡眠建议
    if (metrics['sleep']?['status'] == 'insufficient') {
      suggestions.add('睡眠不足,建议保持规律作息,确保充足睡眠');
    }

    return suggestions;
  }
} 