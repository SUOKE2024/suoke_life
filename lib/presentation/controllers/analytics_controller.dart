import 'package:get/get.dart';
import 'package:suoke_life/services/analytics_service.dart';

class AnalyticsController extends GetxController {
  final AnalyticsService _analyticsService = Get.find();
  
  // 基础统计数据
  final _stats = <String, dynamic>{}.obs;
  Map<String, dynamic> get stats => _stats;
  
  // 标签使用频率
  final _tagFrequency = <String, int>{}.obs;
  Map<String, int> get tagFrequency => _tagFrequency;
  
  // 月度记录数量
  final _monthlyCount = <String, int>{}.obs;
  Map<String, int> get monthlyCount => _monthlyCount;
  
  // 时间分布
  final _hourlyDistribution = <int, int>{}.obs;
  Map<int, int> get hourlyDistribution => _hourlyDistribution;
  
  // 内容长度分布
  final _lengthDistribution = <String, int>{}.obs;
  Map<String, int> get lengthDistribution => _lengthDistribution;
  
  // 情感分析统计
  final _emotionStats = <String, double>{}.obs;
  Map<String, double> get emotionStats => _emotionStats;
  
  @override
  void onInit() {
    super.onInit();
    loadAllStats();
  }
  
  // 加载所有统计数据
  Future<void> loadAllStats() async {
    _stats.value = _analyticsService.getRecordStats();
    _tagFrequency.value = _analyticsService.getTagFrequency();
    _monthlyCount.value = _analyticsService.getMonthlyRecordCount();
    _hourlyDistribution.value = _analyticsService.getHourlyDistribution();
    _lengthDistribution.value = _analyticsService.getContentLengthDistribution();
    _emotionStats.value = await _analyticsService.getEmotionStats();
  }
  
  // 获取热门标签（前N个）
  List<MapEntry<String, int>> getTopTags([int n = 5]) {
    return tagFrequency.entries.take(n).toList();
  }
  
  // 获取最活跃的月份（前N个）
  List<MapEntry<String, int>> getMostActiveMonths([int n = 3]) {
    return monthlyCount.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    return monthlyCount.entries.take(n).toList();
  }
  
  // 获取最常记录的时间段
  List<int> getPeakHours() {
    final maxCount = hourlyDistribution.values.reduce((a, b) => a > b ? a : b);
    return hourlyDistribution.entries
        .where((e) => e.value == maxCount)
        .map((e) => e.key)
        .toList();
  }
  
  // 获取主要情感倾向
  String getDominantEmotion() {
    if (emotionStats.isEmpty) return '暂无数据';
    final maxEmotion = emotionStats.entries
        .reduce((a, b) => a.value > b.value ? a : b);
    switch (maxEmotion.key) {
      case 'positive':
        return '积极';
      case 'neutral':
        return '平和';
      case 'negative':
        return '消极';
      default:
        return '未知';
    }
  }
} 