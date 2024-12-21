import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class AnalyticsService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final analyticsEnabled = true.obs;
  final events = <Map<String, dynamic>>[].obs;
  final userProperties = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initAnalytics();
  }

  Future<void> _initAnalytics() async {
    try {
      await _loadAnalyticsConfig();
      await _loadUserProperties();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize analytics', data: {'error': e.toString()});
    }
  }

  // 记录事件
  Future<void> logEvent(
    String eventName,
    Map<String, dynamic> parameters, {
    bool? enabled,
  }) async {
    if (!(enabled ?? analyticsEnabled.value)) return;

    try {
      final event = {
        'name': eventName,
        'parameters': parameters,
        'timestamp': DateTime.now().toIso8601String(),
      };

      events.insert(0, event);
      await _saveEvent(event);
      await _processEvent(event);
    } catch (e) {
      await _loggingService.log('error', 'Failed to log event', data: {'event': eventName, 'error': e.toString()});
    }
  }

  // 设置用户属性
  Future<void> setUserProperty(String name, dynamic value) async {
    try {
      userProperties[name] = value;
      await _saveUserProperties();
    } catch (e) {
      await _loggingService.log('error', 'Failed to set user property', data: {'name': name, 'error': e.toString()});
    }
  }

  // 获取分析报告
  Future<Map<String, dynamic>> getAnalyticsReport({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final filteredEvents = _filterEvents(startDate, endDate);
      return {
        'event_count': filteredEvents.length,
        'event_types': _countEventTypes(filteredEvents),
        'user_properties': userProperties.value,
        'trends': await _analyzeTrends(filteredEvents),
        'insights': await _generateInsights(filteredEvents),
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to generate analytics report', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadAnalyticsConfig() async {
    try {
      final config = await _storageService.getLocal('analytics_config');
      if (config != null) {
        analyticsEnabled.value = config['enabled'] ?? true;
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadUserProperties() async {
    try {
      final properties = await _storageService.getLocal('user_properties');
      if (properties != null) {
        userProperties.value = Map<String, dynamic>.from(properties);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveEvent(Map<String, dynamic> event) async {
    try {
      final savedEvents = await _getEvents();
      savedEvents.insert(0, event);
      
      // 只保留最近1000条事件
      if (savedEvents.length > 1000) {
        savedEvents.removeRange(1000, savedEvents.length);
      }
      
      await _storageService.saveLocal('analytics_events', savedEvents);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveUserProperties() async {
    try {
      await _storageService.saveLocal('user_properties', userProperties.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _processEvent(Map<String, dynamic> event) async {
    try {
      // 实时处理事件
      await _updateMetrics(event);
      await _checkTriggers(event);
      await _sendToServer(event);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getEvents() async {
    try {
      final data = await _storageService.getLocal('analytics_events');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  List<Map<String, dynamic>> _filterEvents(DateTime? start, DateTime? end) {
    return events.where((event) {
      final timestamp = DateTime.parse(event['timestamp']);
      if (start != null && timestamp.isBefore(start)) return false;
      if (end != null && timestamp.isAfter(end)) return false;
      return true;
    }).toList();
  }

  Map<String, int> _countEventTypes(List<Map<String, dynamic>> events) {
    final counts = <String, int>{};
    for (final event in events) {
      final name = event['name'] as String;
      counts[name] = (counts[name] ?? 0) + 1;
    }
    return counts;
  }

  Future<Map<String, dynamic>> _analyzeTrends(
    List<Map<String, dynamic>> events,
  ) async {
    try {
      // TODO: 实现趋势分析
      return {};
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateInsights(
    List<Map<String, dynamic>> events,
  ) async {
    try {
      // TODO: 实现洞察生成
      return [];
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _updateMetrics(Map<String, dynamic> event) async {
    try {
      // TODO: 实现指标更新
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkTriggers(Map<String, dynamic> event) async {
    try {
      // TODO: 实现触发器检查
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _sendToServer(Map<String, dynamic> event) async {
    try {
      // TODO: 实现服务器上传
    } catch (e) {
      rethrow;
    }
  }
} 