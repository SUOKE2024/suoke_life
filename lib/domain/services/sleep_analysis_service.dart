import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/domain/models/sleep_analysis_model.dart';

/// 睡眠分析服务接口
abstract class SleepAnalysisService {
  /// 分析单条睡眠记录
  Future<SleepAnalysisResult> analyzeSleepRecord(SleepRecord record);

  /// 分析用户一段时间内的睡眠趋势
  Future<Map<String, dynamic>> analyzeSleepTrend(
      String userId, DateTime startDate, DateTime endDate);

  /// 生成睡眠改善建议
  Future<List<String>> generateSleepImprovementSuggestions(
      SleepRecord record, SleepAnalysisResult analysis);

  /// 获取睡眠质量与中医体质的关联分析
  Future<String> getTCMEvaluation(
      SleepRecord record, SleepAnalysisResult analysis);

  /// 获取最近的睡眠分析
  Future<List<SleepAnalysis>> getRecentAnalyses(String userId, int count);

  /// 生成睡眠分析
  Future<SleepAnalysisResult> generateAnalysis(String recordId);
}
