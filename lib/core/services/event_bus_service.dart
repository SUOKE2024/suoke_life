import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class EventBusService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final eventSubscriptions = <String, List<Function(dynamic)>>{}.obs;
  final eventHistory = <Map<String, dynamic>>[].obs;
  final eventFilters = <String, bool Function(dynamic)>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initEventBus();
  }

  Future<void> _initEventBus() async {
    try {
      await _loadEventHistory();
      _registerDefaultFilters();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize event bus', data: {'error': e.toString()});
    }
  }

  // 发布事件
  Future<void> publish(String event, dynamic data) async {
    try {
      // 应用过滤器
      final filter = eventFilters[event];
      if (filter != null && !filter(data)) {
        return;
      }

      await _recordEvent(event, data);
      
      // 通知订阅者
      final subscribers = eventSubscriptions[event];
      if (subscribers != null) {
        for (final callback in subscribers) {
          callback(data);
        }
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to publish event', data: {'event': event, 'error': e.toString()});
    }
  }

  // 订阅事件
  void subscribe(String event, Function(dynamic) callback) {
    try {
      if (!eventSubscriptions.containsKey(event)) {
        eventSubscriptions[event] = [];
      }
      eventSubscriptions[event]!.add(callback);
    } catch (e) {
      _loggingService.log('error', 'Failed to subscribe to event', data: {'event': event, 'error': e.toString()});
    }
  }

  // 取消订阅
  void unsubscribe(String event, Function(dynamic) callback) {
    try {
      eventSubscriptions[event]?.remove(callback);
    } catch (e) {
      _loggingService.log('error', 'Failed to unsubscribe from event', data: {'event': event, 'error': e.toString()});
    }
  }

  // 添加事件过滤器
  void addEventFilter(String event, bool Function(dynamic) filter) {
    try {
      eventFilters[event] = filter;
    } catch (e) {
      _loggingService.log('error', 'Failed to add event filter', data: {'event': event, 'error': e.toString()});
    }
  }

  // 移除事件过滤器
  void removeEventFilter(String event) {
    try {
      eventFilters.remove(event);
    } catch (e) {
      _loggingService.log('error', 'Failed to remove event filter', data: {'event': event, 'error': e.toString()});
    }
  }

  // 获取事件历史
  Future<List<Map<String, dynamic>>> getEventHistory({
    String? event,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = eventHistory.toList();

      if (event != null) {
        history = history.where((record) => record['event'] == event).toList();
      }

      if (startDate != null || endDate != null) {
        history = history.where((record) {
          final timestamp = DateTime.parse(record['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get event history', data: {'error': e.toString()});
      return [];
    }
  }

  void _registerDefaultFilters() {
    // 注册默认过滤器
    addEventFilter('error', (data) {
      return data != null && data is Map && data.containsKey('error');
    });

    addEventFilter('user_action', (data) {
      return data != null && data is Map && data.containsKey('action');
    });

    addEventFilter('system_event', (data) {
      return data != null && data is Map && data.containsKey('type');
    });
  }

  Future<void> _loadEventHistory() async {
    try {
      final history = await _storageService.getLocal('event_history');
      if (history != null) {
        eventHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveEventHistory() async {
    try {
      await _storageService.saveLocal('event_history', eventHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordEvent(String event, dynamic data) async {
    try {
      final record = {
        'event': event,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      };

      eventHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (eventHistory.length > 1000) {
        eventHistory.removeRange(1000, eventHistory.length);
      }
      
      await _saveEventHistory();
    } catch (e) {
      rethrow;
    }
  }
} 