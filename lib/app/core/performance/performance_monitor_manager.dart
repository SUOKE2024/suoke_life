class PerformanceMonitorManager {
  static final instance = PerformanceMonitorManager._();
  PerformanceMonitorManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  final _metrics = <String, PerformanceMetric>{};
  
  bool _isEnabled = true;
  Timer? _reportTimer;

  // 性能监控配置
  static const _config = {
    'memory_warning_threshold': 80, // 内存警告阈值（百分比）
    'frame_drop_threshold': 16.0,   // 帧率下降警告阈值（ms）
    'network_timeout_threshold': 5000, // 网络超时警告阈值（ms）
  };

  Future<void> initialize() async {
    _isEnabled = await _storage.getBool('performance_monitoring_enabled') ?? true;
    
    if (_isEnabled) {
      _startMonitoring();
    }
  }

  void _startMonitoring() {
    // 启动定期报告
    _reportTimer = Timer.periodic(
      const Duration(minutes: 1),
      (_) => _reportMetrics(),
    );

    // 监听内存警告
    WidgetsBinding.instance.addObserver(_MemoryPressureObserver());
    
    // 监听帧率
    WidgetsBinding.instance.addTimingsCallback(_onFrameTimings);
  }

  void recordMetric(String name, double value, {
    String? category,
    Map<String, dynamic>? attributes,
  }) {
    if (!_isEnabled) return;

    final metric = _metrics.putIfAbsent(
      name,
      () => PerformanceMetric(name: name, category: category),
    );

    metric.addSample(value, attributes);
  }

  void startTrace(String name) {
    if (!_isEnabled) return;
    
    final trace = PerformanceTrace(name: name);
    _activeTraces[name] = trace;
  }

  void endTrace(String name) {
    if (!_isEnabled) return;
    
    final trace = _activeTraces.remove(name);
    if (trace != null) {
      final duration = trace.end();
      recordMetric('trace_$name', duration.inMicroseconds.toDouble(), 
        category: 'trace',
        attributes: {'name': name},
      );
    }
  }

  void _onFrameTimings(List<FrameTiming> timings) {
    for (final timing in timings) {
      final buildTime = timing.buildDuration.inMicroseconds.toDouble() / 1000.0;
      final rasterTime = timing.rasterDuration.inMicroseconds.toDouble() / 1000.0;
      
      recordMetric('frame_build_time', buildTime, category: 'frames');
      recordMetric('frame_raster_time', rasterTime, category: 'frames');

      if (buildTime > _config['frame_drop_threshold']!) {
        _eventBus.fire(PerformanceWarningEvent(
          type: PerformanceWarningType.frameDropped,
          message: 'Frame build time exceeded threshold',
          value: buildTime,
        ));
      }
    }
  }

  Future<void> _reportMetrics() async {
    if (_metrics.isEmpty) return;

    try {
      final report = PerformanceReport(
        metrics: Map.from(_metrics),
        timestamp: DateTime.now(),
        deviceInfo: Get.find<DeviceManager>().metadata,
      );

      final apiClient = Get.find<ApiClient>();
      await apiClient.post(
        '/api/performance/metrics',
        data: report.toJson(),
      );

      // 清理旧数据
      _metrics.clear();
    } catch (e) {
      LoggerManager.instance.error('Performance metrics report failed', e);
    }
  }

  void dispose() {
    _reportTimer?.cancel();
    _activeTraces.clear();
    _metrics.clear();
  }

  final _activeTraces = <String, PerformanceTrace>{};
}

class PerformanceMetric {
  final String name;
  final String? category;
  final List<MetricSample> samples = [];

  PerformanceMetric({
    required this.name,
    this.category,
  });

  void addSample(double value, [Map<String, dynamic>? attributes]) {
    samples.add(MetricSample(
      value: value,
      timestamp: DateTime.now(),
      attributes: attributes,
    ));
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'category': category,
    'samples': samples.map((s) => s.toJson()).toList(),
  };
}

class MetricSample {
  final double value;
  final DateTime timestamp;
  final Map<String, dynamic>? attributes;

  MetricSample({
    required this.value,
    required this.timestamp,
    this.attributes,
  });

  Map<String, dynamic> toJson() => {
    'value': value,
    'timestamp': timestamp.toIso8601String(),
    'attributes': attributes,
  };
}

class PerformanceTrace {
  final String name;
  final DateTime startTime;
  DateTime? endTime;

  PerformanceTrace({
    required this.name,
  }) : startTime = DateTime.now();

  Duration end() {
    endTime = DateTime.now();
    return endTime!.difference(startTime);
  }
}

class _MemoryPressureObserver extends WidgetsBindingObserver {
  @override
  void didHaveMemoryPressure() {
    Get.find<EventBus>().fire(PerformanceWarningEvent(
      type: PerformanceWarningType.memoryPressure,
      message: 'System under memory pressure',
    ));
  }
}

class PerformanceWarningEvent extends AppEvent {
  final PerformanceWarningType type;
  final String message;
  final double? value;

  PerformanceWarningEvent({
    required this.type,
    required this.message,
    this.value,
  });
}

enum PerformanceWarningType {
  frameDropped,
  memoryPressure,
  networkTimeout,
  highCpuUsage,
} 