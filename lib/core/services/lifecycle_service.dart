import 'package:get/get.dart';
import 'package:flutter/widgets.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class LifecycleService extends GetxService with WidgetsBindingObserver {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final appState = AppLifecycleState.resumed.obs;
  final lastActiveTime = Rx<DateTime?>(null);
  final sessionDuration = const Duration().obs;
  final isInForeground = true.obs;

  @override
  void onInit() {
    super.onInit();
    WidgetsBinding.instance.addObserver(this);
    _initLifecycle();
  }

  @override
  void onClose() {
    WidgetsBinding.instance.removeObserver(this);
    super.onClose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    appState.value = state;
    _handleStateChange(state);
  }

  Future<void> _initLifecycle() async {
    try {
      lastActiveTime.value = DateTime.now();
      await _loadLifecycleData();
      await _startSession();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize lifecycle', data: {'error': e.toString()});
    }
  }

  // 开始会话
  Future<void> _startSession() async {
    try {
      final sessionData = {
        'start_time': DateTime.now().toIso8601String(),
        'device_info': await _getDeviceInfo(),
        'session_id': _generateSessionId(),
      };
      
      await _storageService.saveLocal('current_session', sessionData);
      _startSessionTimer();
    } catch (e) {
      await _loggingService.log('error', 'Failed to start session', data: {'error': e.toString()});
    }
  }

  // 结束会话
  Future<void> _endSession() async {
    try {
      final sessionData = await _storageService.getLocal('current_session');
      if (sessionData != null) {
        sessionData['end_time'] = DateTime.now().toIso8601String();
        sessionData['duration'] = sessionDuration.value.inSeconds;
        
        await _saveSessionHistory(sessionData);
        await _storageService.removeLocal('current_session');
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to end session', data: {'error': e.toString()});
    }
  }

  void _handleStateChange(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:
        _onResume();
        break;
      case AppLifecycleState.paused:
        _onPause();
        break;
      case AppLifecycleState.inactive:
        _onInactive();
        break;
      case AppLifecycleState.detached:
        _onDetached();
        break;
      default:
        break;
    }
  }

  Future<void> _onResume() async {
    try {
      isInForeground.value = true;
      lastActiveTime.value = DateTime.now();
      await _checkSessionValidity();
      await _loggingService.log('info', 'App resumed');
    } catch (e) {
      await _loggingService.log('error', 'Failed to handle resume', data: {'error': e.toString()});
    }
  }

  Future<void> _onPause() async {
    try {
      isInForeground.value = false;
      await _saveLifecycleData();
      await _loggingService.log('info', 'App paused');
    } catch (e) {
      await _loggingService.log('error', 'Failed to handle pause', data: {'error': e.toString()});
    }
  }

  Future<void> _onInactive() async {
    try {
      await _loggingService.log('info', 'App inactive');
    } catch (e) {
      await _loggingService.log('error', 'Failed to handle inactive', data: {'error': e.toString()});
    }
  }

  Future<void> _onDetached() async {
    try {
      await _endSession();
      await _loggingService.log('info', 'App detached');
    } catch (e) {
      await _loggingService.log('error', 'Failed to handle detached', data: {'error': e.toString()});
    }
  }

  Future<void> _loadLifecycleData() async {
    try {
      final data = await _storageService.getLocal('lifecycle_data');
      if (data != null) {
        lastActiveTime.value = DateTime.parse(data['last_active_time']);
        sessionDuration.value = Duration(seconds: data['session_duration'] ?? 0);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveLifecycleData() async {
    try {
      await _storageService.saveLocal('lifecycle_data', {
        'last_active_time': lastActiveTime.value?.toIso8601String(),
        'session_duration': sessionDuration.value.inSeconds,
        'app_state': appState.value.toString(),
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _checkSessionValidity() async {
    try {
      final lastActive = lastActiveTime.value;
      if (lastActive != null) {
        final now = DateTime.now();
        final difference = now.difference(lastActive);
        
        // 如果超过30分钟没有活动,创建新会话
        if (difference.inMinutes > 30) {
          await _endSession();
          await _startSession();
        }
      }
    } catch (e) {
      rethrow;
    }
  }

  void _startSessionTimer() {
    // 每秒更新会话时长
    Timer.periodic(const Duration(seconds: 1), (timer) {
      if (isInForeground.value) {
        sessionDuration.value += const Duration(seconds: 1);
      }
    });
  }

  Future<Map<String, dynamic>> _getDeviceInfo() async {
    // TODO: 实现设备信息获取
    return {};
  }

  String _generateSessionId() {
    return DateTime.now().millisecondsSinceEpoch.toString();
  }

  Future<void> _saveSessionHistory(Map<String, dynamic> sessionData) async {
    try {
      final history = await _getSessionHistory();
      history.add(sessionData);
      
      // 只保留最近100条会话记录
      if (history.length > 100) {
        history.removeRange(100, history.length);
      }
      
      await _storageService.saveLocal('session_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getSessionHistory() async {
    try {
      final data = await _storageService.getLocal('session_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 