import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class HealthService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final healthData = <String, dynamic>{}.obs;
  final healthMetrics = <String, List<Map<String, dynamic>>>{}.obs;
  final healthGoals = <String, Map<String, dynamic>>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initHealth();
  }

  Future<void> _initHealth() async {
    try {
      await Future.wait([
        _loadHealthData(),
        _loadHealthMetrics(),
        _loadHealthGoals(),
      ]);
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize health', data: {'error': e.toString()});
    }
  }

  // 记录健康数据
  Future<void> recordHealthData(String type, Map<String, dynamic> data) async {
    try {
      final record = {
        ...data,
        'timestamp': DateTime.now().toIso8601String(),
      };

      if (!healthMetrics.containsKey(type)) {
        healthMetrics[type] = [];
      }
      healthMetrics[type]!.insert(0, record);

      await _saveHealthMetrics();
      await _updateHealthStatus(type, record);
    } catch (e) {
      await _loggingService.log('error', 'Failed to record health data', data: {'type': type, 'error': e.toString()});
      rethrow;
    }
  }

  // 设置健康目标
  Future<void> setHealthGoal(String type, Map<String, dynamic> goal) async {
    try {
      healthGoals[type] = {
        ...goal,
        'created_at': DateTime.now().toIso8601String(),
      };
      await _saveHealthGoals();
    } catch (e) {
      await _loggingService.log('error', 'Failed to set health goal', data: {'type': type, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取健康报告
  Future<Map<String, dynamic>> getHealthReport({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final metrics = _filterMetrics(startDate, endDate);
      return {
        'summary': await _generateHealthSummary(metrics),
        'trends': await _analyzeHealthTrends(metrics),
        'goals': await _checkGoalProgress(metrics),
        'recommendations': await _generateRecommendations(metrics),
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to get health report', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadHealthData() async {
    try {
      final data = await _storageService.getLocal('health_data');
      if (data != null) {
        healthData.value = Map<String, dynamic>.from(data);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadHealthMetrics() async {
    try {
      final metrics = await _storageService.getLocal('health_metrics');
      if (metrics != null) {
        healthMetrics.value = Map<String, List<Map<String, dynamic>>>.from(metrics);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadHealthGoals() async {
    try {
      final goals = await _storageService.getLocal('health_goals');
      if (goals != null) {
        healthGoals.value = Map<String, Map<String, dynamic>>.from(goals);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveHealthMetrics() async {
    try {
      await _storageService.saveLocal('health_metrics', healthMetrics.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveHealthGoals() async {
    try {
      await _storageService.saveLocal('health_goals', healthGoals.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _updateHealthStatus(String type, Map<String, dynamic> record) async {
    try {
      healthData[type] = record;
      await _storageService.saveLocal('health_data', healthData.value);
    } catch (e) {
      rethrow;
    }
  }

  Map<String, List<Map<String, dynamic>>> _filterMetrics(
    DateTime? startDate,
    DateTime? endDate,
  ) {
    if (startDate == null && endDate == null) {
      return healthMetrics;
    }

    final filtered = <String, List<Map<String, dynamic>>>{};
    
    for (final entry in healthMetrics.entries) {
      filtered[entry.key] = entry.value.where((record) {
        final timestamp = DateTime.parse(record['timestamp']);
        if (startDate != null && timestamp.isBefore(startDate)) return false;
        if (endDate != null && timestamp.isAfter(endDate)) return false;
        return true;
      }).toList();
    }
    
    return filtered;
  }

  Future<Map<String, dynamic>> _generateHealthSummary(
    Map<String, List<Map<String, dynamic>>> metrics,
  ) async {
    try {
      final summary = <String, dynamic>{};
      
      for (final entry in metrics.entries) {
        if (entry.value.isEmpty) continue;
        
        summary[entry.key] = {
          'latest': entry.value.first,
          'count': entry.value.length,
          'average': _calculateAverage(entry.value),
        };
      }
      
      return summary;
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _analyzeHealthTrends(
    Map<String, List<Map<String, dynamic>>> metrics,
  ) async {
    try {
      final trends = <String, dynamic>{};
      
      for (final entry in metrics.entries) {
        if (entry.value.isEmpty) continue;
        
        trends[entry.key] = {
          'trend': _calculateTrend(entry.value),
          'changes': _calculateChanges(entry.value),
        };
      }
      
      return trends;
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _checkGoalProgress(
    Map<String, List<Map<String, dynamic>>> metrics,
  ) async {
    try {
      final progress = <String, dynamic>{};
      
      for (final goal in healthGoals.entries) {
        if (!metrics.containsKey(goal.key)) continue;
        
        progress[goal.key] = {
          'goal': goal.value,
          'current': metrics[goal.key]!.first,
          'progress': _calculateProgress(
            metrics[goal.key]!.first,
            goal.value,
          ),
        };
      }
      
      return progress;
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateRecommendations(
    Map<String, List<Map<String, dynamic>>> metrics,
  ) async {
    try {
      final recommendations = <String>[];
      
      // TODO: 实现健康建议生成
      
      return recommendations;
    } catch (e) {
      rethrow;
    }
  }

  double _calculateAverage(List<Map<String, dynamic>> records) {
    try {
      if (records.isEmpty) return 0;
      
      final values = records.map((r) => r['value'] as num).toList();
      final sum = values.reduce((a, b) => a + b);
      return sum / values.length;
    } catch (e) {
      return 0;
    }
  }

  String _calculateTrend(List<Map<String, dynamic>> records) {
    try {
      if (records.length < 2) return 'stable';
      
      final first = records.first['value'] as num;
      final last = records.last['value'] as num;
      
      if (first > last) return 'increasing';
      if (first < last) return 'decreasing';
      return 'stable';
    } catch (e) {
      return 'unknown';
    }
  }

  List<Map<String, dynamic>> _calculateChanges(List<Map<String, dynamic>> records) {
    try {
      final changes = <Map<String, dynamic>>[];
      
      for (var i = 1; i < records.length; i++) {
        final current = records[i - 1]['value'] as num;
        final previous = records[i]['value'] as num;
        final change = current - previous;
        
        changes.add({
          'from': previous,
          'to': current,
          'change': change,
          'percentage': (change / previous * 100).toStringAsFixed(2),
          'timestamp': records[i - 1]['timestamp'],
        });
      }
      
      return changes;
    } catch (e) {
      return [];
    }
  }

  double _calculateProgress(
    Map<String, dynamic> current,
    Map<String, dynamic> goal,
  ) {
    try {
      final currentValue = current['value'] as num;
      final goalValue = goal['target'] as num;
      return currentValue / goalValue;
    } catch (e) {
      return 0;
    }
  }
} 
} 