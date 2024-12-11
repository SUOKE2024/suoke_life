class AnalyticsManager {
  static final instance = AnalyticsManager._();
  AnalyticsManager._();

  final _storage = Get.find<StorageManager>();
  final _deviceManager = Get.find<DeviceManager>();
  final _eventBuffer = <AnalyticsEvent>[];
  
  Timer? _flushTimer;
  bool _isEnabled = true;

  Future<void> initialize() async {
    _isEnabled = await _storage.getBool('analytics_enabled') ?? true;
    
    // 启动定期上传
    _startPeriodicFlush();
    
    // 注册路由观察者
    Get.addObserver(_RouteAnalyticsObserver());
  }

  void trackEvent(String name, {
    Map<String, dynamic>? parameters,
    bool immediate = false,
  }) {
    if (!_isEnabled) return;

    final event = AnalyticsEvent(
      name: name,
      parameters: parameters,
      timestamp: DateTime.now(),
      deviceInfo: _getDeviceInfo(),
    );

    _eventBuffer.add(event);

    if (immediate || _eventBuffer.length >= 10) {
      _flushEvents();
    }
  }

  void trackScreen(String screenName) {
    trackEvent('screen_view', parameters: {'screen_name': screenName});
  }

  void trackUserAction(String action, {
    required String category,
    String? label,
    int? value,
  }) {
    trackEvent('user_action', parameters: {
      'action': action,
      'category': category,
      if (label != null) 'label': label,
      if (value != null) 'value': value,
    });
  }

  void trackError(String error, {StackTrace? stackTrace}) {
    trackEvent('error', parameters: {
      'error': error,
      if (stackTrace != null) 'stack_trace': stackTrace.toString(),
    }, immediate: true);
  }

  Map<String, dynamic> _getDeviceInfo() {
    return {
      'device_id': _deviceManager.deviceId,
      'platform': Platform.operatingSystem,
      'os_version': _deviceManager.osVersion,
      'app_version': _deviceManager.packageInfo.version,
    };
  }

  void _startPeriodicFlush() {
    _flushTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _flushEvents(),
    );
  }

  Future<void> _flushEvents() async {
    if (_eventBuffer.isEmpty) return;

    try {
      final events = List<AnalyticsEvent>.from(_eventBuffer);
      _eventBuffer.clear();

      final apiClient = Get.find<ApiClient>();
      await apiClient.post(
        '/api/analytics/events',
        data: {
          'events': events.map((e) => e.toJson()).toList(),
        },
      );
    } catch (e) {
      LoggerManager.instance.error('Analytics flush failed', e);
      // 失败时将事件放回缓冲区
      _eventBuffer.insertAll(0, _eventBuffer);
    }
  }

  Future<void> setEnabled(bool enabled) async {
    _isEnabled = enabled;
    await _storage.setBool('analytics_enabled', enabled);
  }

  void dispose() {
    _flushTimer?.cancel();
    _eventBuffer.clear();
  }
}

class AnalyticsEvent {
  final String name;
  final Map<String, dynamic>? parameters;
  final DateTime timestamp;
  final Map<String, dynamic> deviceInfo;

  AnalyticsEvent({
    required this.name,
    this.parameters,
    required this.timestamp,
    required this.deviceInfo,
  });

  Map<String, dynamic> toJson() => {
    'name': name,
    'parameters': parameters,
    'timestamp': timestamp.toIso8601String(),
    'device_info': deviceInfo,
  };
}

class _RouteAnalyticsObserver extends GetObserver {
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    if (route.settings.name != null) {
      AnalyticsManager.instance.trackScreen(route.settings.name!);
    }
  }
} 