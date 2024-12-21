class SessionManagerService extends GetxService {
  final ContextManagerService _contextManager;
  final ChatHistoryService _historyService;
  final ModelManagerService _modelManager;
  final SubscriptionService _subscriptionService;
  
  // 活跃会话缓存
  final Map<String, AISession> _activeSessions = {};
  
  // 会话配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _sessionConfig = {
    SubscriptionPlan.basic: {
      'max_sessions': 1,
      'session_timeout': Duration(minutes: 30),
      'context_retention': Duration(hours: 2),
    },
    SubscriptionPlan.pro: {
      'max_sessions': 3,
      'session_timeout': Duration(hours: 2),
      'context_retention': Duration(hours: 24),
    },
    SubscriptionPlan.premium: {
      'max_sessions': 10,
      'session_timeout': Duration(hours: 12),
      'context_retention': Duration(days: 7),
    },
  };

  SessionManagerService({
    required ContextManagerService contextManager,
    required ChatHistoryService historyService,
    required ModelManagerService modelManager,
    required SubscriptionService subscriptionService,
  }) : _contextManager = contextManager,
       _historyService = historyService,
       _modelManager = modelManager,
       _subscriptionService = subscriptionService;

  @override
  void onInit() {
    super.onInit();
    _startCleanupTimer();
  }

  // 创建新会话
  Future<String> createSession(
    String assistantName,
    String modelId,
    Map<String, dynamic> config,
  ) async {
    final plan = await _subscriptionService.getCurrentPlan();
    final sessionConfig = _sessionConfig[plan]!;
    
    // 检查会话数量限制
    if (_activeSessions.length >= sessionConfig['max_sessions']) {
      throw AIException('已达到最大会话数限制');
    }

    // 创建会话
    final session = AISession(
      id: _generateSessionId(),
      assistantName: assistantName,
      model: await _modelManager.getModel(modelId),
      startTime: DateTime.now(),
      features: await _subscriptionService.getFeatures(),
    );

    // 初始化上下文
    await _contextManager.initializeContext(session.id);

    // 缓存会话
    _activeSessions[session.id] = session;

    return session.id;
  }

  // 获取会话
  Future<AISession> getSession(String sessionId) async {
    final session = _activeSessions[sessionId];
    if (session == null) {
      throw AIException('会话不存在或已过期');
    }
    return session;
  }

  // 结束会话
  Future<void> endSession(String sessionId) async {
    final session = await getSession(sessionId);
    
    // 保存历史记录
    await _historyService.saveSessionHistory(
      sessionId,
      session.assistantName,
    );

    // 清理上下文
    await _contextManager.clearContext(sessionId);

    // 移除缓存
    _activeSessions.remove(sessionId);
  }

  // 检查会话状态
  Future<bool> isSessionValid(String sessionId) async {
    try {
      final session = await getSession(sessionId);
      final plan = await _subscriptionService.getCurrentPlan();
      final timeout = _sessionConfig[plan]!['session_timeout'] as Duration;
      
      return DateTime.now().difference(session.startTime) < timeout;
    } catch (e) {
      return false;
    }
  }

  // 定期清理过期会话
  void _startCleanupTimer() {
    Timer.periodic(Duration(minutes: 15), (_) => _cleanupExpiredSessions());
  }

  Future<void> _cleanupExpiredSessions() async {
    final expiredSessions = <AISession>[];
    
    for (final session in _activeSessions.values) {
      if (!await isSessionValid(session.id)) {
        expiredSessions.add(session);
      }
    }

    for (final session in expiredSessions) {
      try {
        await endSession(session.id);
      } catch (e) {
        debugPrint('清理过期会话失败: ${session.id} - $e');
      }
    }
  }

  String _generateSessionId() {
    return 'session_${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(10000)}';
  }

  @override
  void onClose() {
    // 清理所有活跃会话
    for (final session in _activeSessions.values) {
      endSession(session.id);
    }
    super.onClose();
  }
} 