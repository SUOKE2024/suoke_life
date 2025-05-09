import 'dart:math';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/domain/models/sleep_analysis_model.dart';
import 'package:suoke_life/domain/repositories/health_repository.dart';
import 'package:suoke_life/domain/services/sleep_analysis_service.dart';
import 'package:uuid/uuid.dart';

/// 睡眠分析服务实现
class SleepAnalysisServiceImpl implements SleepAnalysisService {
  final HealthRepository _healthRepository;

  /// 构造函数
  SleepAnalysisServiceImpl(this._healthRepository);

  @override
  Future<SleepAnalysisResult> analyzeSleepRecord(SleepRecord record) async {
    // 在真实场景中，这里可能会调用AI模型或复杂算法进行分析
    // 现在我们使用示例数据进行模拟
    return SleepAnalysisResult.sample(record);
  }

  @override
  Future<Map<String, dynamic>> analyzeSleepTrend(
      String userId, DateTime startDate, DateTime endDate) async {
    // 获取指定时间范围内的睡眠记录
    final sleepRecords = await _healthRepository.getRecordsByDateRange(
            userId, startDate, endDate, type: HealthDataType.sleep)
        as List<SleepRecord>;

    if (sleepRecords.isEmpty) {
      return {
        'averageScore': 0.0,
        'averageDuration': 0.0,
        'sleepTimeConsistency': 0.0,
        'wakeTimeConsistency': 0.0,
        'qualityTrend': 'insufficient_data',
        'records': <Map<String, dynamic>>[],
      };
    }

    // 分析趋势
    double totalScore = 0;
    double totalDuration = 0;
    List<DateTime> sleepTimes = [];
    List<DateTime> wakeTimes = [];
    List<Map<String, dynamic>> recordAnalysis = [];

    for (final record in sleepRecords) {
      // 为每条记录生成分析
      final analysis = await analyzeSleepRecord(record);
      totalScore += analysis.overallScore;
      totalDuration += record.durationHours;
      sleepTimes.add(record.startTime);
      wakeTimes.add(record.endTime);

      recordAnalysis.add({
        'date': record.recordTime.toIso8601String(),
        'score': analysis.overallScore,
        'duration': record.durationHours,
        'efficiency': analysis.efficiency,
        'deepSleepPercentage': analysis.deepSleepPercentage,
        'qualityLevel': analysis.qualityLevel.label,
      });
    }

    // 计算平均值
    final averageScore = totalScore / sleepRecords.length;
    final averageDuration = totalDuration / sleepRecords.length;

    // 计算一致性（这里简化处理，实际应用中可能需要更复杂的统计算法）
    final sleepTimeConsistency = _calculateTimeConsistency(sleepTimes);
    final wakeTimeConsistency = _calculateTimeConsistency(wakeTimes);

    // 确定趋势方向
    String qualityTrend = 'stable';
    if (sleepRecords.length >= 3) {
      final firstHalf = sleepRecords.sublist(0, sleepRecords.length ~/ 2);
      final secondHalf = sleepRecords.sublist(sleepRecords.length ~/ 2);

      double firstHalfAvg = 0;
      double secondHalfAvg = 0;

      for (final record in firstHalf) {
        final analysis = await analyzeSleepRecord(record);
        firstHalfAvg += analysis.overallScore;
      }

      for (final record in secondHalf) {
        final analysis = await analyzeSleepRecord(record);
        secondHalfAvg += analysis.overallScore;
      }

      firstHalfAvg /= firstHalf.length;
      secondHalfAvg /= secondHalf.length;

      final difference = secondHalfAvg - firstHalfAvg;
      if (difference > 5) {
        qualityTrend = 'improving';
      } else if (difference < -5) {
        qualityTrend = 'declining';
      }
    }

    return {
      'averageScore': averageScore,
      'averageDuration': averageDuration,
      'sleepTimeConsistency': sleepTimeConsistency,
      'wakeTimeConsistency': wakeTimeConsistency,
      'qualityTrend': qualityTrend,
      'records': recordAnalysis,
    };
  }

  /// 计算时间的一致性（0-100%）
  double _calculateTimeConsistency(List<DateTime> times) {
    if (times.length <= 1) return 100.0;

    // 计算所有时间的小时+分钟部分（忽略日期）
    List<double> hourValues = times.map((time) {
      return time.hour + (time.minute / 60.0);
    }).toList();

    // 计算平均时间
    double sum = hourValues.reduce((a, b) => a + b);
    double average = sum / hourValues.length;

    // 计算标准差
    double sumSquaredDiff = 0;
    for (final value in hourValues) {
      // 考虑24小时循环的特殊情况，例如23:30和00:30的差应该是1小时而不是23小时
      double diff = (value - average).abs();
      if (diff > 12) diff = 24 - diff;
      sumSquaredDiff += diff * diff;
    }

    double stdDev = sqrt(sumSquaredDiff / hourValues.length);

    // 将标准差转换为一致性得分（0-100%）
    // 标准差越小，一致性越高
    double consistency = (1 - (stdDev / 6)).clamp(0.0, 1.0) * 100;
    return consistency;
  }

  @override
  Future<List<String>> generateSleepImprovementSuggestions(
      SleepRecord record, SleepAnalysisResult analysis) async {
    // 这里应该根据分析结果生成个性化建议
    // 现在我们返回一些基于分析质量等级的通用建议

    List<String> suggestions = [];

    // 基础建议
    suggestions.add('保持规律的睡眠时间，每天相同时间入睡和起床');

    // 根据质量等级添加额外建议
    switch (analysis.qualityLevel) {
      case SleepQualityLevel.excellent:
        suggestions.add('您的睡眠质量很好，继续保持当前的健康作息');
        break;
      case SleepQualityLevel.good:
        suggestions.add('睡前20分钟可以进行冥想或轻度拉伸活动');
        suggestions.add('尝试睡前一小时关闭电子设备，减少蓝光对褪黑素的抑制');
        break;
      case SleepQualityLevel.average:
        suggestions.add('优化睡眠环境，保持安静、黑暗和适宜的温度');
        suggestions.add('建立睡前放松仪式，如热水澡或读书');
        suggestions.add('避免睡前摄入咖啡因和酒精');
        break;
      case SleepQualityLevel.poor:
      case SleepQualityLevel.veryPoor:
        suggestions.add('白天增加适度的户外活动和阳光暴露');
        suggestions.add('控制午睡时间，不超过30分钟');
        suggestions.add('睡前避免大量饮水，减少夜间醒来次数');
        suggestions.add('睡前可以喝一杯温热的牛奶或草药茶（如洋甘菊）');
        suggestions.add('考虑睡前按摩足部涌泉穴，帮助安神养血');
        suggestions.add('如持续存在严重睡眠问题，建议咨询医生或睡眠专家');
        break;
    }

    return suggestions;
  }

  @override
  Future<String> getTCMEvaluation(
      SleepRecord record, SleepAnalysisResult analysis) async {
    // 在实际应用中，应基于更多用户数据和体质信息提供精准的中医评估
    // 这里提供简化的示例评估

    if (analysis.qualityLevel == SleepQualityLevel.excellent ||
        analysis.qualityLevel == SleepQualityLevel.good) {
      return '阴阳调和，气血充盈。您的睡眠状态良好，体现了气血充足，阴阳平衡的状态。';
    }

    if (analysis.timeToFallAsleepMinutes > 30) {
      return '肝郁化火，心神不宁。入睡困难多与肝气郁结，心火旺盛有关，可通过疏肝解郁，清心安神来改善。';
    }

    if (analysis.interruptionCount > 2) {
      return '心肾不交，阴虚火旺。夜间频繁醒来多与心肾阴虚，虚热内扰有关，宜滋阴降火，交通心肾。';
    }

    if (record.durationHours < 6) {
      return '肝胆湿热，气机不畅。睡眠时间短，可能与肝胆湿热，导致气机郁滞有关，可通过清利湿热，疏肝理气改善。';
    }

    if (record.quality != null && record.quality! < 3) {
      return '脾胃虚弱，气血生化不足。睡眠质量差，易做梦，多与脾胃虚弱，气血生化不足有关，宜健脾益气，养血安神。';
    }

    return '气血平和，但有轻微失调。您的睡眠基本正常，但存在一些小问题，建议调整作息，注意饮食平衡，以维持气血和谐。';
  }

  @override
  Future<List<SleepAnalysis>> getRecentAnalyses(String userId, int count) async {
    // 在实际应用中，这里应该从数据库中获取最近的分析结果
    // 但现在我们生成一些示例数据
    final analyses = <SleepAnalysis>[];
    
    // 获取最近的睡眠记录
    try {
      final records = await _healthRepository.getRecentRecords(
        userId,
        count, 
        type: HealthDataType.sleep,
      ) as List<SleepRecord>;
      
      // 为每条记录生成分析
      for (final record in records) {
        final uuid = const Uuid().v4();
        final analysis = await analyzeSleepRecord(record);
        analyses.add(SleepAnalysis.fromResult(uuid, analysis));
      }
    } catch (e) {
      // 捕获可能的错误，返回空列表
      print('获取睡眠分析失败: $e');
    }
    
    // 如果没有记录或发生错误，返回一些示例数据
    if (analyses.isEmpty) {
      final now = DateTime.now();
      
      // 生成过去7天的示例数据
      for (int i = 0; i < min(count, 7); i++) {
        final date = now.subtract(Duration(days: i));
        final uuid = 'sample-${date.millisecondsSinceEpoch}';
        analyses.add(SleepAnalysis.sample(id: uuid, date: date));
      }
    }
    
    return analyses;
  }
  
  @override
  Future<SleepAnalysisResult> generateAnalysis(String recordId) async {
    try {
      // 获取睡眠记录
      final record = await _healthRepository.getRecordById(recordId);
      
      if (record == null || record.type != HealthDataType.sleep) {
        throw Exception('睡眠记录不存在或类型错误');
      }
      
      // 分析睡眠记录
      return analyzeSleepRecord(record as SleepRecord);
    } catch (e) {
      // 发生错误，返回示例数据
      print('生成睡眠分析失败: $e');
      return SleepAnalysisResult.sample(SleepRecord.sample());
    }
  }
}
