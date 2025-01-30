import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class StatisticsService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final statistics = <String, dynamic>{}.obs;
  final dailyStats = <String, Map<String, dynamic>>{}.obs;
  final isCollecting = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initStatistics();
  }

  Future<void> _initStatistics() async {
    try {
      await _loadStatistics();
      await _startCollection();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize statistics', data: {'error': e.toString()});
    }
  }

  // 记录统计数据
  Future<void> recordStatistic(String key, dynamic value) async {
    try {
      statistics[key] = value;
      await _updateDailyStats(key, value);
      await _saveStatistics();
    } catch (e) {
      await _loggingService.log('error', 'Failed to record statistic', data: {'key': key, 'error': e.toString()});
    }
  }

  // 增加计数
  Future<void> incrementCounter(String key, [int increment = 1]) async {
    try {
      final currentValue = statistics[key] as int? ?? 0;
      await recordStatistic(key, currentValue + increment);
    } catch (e) {
      await _loggingService.log('error', 'Failed to increment counter', data: {'key': key, 'error': e.toString()});
    }
  }

  // 获取统计报告
  Future<Map<String, dynamic>> getStatisticsReport({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final filteredStats = _filterDailyStats(startDate, endDate);
      return {
        'summary': _generateSummary(filteredStats),
        'trends': await _analyzeTrends(filteredStats),
        'comparisons': await _generateComparisons(filteredStats),
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to generate statistics report', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadStatistics() async {
    try {
      final stats = await _storageService.getLocal('statistics');
      if (stats != null) {
        statistics.value = Map<String, dynamic>.from(stats);
      }

      final daily = await _storageService.getLocal('daily_statistics');
      if (daily != null) {
        dailyStats.value = Map<String, Map<String, dynamic>>.from(daily);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStatistics() async {
    try {
      await _storageService.saveLocal('statistics', statistics.value);
      await _storageService.saveLocal('daily_statistics', dailyStats.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _startCollection() async {
    if (isCollecting.value) return;

    try {
      isCollecting.value = true;
      await _collectSystemStats();
      await _collectAppStats();
      await _collectUserStats();
    } catch (e) {
      isCollecting.value = false;
      rethrow;
    }
  }

  Future<void> _updateDailyStats(String key, dynamic value) async {
    try {
      final today = DateTime.now().toIso8601String().split('T')[0];
      final dayStats = dailyStats[today] ?? {};
      
      dayStats[key] = value;
      dailyStats[today] = dayStats;
      
      // 只保留最近30天的数据
      _cleanupOldStats();
    } catch (e) {
      rethrow;
    }
  }

  void _cleanupOldStats() {
    final dates = dailyStats.keys.toList()..sort();
    if (dates.length > 30) {
      final toRemove = dates.sublist(0, dates.length - 30);
      for (final date in toRemove) {
        dailyStats.remove(date);
      }
    }
  }

  Map<String, Map<String, dynamic>> _filterDailyStats(
    DateTime? startDate,
    DateTime? endDate,
  ) {
    return Map.fromEntries(
      dailyStats.entries.where((entry) {
        final date = DateTime.parse(entry.key);
        if (startDate != null && date.isBefore(startDate)) return false;
        if (endDate != null && date.isAfter(endDate)) return false;
        return true;
      }),
    );
  }

  Map<String, dynamic> _generateSummary(
    Map<String, Map<String, dynamic>> stats,
  ) {
    final summary = <String, dynamic>{};
    
    // 计算总计和平均值
    for (final dayStats in stats.values) {
      for (final entry in dayStats.entries) {
        if (entry.value is num) {
          summary[entry.key] = (summary[entry.key] ?? 0) + entry.value;
          summary['avg_${entry.key}'] = summary[entry.key] / stats.length;
        }
      }
    }
    
    return summary;
  }

  Future<Map<String, dynamic>> _analyzeTrends(
    Map<String, Map<String, dynamic>> stats,
  ) async {
    try {
      // 实现趋势分析
      final trends = <String, dynamic>{};
      for (final entry in stats.entries) {
        for (final key in entry.value.keys) {
          trends[key] = (trends[key] ?? 0) + entry.value[key];
        }
      }
      return trends;
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _generateComparisons(
    Map<String, Map<String, dynamic>> stats,
  ) async {
    try {
      // 实现数据对比
      final comparisons = <String, dynamic>{};
      final keys = stats.values.first.keys;
      for (final key in keys) {
        final values = stats.values.map((dayStats) => dayStats[key] as num).toList();
        comparisons[key] = {
          'max': values.reduce((a, b) => a > b ? a : b),
          'min': values.reduce((a, b) => a < b ? a : b),
          'average': values.reduce((a, b) => a + b) / values.length,
        };
      }
      return comparisons;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _collectSystemStats() async {
    try {
      // 实现系统统计收集
      statistics['system'] = {
        'cpu_usage': 0.5, // 示例值
        'memory_usage': 0.7, // 示例值
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _collectAppStats() async {
    try {
      // 实现应用统计收集
      statistics['app'] = {
        'active_users': 100, // 示例值
        'crash_count': 2, // 示例值
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _collectUserStats() async {
    try {
      // 实现用户统计收集
      statistics['user'] = {
        'login_count': 50, // 示例值
        'purchase_count': 5, // 示例值
      };
    } catch (e) {
      rethrow;
    }
  }
} 