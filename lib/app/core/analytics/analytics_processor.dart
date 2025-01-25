import 'package:injectable/injectable.dart';
import '../logger/logger.dart';
import '../storage/local_storage.dart';
import 'analytics_service.dart';

@singleton
class AnalyticsProcessor {
  final AnalyticsService _analytics;
  final LocalStorage _storage;
  final AppLogger _logger;

  AnalyticsProcessor(this._analytics, this._storage, this._logger);

  Future<void> processUserBehavior(Map<String, dynamic> behaviorData) async {
    try {
      // 数据匿名化
      final anonymizedData = _anonymizeData(behaviorData);
      
      // 记录行为数据
      await _analytics.trackEvent('user_behavior', anonymizedData);
      
      // 本地存储处理后的数据
      await _storage.setObject(
        'behavior_${DateTime.now().toIso8601String()}',
        anonymizedData,
      );
    } catch (e, stack) {
      _logger.error('Error processing user behavior', e, stack);
    }
  }

  Map<String, dynamic> _anonymizeData(Map<String, dynamic> data) {
    // 实现数据匿名化逻辑
    return data..remove('personalInfo');
  }

  Future<Map<String, dynamic>> aggregateData(
    DateTime start,
    DateTime end,
  ) async {
    try {
      final events = await _analytics.getEvents(start, end);
      return _processEvents(events);
    } catch (e, stack) {
      _logger.error('Error aggregating data', e, stack);
      rethrow;
    }
  }

  Map<String, dynamic> _processEvents(List<Map<String, dynamic>> events) {
    // 实现数据聚合逻辑
    return {
      'totalEvents': events.length,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
} 