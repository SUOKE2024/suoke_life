import 'dart:async';
import 'package:get/get.dart';
import '../storage/storage_manager.dart';
import '../device/device_manager.dart';
import 'models/analytics_event.dart';

class AnalyticsManager extends GetxService {
  static final instance = AnalyticsManager._();
  AnalyticsManager._();

  final _storage = Get.find<StorageManager>();
  final _deviceManager = Get.find<DeviceManager>();
  final _eventBuffer = <AnalyticsEvent>[].obs;
  final _isEnabled = true.obs;
  Timer? _flushTimer;
  
  Future<void> initialize() async {
    _isEnabled.value = await _storage.getBool('analytics_enabled', true);
    _startPeriodicFlush();
  }

  void trackEvent(String name, {Map<String, dynamic>? parameters}) {
    if (!_isEnabled.value) return;

    final event = AnalyticsEvent(
      name: name,
      parameters: parameters,
      timestamp: DateTime.now(),
      deviceInfo: {
        'deviceId': _deviceManager.deviceId,
        'osVersion': _deviceManager.osVersion,
        'appVersion': _deviceManager.packageInfo.version,
      },
    );

    _eventBuffer.add(event);
  }

  void _startPeriodicFlush() {
    _flushTimer?.cancel();
    _flushTimer = Timer.periodic(const Duration(minutes: 5), (_) {
      _flushEvents();
    });
  }

  Future<void> _flushEvents() async {
    if (_eventBuffer.isEmpty) return;
    
    // 实现数据上传逻辑
    _eventBuffer.clear();
  }

  @override
  void onClose() {
    _flushTimer?.cancel();
    _eventBuffer.clear();
    super.onClose();
  }
} 