class ContextManagerService extends GetxService {
  final SubscriptionService _subscriptionService;
  final CacheManagerService _cacheManager;
  final SecurityManagerService _securityManager;
  
  // 上下文配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _contextConfig = {
    SubscriptionPlan.basic: {
      'max_tokens': 1000,
      'max_messages': 10,
      'retention_time': Duration(hours: 2),
    },
    SubscriptionPlan.pro: {
      'max_tokens': 4000,
      'max_messages': 50,
      'retention_time': Duration(hours: 24),
    },
    SubscriptionPlan.premium: {
      'max_tokens': 16000,
      'max_messages': 200,
      'retention_time': Duration(days: 7),
    },
  };

  ContextManagerService({
    required SubscriptionService subscriptionService,
    required CacheManagerService cacheManager,
    required SecurityManagerService securityManager,
  }) : _subscriptionService = subscriptionService,
       _cacheManager = cacheManager,
       _securityManager = securityManager;

  // 初始化上下文
  Future<void> initializeContext(String sessionId) async {
    final plan = await _subscriptionService.getCurrentPlan();
    final config = _contextConfig[plan]!;
    
    await _cacheManager.set(
      _getContextKey(sessionId),
      {
        'messages': <String>[],
        'tokens': 0,
        'created_at': DateTime.now().toIso8601String(),
        'config': config,
      },
      expiry: config['retention_time'] as Duration,
    );
  }

  // 处理上下文
  Future<Map<String, dynamic>> processContext(
    Map<String, dynamic>? context,
    String sessionId,
  ) async {
    final existingContext = await _getContext(sessionId);
    if (existingContext == null) {
      await initializeContext(sessionId);
      return context ?? {};
    }

    // 合并上下文
    final mergedContext = {
      ...existingContext,
      ...?context,
    };

    // 安全检查
    await _securityManager.validateContext(mergedContext);

    // 令牌计数
    final tokens = _estimateTokens(mergedContext);
    final config = existingContext['config'] as Map<String, dynamic>;
    
    if (tokens > config['max_tokens']) {
      // 裁剪上下文以适应令牌限制
      return _truncateContext(mergedContext, config['max_tokens']);
    }

    return mergedContext;
  }

  // 更新上下文
  Future<void> updateContext(
    String sessionId,
    Map<String, dynamic> updates,
  ) async {
    final context = await _getContext(sessionId);
    if (context == null) {
      throw AIException('上下文不存在');
    }

    final messages = List<String>.from(context['messages']);
    messages.add(updates['message'] as String);

    final config = context['config'] as Map<String, dynamic>;
    if (messages.length > config['max_messages']) {
      messages.removeAt(0);
    }

    await _cacheManager.set(
      _getContextKey(sessionId),
      {
        ...context,
        'messages': messages,
        'tokens': _estimateTokens({'messages': messages}),
        'last_update': DateTime.now().toIso8601String(),
      },
      expiry: config['retention_time'] as Duration,
    );
  }

  // 清理上下文
  Future<void> clearContext(String sessionId) async {
    await _cacheManager.delete(_getContextKey(sessionId));
  }

  // 获取上下文
  Future<Map<String, dynamic>?> _getContext(String sessionId) async {
    return await _cacheManager.get(_getContextKey(sessionId));
  }

  // 生成上下文缓存键
  String _getContextKey(String sessionId) => 'context_$sessionId';

  // 估算令牌数量
  int _estimateTokens(Map<String, dynamic> context) {
    // 简单估算：每个字符算1个token
    return context.toString().length;
  }

  // 裁剪上下文
  Map<String, dynamic> _truncateContext(
    Map<String, dynamic> context,
    int maxTokens,
  ) {
    final messages = List<String>.from(context['messages']);
    while (_estimateTokens({'messages': messages}) > maxTokens && messages.isNotEmpty) {
      messages.removeAt(0);
    }
    return {
      ...context,
      'messages': messages,
    };
  }

  @override
  void onInit() {
    super.onInit();
    _startCleanupTask();
  }

  // 定期清理过期上下文
  void _startCleanupTask() {
    Timer.periodic(Duration(hours: 1), (_) => _cleanupExpiredContexts());
  }

  Future<void> _cleanupExpiredContexts() async {
    try {
      await _cacheManager.cleanup();
    } catch (e) {
      debugPrint('清理过期上下文失败: $e');
    }
  }
} 