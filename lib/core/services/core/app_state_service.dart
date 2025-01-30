import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class AppStateService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final appState = <String, dynamic>{}.obs;
  final stateHistory = <Map<String, dynamic>>[].obs;
  final isRestoring = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initAppState();
  }

  Future<void> _initAppState() async {
    try {
      await _loadAppState();
      await _loadStateHistory();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize app state', data: {'error': e.toString()});
    }
  }

  // 更新状态
  Future<void> updateState(String key, dynamic value) async {
    try {
      final oldValue = appState[key];
      appState[key] = value;
      
      await _saveAppState();
      await _saveStateChange(key, oldValue, value);
    } catch (e) {
      await _loggingService.log('error', 'Failed to update state', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 批量更新状态
  Future<void> updateStates(Map<String, dynamic> states) async {
    try {
      final oldStates = Map<String, dynamic>.from(appState);
      appState.addAll(states);
      
      await _saveAppState();
      await _saveStateChanges(oldStates, states);
    } catch (e) {
      await _loggingService.log('error', 'Failed to update states', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 恢复状态
  Future<void> restoreState(DateTime timestamp) async {
    if (isRestoring.value) return;

    try {
      isRestoring.value = true;
      
      final state = await _findStateAtTime(timestamp);
      if (state != null) {
        appState.value = state;
        await _saveAppState();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to restore state', data: {'timestamp': timestamp.toIso8601String(), 'error': e.toString()});
      rethrow;
    } finally {
      isRestoring.value = false;
    }
  }

  // 清除状态历史
  Future<void> clearStateHistory() async {
    try {
      stateHistory.clear();
      await _storageService.removeLocal('state_history');
      await _loggingService.log('info', 'State history cleared');
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear state history', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadAppState() async {
    try {
      final state = await _storageService.getLocal('app_state');
      if (state != null) {
        appState.value = Map<String, dynamic>.from(state);
      }
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

  Future<void> _saveAppState() async {
    try {
      await _storageService.saveLocal('app_state', appState.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStateChange(
    String key,
    dynamic oldValue,
    dynamic newValue,
  ) async {
    try {
      final change = {
        'key': key,
        'old_value': oldValue,
        'new_value': newValue,
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      await _addToStateHistory(change);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStateChanges(
    Map<String, dynamic> oldStates,
    Map<String, dynamic> newStates,
  ) async {
    try {
      final changes = <Map<String, dynamic>>[];
      
      for (final key in newStates.keys) {
        if (oldStates[key] != newStates[key]) {
          changes.add({
            'key': key,
            'old_value': oldStates[key],
            'new_value': newStates[key],
            'timestamp': DateTime.now().toIso8601String(),
          });
        }
      }
      
      for (final change in changes) {
        await _addToStateHistory(change);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _addToStateHistory(Map<String, dynamic> change) async {
    try {
      stateHistory.insert(0, change);
      
      // 只保留最近100条记录
      if (stateHistory.length > 100) {
        stateHistory.removeRange(100, stateHistory.length);
      }
      
      await _storageService.saveLocal('state_history', stateHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> _findStateAtTime(DateTime timestamp) async {
    try {
      // 查找指定时间点之前的最近状态
      final changes = stateHistory.where(
        (change) => DateTime.parse(change['timestamp']).isBefore(timestamp),
      ).toList();
      
      if (changes.isEmpty) return null;
      
      // 重建状态
      final state = <String, dynamic>{};
      for (final change in changes.reversed) {
        state[change['key']] = change['new_value'];
      }
      
      return state;
    } catch (e) {
      rethrow;
    }
  }
} 