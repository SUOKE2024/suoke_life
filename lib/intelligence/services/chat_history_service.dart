class ChatHistoryService extends GetxService {
  final StorageService _storageService;
  final SubscriptionService _subscriptionService;
  final SecurityManagerService _securityManager;
  
  // 历史记录配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _historyConfig = {
    SubscriptionPlan.basic: {
      'max_history_days': 7,
      'max_messages_per_chat': 100,
      'export_formats': ['txt'],
    },
    SubscriptionPlan.pro: {
      'max_history_days': 30,
      'max_messages_per_chat': 1000,
      'export_formats': ['txt', 'json', 'csv'],
    },
    SubscriptionPlan.premium: {
      'max_history_days': 365,
      'max_messages_per_chat': -1, // 无限制
      'export_formats': ['txt', 'json', 'csv', 'pdf'],
    },
  };
  
  ChatHistoryService({
    required StorageService storageService,
    required SubscriptionService subscriptionService,
    required SecurityManagerService securityManager,
  })  : _storageService = storageService,
        _subscriptionService = subscriptionService,
        _securityManager = securityManager {
    _startCleanupTask();
  }

  // 保存会话历史
  Future<void> saveSessionHistory(
    String sessionId,
    String assistantName,
  ) async {
    final messages = await _storageService.getSessionMessages(sessionId);
    if (messages.isEmpty) return;

    final plan = await _subscriptionService.getCurrentPlan();
    final config = _historyConfig[plan]!;
    
    // 加密消息内容
    final encryptedMessages = await Future.wait(
      messages.map((msg) => _securityManager.encryptMessage(msg))
    );

    // 保存历史记录
    await _storageService.saveHistory(
      sessionId: sessionId,
      assistantName: assistantName,
      messages: encryptedMessages,
      metadata: {
        'timestamp': DateTime.now().toIso8601String(),
        'message_count': messages.length,
      },
      retention: Duration(days: config['max_history_days']),
    );
  }

  // 获取历史记录
  Future<List<ChatMessage>> getHistory({
    String? assistantName,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
    int offset = 0,
  }) async {
    try {
      final plan = await _subscriptionService.getCurrentPlan();
      final config = _historyConfig[plan]!;

      // 应用日期限制
      final maxDate = DateTime.now();
      final minDate = maxDate.subtract(
        Duration(days: config['max_history_days'])
      );

      startDate ??= minDate;
      endDate ??= maxDate;

      if (startDate.isBefore(minDate)) {
        startDate = minDate;
      }

      // 获取加密的历史记录
      final encryptedHistory = await _storageService.getHistory(
        assistantName: assistantName,
        startDate: startDate,
        endDate: endDate,
        limit: limit,
        offset: offset,
      );

      // 解密消息
      return await Future.wait(
        encryptedHistory.map((msg) => _securityManager.decryptMessage(msg))
      );

    } catch (e) {
      throw AIException('获取历史记录失败', details: e);
    }
  }

  // 导出历史记录
  Future<String> exportHistory({
    required String format,
    String? assistantName,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 验证导出格式
      final plan = await _subscriptionService.getCurrentPlan();
      final allowedFormats = _historyConfig[plan]!['export_formats'] as List<String>;
      
      if (!allowedFormats.contains(format)) {
        throw AIException('不支持的导出格式');
      }

      // 获取历史记录
      final history = await getHistory(
        assistantName: assistantName,
        startDate: startDate,
        endDate: endDate,
      );

      // 根据格式导出
      switch (format) {
        case 'txt':
          return _exportAsTxt(history);
        case 'json':
          return _exportAsJson(history);
        case 'csv':
          return _exportAsCsv(history);
        case 'pdf':
          return await _exportAsPdf(history);
        default:
          throw AIException('未知的导出格式');
      }

    } catch (e) {
      throw AIException('导出历史记录失败', details: e);
    }
  }

  // 清理历史记录
  Future<void> cleanupHistory({
    String? assistantName,
    DateTime? before,
  }) async {
    try {
      before ??= DateTime.now().subtract(
        Duration(days: _historyConfig[SubscriptionPlan.premium]!['max_history_days'])
      );

      await _storageService.deleteHistory(
        assistantName: assistantName,
        before: before,
      );

    } catch (e) {
      debugPrint('清理历史记录失败: $e');
    }
  }

  // 导出格式转换方法
  String _exportAsTxt(List<ChatMessage> history) {
    return history.map((msg) => 
      '${msg.role}: ${msg.content}\n'
    ).join('\n');
  }

  String _exportAsJson(List<ChatMessage> history) {
    return jsonEncode(history.map((msg) => msg.toMap()).toList());
  }

  String _exportAsCsv(List<ChatMessage> history) {
    const headers = 'Timestamp,Role,Content\n';
    final rows = history.map((msg) =>
      '${msg.timestamp},${msg.role},${msg.content}\n'
    ).join();
    return headers + rows;
  }

  Future<String> _exportAsPdf(List<ChatMessage> history) async {
    // TODO: 实现PDF导出
    throw UnimplementedError();
  }

  void _startCleanupTask() {
    Timer.periodic(Duration(days: 1), (_) {
      _cleanupOldHistory();
    });
  }

  Future<void> _cleanupOldHistory() async {
    try {
      final retentionDays = _historyConfig[_subscriptionService.currentPlan]!['retention_days'] as int;
      final cutoffDate = DateTime.now().subtract(Duration(days: retentionDays));
      
      await deleteHistory(
        'system',  // 系统级清理
        before: cutoffDate,
      );
    } catch (e) {
      debugPrint('清理历史记录失败: $e');
    }
  }
} 