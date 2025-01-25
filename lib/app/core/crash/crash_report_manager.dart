class CrashReportManager {
  static final instance = CrashReportManager._();
  CrashReportManager._();

  final _storage = Get.find<StorageManager>();
  final _deviceManager = Get.find<DeviceManager>();
  final _pendingReports = <CrashReport>[];
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 设置全局错误处理
    FlutterError.onError = _handleFlutterError;
    
    // 处理未捕获的异步错误
    PlatformDispatcher.instance.onError = _handlePlatformError;
    
    // 加载未发送的崩溃报告
    await _loadPendingReports();
    
    // 尝试发送待处理的报告
    _sendPendingReports();
    
    _isInitialized = true;
  }

  void _handleFlutterError(FlutterErrorDetails details) {
    _reportCrash(
      error: details.exception,
      stack: details.stack,
      type: CrashType.flutterError,
      context: details.context?.toString(),
    );
  }

  bool _handlePlatformError(Object error, StackTrace stack) {
    _reportCrash(
      error: error,
      stack: stack,
      type: CrashType.platformError,
    );
    return true;
  }

  Future<void> _reportCrash({
    required Object error,
    required StackTrace? stack,
    required CrashType type,
    String? context,
  }) async {
    final report = CrashReport(
      error: error.toString(),
      stackTrace: stack?.toString(),
      type: type,
      context: context,
      deviceInfo: _deviceManager.metadata,
      timestamp: DateTime.now(),
    );

    _pendingReports.add(report);
    await _savePendingReports();
    
    // 尝试立即发送
    _sendPendingReports();
  }

  Future<void> _loadPendingReports() async {
    final reports = await _storage.getObject<List>(
      'pending_crash_reports',
      (json) => (json['reports'] as List)
          .map((e) => CrashReport.fromJson(e))
          .toList(),
    );
    
    if (reports != null) {
      _pendingReports.addAll(reports);
    }
  }

  Future<void> _savePendingReports() async {
    await _storage.setObject('pending_crash_reports', {
      'reports': _pendingReports.map((r) => r.toJson()).toList(),
    });
  }

  Future<void> _sendPendingReports() async {
    if (_pendingReports.isEmpty) return;

    try {
      final apiClient = Get.find<ApiClient>();
      await apiClient.post(
        '/api/crash-reports',
        data: {
          'reports': _pendingReports.map((r) => r.toJson()).toList(),
        },
      );

      _pendingReports.clear();
      await _storage.remove('pending_crash_reports');
    } catch (e) {
      LoggerManager.instance.error('Failed to send crash reports', e);
    }
  }
}

class CrashReport {
  final String error;
  final String? stackTrace;
  final CrashType type;
  final String? context;
  final Map<String, dynamic> deviceInfo;
  final DateTime timestamp;

  CrashReport({
    required this.error,
    this.stackTrace,
    required this.type,
    this.context,
    required this.deviceInfo,
    required this.timestamp,
  });

  factory CrashReport.fromJson(Map<String, dynamic> json) => CrashReport(
    error: json['error'],
    stackTrace: json['stackTrace'],
    type: CrashType.values.byName(json['type']),
    context: json['context'],
    deviceInfo: Map<String, dynamic>.from(json['deviceInfo']),
    timestamp: DateTime.parse(json['timestamp']),
  );

  Map<String, dynamic> toJson() => {
    'error': error,
    'stackTrace': stackTrace,
    'type': type.name,
    'context': context,
    'deviceInfo': deviceInfo,
    'timestamp': timestamp.toIso8601String(),
  };
}

enum CrashType {
  flutterError,
  platformError,
  uncaughtException,
  anr,
} 