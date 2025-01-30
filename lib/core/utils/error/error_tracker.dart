class ErrorTracker {
  static final instance = ErrorTracker._();
  ErrorTracker._();

  final _logger = Get.find<LoggerManager>();
  final _storage = Get.find<StorageManager>();
  final _errorBuffer = <ErrorReport>[];
  
  bool _initialized = false;
  Timer? _uploadTimer;

  Future<void> initialize() async {
    if (_initialized) return;
    
    // 加载未上传的错误报告
    await _loadPendingReports();
    // 启动定期上传
    _startPeriodicUpload();
    
    _initialized = true;
  }

  void trackError(dynamic error, StackTrace? stackTrace, {
    String? context,
    Map<String, dynamic>? extras,
  }) {
    final report = ErrorReport(
      error: error.toString(),
      stackTrace: stackTrace?.toString(),
      context: context,
      extras: extras,
      timestamp: DateTime.now(),
    );

    _errorBuffer.add(report);
    _logger.error('Error tracked', error, stackTrace);

    if (_errorBuffer.length >= 10) {
      _uploadReports();
    }
  }

  Future<void> _loadPendingReports() async {
    final reports = await _storage.getObject<List>(
      'pending_error_reports',
      (json) => (json['reports'] as List)
          .map((e) => ErrorReport.fromJson(e))
          .toList(),
    );
    
    if (reports != null) {
      _errorBuffer.addAll(reports);
    }
  }

  void _startPeriodicUpload() {
    _uploadTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _uploadReports(),
    );
  }

  Future<void> _uploadReports() async {
    if (_errorBuffer.isEmpty) return;

    try {
      final apiClient = Get.find<ApiClient>();
      await apiClient.post(
        '/api/error-reports',
        data: {
          'reports': _errorBuffer.map((r) => r.toJson()).toList(),
        },
      );

      _errorBuffer.clear();
      await _storage.remove('pending_error_reports');
    } catch (e) {
      // 保存到本地存储，等待下次上传
      await _storage.setObject('pending_error_reports', {
        'reports': _errorBuffer.map((r) => r.toJson()).toList(),
      });
    }
  }

  void dispose() {
    _uploadTimer?.cancel();
    _errorBuffer.clear();
  }
}

class ErrorReport {
  final String error;
  final String? stackTrace;
  final String? context;
  final Map<String, dynamic>? extras;
  final DateTime timestamp;

  ErrorReport({
    required this.error,
    this.stackTrace,
    this.context,
    this.extras,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
    'error': error,
    'stackTrace': stackTrace,
    'context': context,
    'extras': extras,
    'timestamp': timestamp.toIso8601String(),
  };

  factory ErrorReport.fromJson(Map<String, dynamic> json) => ErrorReport(
    error: json['error'],
    stackTrace: json['stackTrace'],
    context: json['context'],
    extras: json['extras'],
    timestamp: DateTime.parse(json['timestamp']),
  );
} 