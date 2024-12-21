class ErrorHandlerService extends GetxService {
  final LogManagerService _logManager;
  final EventTrackingService _eventTracking;
  final NotificationManagerService _notificationManager;
  final FallbackService _fallbackService;
  
  // 错误处理策略
  static const Map<String, ErrorStrategy> _errorStrategies = {
    'network': ErrorStrategy(
      maxRetries: 3,
      retryDelay: Duration(seconds: 1),
      exponentialBackoff: true,
      fallbackEnabled: true,
      notifyUser: true,
      severity: ErrorSeverity.high,
    ),
    'timeout': ErrorStrategy(
      maxRetries: 2,
      retryDelay: Duration(milliseconds: 500),
      exponentialBackoff: true,
      fallbackEnabled: true,
      notifyUser: true,
      severity: ErrorSeverity.medium,
    ),
    'validation': ErrorStrategy(
      maxRetries: 0,
      fallbackEnabled: false,
      notifyUser: true,
      severity: ErrorSeverity.low,
    ),
    'permission': ErrorStrategy(
      maxRetries: 0,
      fallbackEnabled: false,
      notifyUser: true,
      severity: ErrorSeverity.high,
    ),
  };
  
  // 错误计数器
  final Map<String, ErrorCounter> _errorCounters = {};
  
  ErrorHandlerService({
    required LogManagerService logManager,
    required EventTrackingService eventTracking,
    required NotificationManagerService notificationManager,
    required FallbackService fallbackService,
  })  : _logManager = logManager,
        _eventTracking = eventTracking,
        _notificationManager = notificationManager,
        _fallbackService = fallbackService {
    _startErrorMonitoring();
  }

  Future<T> handleError<T>({
    required Future<T> Function() operation,
    required String errorType,
    String? userId,
    String? assistantName,
    Map<String, dynamic>? context,
  }) async {
    final strategy = _getErrorStrategy(errorType);
    int retryCount = 0;
    Duration delay = strategy.retryDelay ?? Duration.zero;

    while (true) {
      try {
        final result = await operation();
        // 成功后重置错误计数
        _resetErrorCount(errorType, userId);
        return result;
      } catch (e) {
        // 增加错误计数
        _incrementErrorCount(errorType, userId);
        
        // 记录错误
        await _logError(
          e,
          errorType,
          userId: userId,
          assistantName: assistantName,
          context: context,
        );

        // 检查是否需要重试
        if (retryCount < (strategy.maxRetries ?? 0)) {
          retryCount++;
          
          // 指数退避
          if (strategy.exponentialBackoff) {
            delay *= 2;
          }
          
          await Future.delayed(delay);
          continue;
        }

        // 检查是否需要降级
        if (strategy.fallbackEnabled) {
          return await _handleFallback<T>(
            e,
            errorType,
            userId: userId,
            assistantName: assistantName,
          );
        }

        // 通知用户
        if (strategy.notifyUser) {
          await _notifyUser(
            e,
            errorType,
            userId: userId,
            assistantName: assistantName,
          );
        }

        rethrow;
      }
    }
  }

  Future<void> reportError(
    dynamic error,
    String errorType, {
    String? userId,
    String? assistantName,
    Map<String, dynamic>? context,
    StackTrace? stackTrace,
  }) async {
    try {
      // 记录错误
      await _logError(
        error,
        errorType,
        userId: userId,
        assistantName: assistantName,
        context: context,
        stackTrace: stackTrace,
      );

      // 增加错误计数
      _incrementErrorCount(errorType, userId);

      // 检查错误阈值
      await _checkErrorThresholds(errorType, userId);
    } catch (e) {
      debugPrint('错误报告失败: $e');
    }
  }

  Future<ErrorStats> getErrorStats(
    String errorType, {
    String? userId,
    Duration? timeWindow,
  }) async {
    final counter = _getErrorCounter(errorType, userId);
    return ErrorStats(
      total: counter.total,
      recent: counter.getRecentCount(timeWindow ?? Duration(hours: 1)),
      lastError: counter.lastError,
      errorType: errorType,
    );
  }

  ErrorStrategy _getErrorStrategy(String errorType) {
    return _errorStrategies[errorType] ?? 
      ErrorStrategy(
        maxRetries: 0,
        fallbackEnabled: false,
        notifyUser: true,
        severity: ErrorSeverity.medium,
      );
  }

  Future<void> _logError(
    dynamic error,
    String errorType, {
    String? userId,
    String? assistantName,
    Map<String, dynamic>? context,
    StackTrace? stackTrace,
  }) async {
    final strategy = _getErrorStrategy(errorType);
    
    await _logManager.log(
      error.toString(),
      userId: userId ?? 'system',
      assistantName: assistantName ?? 'system',
      level: _getSeverityLevel(strategy.severity),
      metadata: {
        'error_type': errorType,
        'context': context,
        'stack_trace': stackTrace?.toString(),
      },
    );

    await _trackErrorEvent(
      error,
      errorType,
      userId: userId,
      assistantName: assistantName,
      context: context,
    );
  }

  Future<T> _handleFallback<T>(
    dynamic error,
    String errorType, {
    String? userId,
    String? assistantName,
  }) async {
    try {
      if (assistantName != null) {
        final fallbackModel = await _fallbackService.getFallbackModel(
          assistantName,
        );
        
        // TODO: 实现具体的降级逻辑
        throw UnimplementedError();
      }
      throw error;
    } catch (e) {
      debugPrint('降级处理失败: $e');
      throw error;
    }
  }

  Future<void> _notifyUser(
    dynamic error,
    String errorType, {
    String? userId,
    String? assistantName,
  }) async {
    if (userId == null) return;

    try {
      await _notificationManager.sendNotification(AINotification(
        id: 'error_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        channel: 'error',
        title: '操作失败',
        message: _getErrorMessage(error, errorType),
        priority: NotificationPriority.high,
      ));
    } catch (e) {
      debugPrint('发送错误通知失败: $e');
    }
  }

  String _getErrorMessage(dynamic error, String errorType) {
    // TODO: 根据错误类型和内容生成用户友好的错误消息
    return '操作��行失败，请稍后重试';
  }

  void _incrementErrorCount(String errorType, String? userId) {
    final counter = _getErrorCounter(errorType, userId);
    counter.increment();
  }

  void _resetErrorCount(String errorType, String? userId) {
    final counter = _getErrorCounter(errorType, userId);
    counter.reset();
  }

  ErrorCounter _getErrorCounter(String errorType, String? userId) {
    final key = _getCounterKey(errorType, userId);
    return _errorCounters[key] ??= ErrorCounter();
  }

  String _getCounterKey(String errorType, String? userId) =>
    userId != null ? '${userId}_$errorType' : errorType;

  Future<void> _checkErrorThresholds(
    String errorType,
    String? userId,
  ) async {
    final counter = _getErrorCounter(errorType, userId);
    final strategy = _getErrorStrategy(errorType);
    
    // 检查最近错误数量
    final recentErrors = counter.getRecentCount(Duration(minutes: 5));
    if (recentErrors >= 5) {  // 5分钟内5次错误
      await _handleErrorThresholdExceeded(
        errorType,
        userId,
        'high_frequency',
      );
    }
    
    // 检查总错误数量
    if (counter.total >= 100) {  // 累计100次错误
      await _handleErrorThresholdExceeded(
        errorType,
        userId,
        'high_volume',
      );
    }
  }

  Future<void> _handleErrorThresholdExceeded(
    String errorType,
    String? userId,
    String reason,
  ) async {
    // 记录事件
    await _trackErrorEvent(
      'error_threshold_exceeded',
      errorType,
      userId: userId,
      context: {'reason': reason},
    );
    
    // 通知相关人员
    // TODO: 实现告警通知逻辑
  }

  Future<void> _trackErrorEvent(
    dynamic error,
    String errorType, {
    String? userId,
    String? assistantName,
    Map<String, dynamic>? context,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'error_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId ?? 'system',
      assistantName: assistantName ?? 'system',
      type: AIEventType.error,
      data: {
        'error': error.toString(),
        'error_type': errorType,
        'context': context,
      },
    ));
  }

  LogLevel _getSeverityLevel(ErrorSeverity severity) {
    switch (severity) {
      case ErrorSeverity.low:
        return LogLevel.warning;
      case ErrorSeverity.medium:
        return LogLevel.error;
      case ErrorSeverity.high:
        return LogLevel.critical;
      default:
        return LogLevel.error;
    }
  }

  void _startErrorMonitoring() {
    Timer.periodic(Duration(hours: 1), (_) {
      _cleanupOldErrors();
    });
  }

  void _cleanupOldErrors() {
    final now = DateTime.now();
    for (final counter in _errorCounters.values) {
      counter.cleanup(now.subtract(Duration(days: 7)));  // 保留7天的错误记录
    }
  }
} 