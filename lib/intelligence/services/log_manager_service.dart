class LogManagerService extends GetxService {
  final DataStorageService _storageService;
  final EventTrackingService _eventTracking;
  final SubscriptionService _subscriptionService;
  
  // 日志缓存
  final Queue<AILogEntry> _logBuffer = Queue();
  final int _maxBufferSize = 1000;
  
  // 日志级别配置
  static const Map<SubscriptionPlan, Set<LogLevel>> _logLevels = {
    SubscriptionPlan.basic: {
      LogLevel.error,
      LogLevel.critical,
    },
    SubscriptionPlan.pro: {
      LogLevel.error,
      LogLevel.critical,
      LogLevel.warning,
      LogLevel.info,
    },
    SubscriptionPlan.premium: {
      LogLevel.error,
      LogLevel.critical,
      LogLevel.warning,
      LogLevel.info,
      LogLevel.debug,
      LogLevel.trace,
    },
  };
  
  LogManagerService({
    required DataStorageService storageService,
    required EventTrackingService eventTracking,
    required SubscriptionService subscriptionService,
  })  : _storageService = storageService,
        _eventTracking = eventTracking,
        _subscriptionService = subscriptionService {
    _startPeriodicFlush();
  }

  Future<void> log(
    String message, {
    required String userId,
    required String assistantName,
    required LogLevel level,
    String? sessionId,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 检查日志级别
      if (!_shouldLog(level)) return;

      final entry = AILogEntry(
        id: 'log_${DateTime.now().millisecondsSinceEpoch}',
        userId: userId,
        assistantName: assistantName,
        message: message,
        level: level,
        timestamp: DateTime.now(),
        sessionId: sessionId,
        metadata: metadata,
      );

      // 添加到缓冲区
      _addToBuffer(entry);

      // 对于高级别日志，立即处理
      if (_isHighPriorityLog(level)) {
        await _processHighPriorityLog(entry);
      }
    } catch (e) {
      debugPrint('日志记录失败: $e');
    }
  }

  Future<List<AILogEntry>> getLogs({
    required String userId,
    String? assistantName,
    DateTime? startTime,
    DateTime? endTime,
    LogLevel? minLevel,
    int limit = 100,
  }) async {
    try {
      return await _storageService.getLogs(
        userId: userId,
        assistantName: assistantName,
        startTime: startTime,
        endTime: endTime,
        minLevel: minLevel,
        limit: limit,
      );
    } catch (e) {
      throw AIException(
        '获��日志失败',
        code: 'GET_LOGS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> generateLogReport(
    String userId,
    String assistantName, {
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    try {
      final logs = await getLogs(
        userId: userId,
        assistantName: assistantName,
        startTime: startTime,
        endTime: endTime,
        minLevel: LogLevel.warning,
      );

      return _analyzeLogEntries(logs);
    } catch (e) {
      throw AIException(
        '生成日志报告失败',
        code: 'GENERATE_LOG_REPORT_ERROR',
        details: e,
      );
    }
  }

  void _addToBuffer(AILogEntry entry) {
    _logBuffer.addLast(entry);
    if (_logBuffer.length > _maxBufferSize) {
      _logBuffer.removeFirst();
    }
  }

  bool _shouldLog(LogLevel level) {
    final plan = _subscriptionService.currentPlan;
    final allowedLevels = _logLevels[plan] ?? {LogLevel.error, LogLevel.critical};
    return allowedLevels.contains(level);
  }

  bool _isHighPriorityLog(LogLevel level) {
    return level == LogLevel.error || level == LogLevel.critical;
  }

  Future<void> _processHighPriorityLog(AILogEntry entry) async {
    try {
      // 立即保存
      await _storageService.saveLog(entry);
      
      // 发送事件通知
      await _eventTracking.trackEvent(AIEvent(
        id: 'high_priority_log_${DateTime.now().millisecondsSinceEpoch}',
        userId: entry.userId,
        assistantName: entry.assistantName,
        type: AIEventType.highPriorityLog,
        data: entry.toMap(),
      ));
    } catch (e) {
      debugPrint('处理高优先级日志失败: $e');
    }
  }

  Map<String, dynamic> _analyzeLogEntries(List<AILogEntry> logs) {
    final analysis = {
      'total_entries': logs.length,
      'by_level': <String, int>{},
      'by_assistant': <String, int>{},
      'error_patterns': <String, int>{},
      'time_distribution': <String, int>{},
    };

    for (final log in logs) {
      // 按级别统计
      analysis['by_level'][log.level.toString()] = 
        (analysis['by_level'][log.level.toString()] ?? 0) + 1;
      
      // 按助手统计
      analysis['by_assistant'][log.assistantName] = 
        (analysis['by_assistant'][log.assistantName] ?? 0) + 1;
      
      // 错误模式分析
      if (log.level == LogLevel.error || log.level == LogLevel.critical) {
        final pattern = _extractErrorPattern(log.message);
        analysis['error_patterns'][pattern] = 
          (analysis['error_patterns'][pattern] ?? 0) + 1;
      }
      
      // 时间分布
      final hour = log.timestamp.hour.toString().padLeft(2, '0');
      analysis['time_distribution'][hour] = 
        (analysis['time_distribution'][hour] ?? 0) + 1;
    }

    return analysis;
  }

  String _extractErrorPattern(String message) {
    // 简单的错误模式提取
    final patterns = [
      r'timeout|超时',
      r'connection|连接',
      r'permission|权限',
      r'quota|配额',
      r'invalid|无效',
    ];

    for (final pattern in patterns) {
      if (RegExp(pattern, caseSensitive: false).hasMatch(message)) {
        return pattern.split('|')[0];
      }
    }

    return 'other';
  }

  void _startPeriodicFlush() {
    Timer.periodic(Duration(minutes: 5), (_) => _flushBuffer());
  }

  Future<void> _flushBuffer() async {
    if (_logBuffer.isEmpty) return;

    try {
      final entries = List<AILogEntry>.from(_logBuffer);
      _logBuffer.clear();

      // 批量保存日志
      await _storageService.saveLogs(entries);
    } catch (e) {
      debugPrint('刷新日志缓冲区失败: $e');
    }
  }

  @override
  void onClose() {
    _flushBuffer();
    super.onClose();
  }
} 