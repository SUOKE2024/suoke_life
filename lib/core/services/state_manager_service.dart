import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class StateManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final states = <String, dynamic>{}.obs;
  final stateHistory = <Map<String, dynamic>>[].obs;
  final stateSubscriptions = <String, List<Function(dynamic)>>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initStateManager();
  }

  Future<void> _initStateManager() async {
    try {
      await _loadStates();
      await _loadStateHistory();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize state manager', data: {'error': e.toString()});
    }
  }

  // 设置状态
  Future<void> setState(String key, dynamic value) async {
    try {
      final oldValue = states[key];
      states[key] = value;
      
      await _recordStateChange(key, oldValue, value);
      await _saveStates();
      
      // 通知订阅者
      _notifySubscribers(key, value);
    } catch (e) {
      await _loggingService.log('error', 'Failed to set state', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取状态
  T? getState<T>(String key, {T? defaultValue}) {
    try {
      return states[key] as T? ?? defaultValue;
    } catch (e) {
      _loggingService.log('error', 'Failed to get state', data: {'key': key, 'error': e.toString()});
      return defaultValue;
    }
  }

  // 订阅状态变化
  void subscribeToState(String key, Function(dynamic) callback) {
    try {
      if (!stateSubscriptions.containsKey(key)) {
        stateSubscriptions[key] = [];
      }
      stateSubscriptions[key]!.add(callback);
    } catch (e) {
      _loggingService.log('error', 'Failed to subscribe to state', data: {'key': key, 'error': e.toString()});
    }
  }

  // 取消订阅
  void unsubscribeFromState(String key, Function(dynamic) callback) {
    try {
      stateSubscriptions[key]?.remove(callback);
    } catch (e) {
      _loggingService.log('error', 'Failed to unsubscribe from state', data: {'key': key, 'error': e.toString()});
    }
  }

  // 重置状态
  Future<void> resetState([String? key]) async {
    try {
      if (key != null) {
        states.remove(key);
      } else {
        states.clear();
      }
      await _saveStates();
    } catch (e) {
      await _loggingService.log('error', 'Failed to reset state', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取状态历史
  Future<List<Map<String, dynamic>>> getStateHistory({
    String? key,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = stateHistory.toList();

      if (key != null) {
        history = history.where((record) => record['key'] == key).toList();
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
      await _loggingService.log('error', 'Failed to get state history', data: {'error': e.toString()});
      return [];
    }
  }

  void _notifySubscribers(String key, dynamic value) {
    try {
      final subscribers = stateSubscriptions[key];
      if (subscribers != null) {
        for (final callback in subscribers) {
          callback(value);
        }
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to notify subscribers', data: {'key': key, 'error': e.toString()});
    }
  }

  Future<void> _loadStates() async {
    try {
      final saved = await _storageService.getLocal('app_states');
      if (saved != null) {
        states.value = Map<String, dynamic>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStates() async {
    try {
      await _storageService.saveLocal('app_states', states.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadStateHistory() async {
    try {
      final history = await _storageService.getLocal('state_history');
      if (history != null) {
        stateHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStateHistory() async {
    try {
      await _storageService.saveLocal('state_history', stateHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordStateChange(
    String key,
    dynamic oldValue,
    dynamic newValue,
  ) async {
    try {
      final record = {
        'key': key,
        'old_value': oldValue,
        'new_value': newValue,
        'timestamp': DateTime.now().toIso8601String(),
      };

      stateHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (stateHistory.length > 1000) {
        stateHistory.removeRange(1000, stateHistory.length);
      }
      
      await _saveStateHistory();
    } catch (e) {
      rethrow;
    }
  }
} 