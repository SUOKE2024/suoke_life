class NetworkAnalyzer {
  static final instance = NetworkAnalyzer._();
  NetworkAnalyzer._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  final _requests = <String, NetworkRequest>{};

  bool _isEnabled = true;
  Timer? _cleanupTimer;

  // 配置
  static const _config = {
    'slow_request_threshold': 3000, // 慢请求阈值（毫秒）
    'max_request_history': 100, // 最大请求历史记录数
    'cleanup_interval': 300000, // 清理间隔（毫秒）
  };

  Future<void> initialize() async {
    _isEnabled = await _storage.getBool('network_analyzer_enabled') ?? true;

    if (_isEnabled) {
      _startCleanupTimer();
    }
  }

  void trackRequest(
    String url, {
    required String method,
    Map<String, dynamic>? headers,
    dynamic body,
  }) {
    if (!_isEnabled) return;

    final request = NetworkRequest(
      url: url,
      method: method,
      headers: headers,
      body: body,
      startTime: DateTime.now(),
    );

    _requests[request.id] = request;
  }

  void trackResponse(
    String requestId, {
    required int statusCode,
    Map<String, dynamic>? headers,
    dynamic body,
    dynamic error,
  }) {
    if (!_isEnabled) return;

    final request = _requests[requestId];
    if (request == null) return;

    request.complete(
      statusCode: statusCode,
      headers: headers,
      body: body,
      error: error,
    );

    _analyzeRequest(request);
  }

  void _analyzeRequest(NetworkRequest request) {
    final duration = request.duration;
    if (duration == null) return;

    // 记录性能指标
    Get.find<PerformanceMonitorManager>().recordMetric(
      'network_request_duration',
      duration.inMilliseconds.toDouble(),
      category: 'network',
      attributes: {
        'url': request.url,
        'method': request.method,
        'status': request.statusCode,
      },
    );

    // 检查慢请求
    if (duration.inMilliseconds > _config['slow_request_threshold']!) {
      _eventBus.fire(NetworkWarningEvent(
        type: NetworkWarningType.slowRequest,
        message: 'Slow network request',
        request: request,
      ));
    }

    // 检查错误
    if (request.error != null || request.statusCode >= 400) {
      _eventBus.fire(NetworkWarningEvent(
        type: NetworkWarningType.error,
        message: 'Network request failed',
        request: request,
      ));
    }
  }

  void _startCleanupTimer() {
    _cleanupTimer = Timer.periodic(
      Duration(milliseconds: _config['cleanup_interval']!),
      (_) => _cleanup(),
    );
  }

  void _cleanup() {
    final now = DateTime.now();
    _requests.removeWhere((_, request) {
      return request.startTime.difference(now).inMinutes > 30;
    });

    while (_requests.length > _config['max_request_history']!) {
      String? oldestKey;
      DateTime? oldestTime;

      for (final entry in _requests.entries) {
        if (oldestTime == null || entry.value.startTime.isBefore(oldestTime)) {
          oldestKey = entry.key;
          oldestTime = entry.value.startTime;
        }
      }

      if (oldestKey != null) {
        _requests.remove(oldestKey);
      }
    }
  }

  List<NetworkRequest> getRequestHistory() {
    return _requests.values.toList()
      ..sort((a, b) => b.startTime.compareTo(a.startTime));
  }

  void dispose() {
    _cleanupTimer?.cancel();
    _requests.clear();
  }
}

class NetworkRequest {
  final String id;
  final String url;
  final String method;
  final Map<String, dynamic>? headers;
  final dynamic body;
  final DateTime startTime;

  DateTime? endTime;
  int? statusCode;
  Map<String, dynamic>? responseHeaders;
  dynamic responseBody;
  dynamic error;

  NetworkRequest({
    required this.url,
    required this.method,
    this.headers,
    this.body,
    required this.startTime,
  }) : id = const Uuid().v4();

  void complete({
    required int statusCode,
    Map<String, dynamic>? headers,
    dynamic body,
    dynamic error,
  }) {
    this.statusCode = statusCode;
    responseHeaders = headers;
    responseBody = body;
    this.error = error;
    endTime = DateTime.now();
  }

  Duration? get duration => endTime?.difference(startTime);

  Map<String, dynamic> toJson() => {
        'id': id,
        'url': url,
        'method': method,
        'headers': headers,
        'body': body,
        'startTime': startTime.toIso8601String(),
        'endTime': endTime?.toIso8601String(),
        'statusCode': statusCode,
        'responseHeaders': responseHeaders,
        'responseBody': responseBody,
        'error': error?.toString(),
        'duration': duration?.inMilliseconds,
      };
}

class NetworkWarningEvent extends AppEvent {
  final NetworkWarningType type;
  final String message;
  final NetworkRequest request;

  NetworkWarningEvent({
    required this.type,
    required this.message,
    required this.request,
  });
}

enum NetworkWarningType {
  slowRequest,
  error,
  timeout,
}
