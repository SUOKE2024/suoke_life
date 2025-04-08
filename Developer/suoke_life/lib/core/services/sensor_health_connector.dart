import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/services/context_aware_sensing_service.dart';
import 'package:suoke_life/core/services/holistic_sensing_engine.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/repositories/health_data_repository.dart';

/// 健康建议类型
enum HealthAdviceType {
  activity, // 活动相关
  environment, // 环境相关
  time, // 时间相关
  tcm, // 中医相关
  general, // 一般性建议
}

/// 健康建议数据类
class HealthAdvice {
  final String content;
  final HealthAdviceType type;
  final double relevanceScore; // 相关性得分，0-1之间
  final Map<String, dynamic>? metadata;

  const HealthAdvice({
    required this.content,
    required this.type,
    this.relevanceScore = 1.0,
    this.metadata,
  });
}

/// 传感器健康连接器
///
/// 连接传感器数据和健康服务，提供基于传感器数据的健康建议
class SensorHealthConnector {
  final ContextAwareSensingService? contextService;
  final HolisticSensingEngine? holisticEngine;
  final HealthDataRepository healthDataRepository;

  /// 构造函数
  SensorHealthConnector({
    this.contextService,
    this.holisticEngine,
    required this.healthDataRepository,
  });

  /// 获取基于环境数据的健康建议
  Future<List<String>> getEnvironmentalHealthRecommendations() async {
    try {
      final environmentalData =
          await healthDataRepository.getEnvironmentalHealthData();

      // 分析环境数据并生成建议
      final recommendations = <String>[];

      // 温度建议
      if (environmentalData.containsKey('temperature')) {
        final temperature = environmentalData['temperature'] as double;
        if (temperature > 30) {
          recommendations.add('当前温度较高，请注意防暑降温，多补充水分。');
        } else if (temperature < 10) {
          recommendations.add('当前温度较低，请注意保暖，预防感冒。');
        }
      }

      // 湿度建议
      if (environmentalData.containsKey('humidity')) {
        final humidity = environmentalData['humidity'] as double;
        if (humidity > 80) {
          recommendations.add('当前湿度较高，请注意防潮，保持室内通风。');
        } else if (humidity < 30) {
          recommendations.add('当前湿度较低，请注意保湿，多喝水。');
        }
      }

      // 空气质量建议
      if (environmentalData.containsKey('air_quality')) {
        final airQuality =
            environmentalData['air_quality'] as Map<String, dynamic>;
        final pm25 = airQuality['pm25'] as double?;

        if (pm25 != null) {
          if (pm25 > 150) {
            recommendations.add('当前PM2.5浓度较高，建议减少户外活动，外出佩戴口罩。');
          } else if (pm25 > 75) {
            recommendations.add('当前空气质量一般，敏感人群应减少户外活动。');
          }
        }
      }

      // 如果没有具体建议，添加一个通用建议
      if (recommendations.isEmpty) {
        recommendations.add('当前环境适宜，可以正常进行户外活动。');
      }

      return recommendations;
    } catch (e) {
      print('获取环境健康建议错误: $e');
      return ['无法获取环境健康建议，请稍后再试。'];
    }
  }

  /// 获取基于用户健康数据的健康建议
  Future<List<String>> getUserHealthRecommendations(String userId) async {
    try {
      final healthData = await healthDataRepository.getUserHealthData(userId);

      // 分析健康数据并生成建议
      final recommendations = <String>[];

      // 睡眠建议
      if (healthData.containsKey('sleep')) {
        final sleepData = healthData['sleep'] as Map<String, dynamic>;
        final sleepDuration = sleepData['duration'] as double?;

        if (sleepDuration != null) {
          if (sleepDuration < 6) {
            recommendations.add('您的睡眠时间不足，建议保证7-8小时的睡眠时间。');
          } else if (sleepDuration > 9) {
            recommendations.add('您的睡眠时间较长，过长的睡眠可能影响健康，建议控制在7-8小时。');
          }
        }
      }

      // 活动建议
      if (healthData.containsKey('activity')) {
        final activityData = healthData['activity'] as Map<String, dynamic>;
        final steps = activityData['steps'] as int?;

        if (steps != null) {
          if (steps < 5000) {
            recommendations.add('您的活动量较少，建议每天步行至少8000步。');
          } else if (steps > 12000) {
            recommendations.add('您的活动量充足，继续保持！');
          }
        }
      }

      // 心率建议
      if (healthData.containsKey('heart_rate')) {
        final heartRateData = healthData['heart_rate'] as Map<String, dynamic>;
        final restingHeartRate = heartRateData['resting'] as int?;

        if (restingHeartRate != null) {
          if (restingHeartRate > 80) {
            recommendations.add('您的静息心率偏高，建议增加有氧运动，保持良好的作息习惯。');
          } else if (restingHeartRate < 50) {
            recommendations.add('您的静息心率偏低，如无不适感，可能是长期锻炼的结果。');
          }
        }
      }

      // 如果没有具体建议，添加一个通用建议
      if (recommendations.isEmpty) {
        recommendations.add('您的健康状况良好，请继续保持健康的生活方式。');
      }

      return recommendations;
    } catch (e) {
      print('获取用户健康建议错误: $e');
      return ['无法获取健康建议，请稍后再试。'];
    }
  }

  /// 获取综合健康建议
  Future<List<String>> getComprehensiveHealthRecommendations(
      String userId) async {
    try {
      final environmentalRecommendations =
          await getEnvironmentalHealthRecommendations();
      final userRecommendations = await getUserHealthRecommendations(userId);

      // 合并建议并去重
      final allRecommendations = [
        ...environmentalRecommendations,
        ...userRecommendations
      ];
      return allRecommendations.toSet().toList();
    } catch (e) {
      print('获取综合健康建议错误: $e');
      return ['无法获取综合健康建议，请稍后再试。'];
    }
  }
}
