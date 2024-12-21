import 'package:get/get.dart';
import 'package:flutter/gestures.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class GestureService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final gestureCallbacks = <String, Function(dynamic)>{}.obs;
  final gestureConfigs = <String, Map<String, dynamic>>{}.obs;
  final gestureHistory = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initGestureService();
  }

  Future<void> _initGestureService() async {
    try {
      await _loadGestureConfigs();
      await _loadGestureHistory();
      _registerDefaultGestures();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize gesture service', data: {'error': e.toString()});
    }
  }

  // 注册手势回调
  void registerGestureCallback(String gesture, Function(dynamic) callback) {
    try {
      gestureCallbacks[gesture] = callback;
    } catch (e) {
      _loggingService.log('error', 'Failed to register gesture callback', data: {'gesture': gesture, 'error': e.toString()});
    }
  }

  // 移除手势回调
  void removeGestureCallback(String gesture) {
    try {
      gestureCallbacks.remove(gesture);
    } catch (e) {
      _loggingService.log('error', 'Failed to remove gesture callback', data: {'gesture': gesture, 'error': e.toString()});
    }
  }

  // 处理手势
  Future<void> handleGesture(String gesture, dynamic details) async {
    try {
      final callback = gestureCallbacks[gesture];
      if (callback != null) {
        callback(details);
        await _recordGesture(gesture, details);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to handle gesture', data: {'gesture': gesture, 'error': e.toString()});
    }
  }

  // 更新手势配置
  Future<void> updateGestureConfig(String gesture, Map<String, dynamic> config) async {
    try {
      gestureConfigs[gesture] = config;
      await _saveGestureConfigs();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update gesture config', data: {'gesture': gesture, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取手势配置
  Map<String, dynamic>? getGestureConfig(String gesture) {
    try {
      return gestureConfigs[gesture];
    } catch (e) {
      _loggingService.log('error', 'Failed to get gesture config', data: {'gesture': gesture, 'error': e.toString()});
      return null;
    }
  }

  // 获取手势历史
  Future<List<Map<String, dynamic>>> getGestureHistory({
    String? gesture,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = gestureHistory.toList();

      if (gesture != null) {
        history = history.where((record) => record['gesture'] == gesture).toList();
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
      await _loggingService.log('error', 'Failed to get gesture history', data: {'error': e.toString()});
      return [];
    }
  }

  void _registerDefaultGestures() {
    // 注册默认手势
    registerGestureCallback('tap', _handleTap);
    registerGestureCallback('double_tap', _handleDoubleTap);
    registerGestureCallback('long_press', _handleLongPress);
    registerGestureCallback('pan', _handlePan);
    registerGestureCallback('scale', _handleScale);
  }

  void _handleTap(TapDownDetails details) {
    // 处理点击
  }

  void _handleDoubleTap(TapDownDetails details) {
    // 处理双击
  }

  void _handleLongPress(LongPressStartDetails details) {
    // 处理长按
  }

  void _handlePan(PanUpdateDetails details) {
    // 处理拖动
  }

  void _handleScale(ScaleUpdateDetails details) {
    // 处理缩放
  }

  Future<void> _loadGestureConfigs() async {
    try {
      final configs = await _storageService.getLocal('gesture_configs');
      if (configs != null) {
        gestureConfigs.value = Map<String, Map<String, dynamic>>.from(configs);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveGestureConfigs() async {
    try {
      await _storageService.saveLocal('gesture_configs', gestureConfigs.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadGestureHistory() async {
    try {
      final history = await _storageService.getLocal('gesture_history');
      if (history != null) {
        gestureHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveGestureHistory() async {
    try {
      await _storageService.saveLocal('gesture_history', gestureHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordGesture(String gesture, dynamic details) async {
    try {
      final record = {
        'gesture': gesture,
        'details': _serializeGestureDetails(details),
        'timestamp': DateTime.now().toIso8601String(),
      };

      gestureHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (gestureHistory.length > 1000) {
        gestureHistory.removeRange(1000, gestureHistory.length);
      }
      
      await _saveGestureHistory();
    } catch (e) {
      rethrow;
    }
  }

  Map<String, dynamic> _serializeGestureDetails(dynamic details) {
    try {
      if (details is TapDownDetails) {
        return {
          'type': 'tap',
          'globalPosition': {
            'dx': details.globalPosition.dx,
            'dy': details.globalPosition.dy,
          },
        };
      } else if (details is LongPressStartDetails) {
        return {
          'type': 'long_press',
          'globalPosition': {
            'dx': details.globalPosition.dx,
            'dy': details.globalPosition.dy,
          },
        };
      } else if (details is PanUpdateDetails) {
        return {
          'type': 'pan',
          'delta': {
            'dx': details.delta.dx,
            'dy': details.delta.dy,
          },
          'globalPosition': {
            'dx': details.globalPosition.dx,
            'dy': details.globalPosition.dy,
          },
        };
      } else if (details is ScaleUpdateDetails) {
        return {
          'type': 'scale',
          'scale': details.scale,
          'rotation': details.rotation,
          'focalPoint': {
            'dx': details.focalPoint.dx,
            'dy': details.focalPoint.dy,
          },
        };
      }
      return {};
    } catch (e) {
      return {};
    }
  }
} 