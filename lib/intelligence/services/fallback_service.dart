class FallbackService extends GetxService {
  final ModelManagerService _modelManager;
  final HealthCheckService _healthCheck;
  final EventTrackingService _eventTracking;
  final SubscriptionService _subscriptionService;
  
  // 降级配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _fallbackConfig = {
    SubscriptionPlan.basic: {
      'strategies': ['retry', 'timeout'],
      'max_retries': 3,
      'timeout': Duration(seconds: 10),
      'features': {'basic_fallback'},
    },
    SubscriptionPlan.pro: {
      'strategies': ['retry', 'timeout', 'circuit_breaker', 'model_switch'],
      'max_retries': 5,
      'timeout': Duration(seconds: 15),
      'features': {'basic_fallback', 'advanced_fallback', 'auto_recovery'},
    },
    SubscriptionPlan.premium: {
      'strategies': ['retry', 'timeout', 'circuit_breaker', 'model_switch', 'custom_fallback'],
      'max_retries': -1,  // 无限制
      'timeout': Duration(seconds: 30),
      'features': {'basic_fallback', 'advanced_fallback', 'auto_recovery', 'custom_strategies'},
    },
  };
  
  // 降级状态
  final Map<String, CircuitBreaker> _circuitBreakers = {};
  final Map<String, List<String>> _fallbackModels = {};
  
  FallbackService({
    required ModelManagerService modelManager,
    required HealthCheckService healthCheck,
    required EventTrackingService eventTracking,
    required SubscriptionService subscriptionService,
  })  : _modelManager = modelManager,
        _healthCheck = healthCheck,
        _eventTracking = eventTracking,
        _subscriptionService = subscriptionService {
    _initializeFallbacks();
  }

  Future<AIModel> getFallbackModel(String assistantName) async {
    try {
      // 获取可用的降级模型
      final fallbacks = _fallbackModels[assistantName];
      if (fallbacks == null || fallbacks.isEmpty) {
        throw AIException(
          '没有可用的降级模型',
          code: 'NO_FALLBACK_MODELS',
        );
      }

      // 选择最佳的降级模型
      final modelId = await _selectBestFallback(fallbacks);
      return await _modelManager.getModel(modelId);
    } catch (e) {
      throw AIException(
        '获取降级模型失败',
        code: 'GET_FALLBACK_MODEL_ERROR',
        details: e,
      );
    }
  }

  Future<T> executeFallback<T>({
    required Future<T> Function() operation,
    required String modelId,
    required String fallbackType,
    Map<String, dynamic>? options,
  }) async {
    try {
      // 检查熔断器状态
      if (_shouldBreakCircuit(modelId)) {
        throw AIException(
          '服务熔断中',
          code: 'CIRCUIT_BREAKER_OPEN',
        );
      }

      // 执行操作
      return await _executeWithFallback(
        operation,
        modelId,
        fallbackType,
        options,
      );
    } catch (e) {
      // 记录降级事件
      await _trackFallbackEvent(
        modelId,
        fallbackType,
        success: false,
        error: e,
      );
      rethrow;
    }
  }

  Future<void> updateCircuitBreaker(
    String modelId,
    bool success,
  ) async {
    final breaker = _getCircuitBreaker(modelId);
    
    if (success) {
      breaker.recordSuccess();
    } else {
      breaker.recordFailure();
      
      // 检查是否需要开启熔断
      if (breaker.shouldOpen()) {
        await _openCircuitBreaker(modelId);
      }
    }
  }

  Future<Map<String, dynamic>> getFallbackStatus(String modelId) async {
    try {
      final breaker = _getCircuitBreaker(modelId);
      final status = breaker.getStatus();
      
      return {
        'circuit_breaker': status,
        'fallback_models': _fallbackModels[modelId],
        'current_strategy': await _getCurrentStrategy(modelId),
        'metrics': await _getFallbackMetrics(modelId),
      };
    } catch (e) {
      throw AIException(
        '获取降级状态失败',
        code: 'GET_FALLBACK_STATUS_ERROR',
        details: e,
      );
    }
  }

  Future<T> _executeWithFallback<T>(
    Future<T> Function() operation,
    String modelId,
    String fallbackType,
    Map<String, dynamic>? options,
  ) async {
    final strategies = _getAvailableStrategies();
    
    for (final strategy in strategies) {
      try {
        switch (strategy) {
          case 'retry':
            return await _executeWithRetry(operation, options);
          case 'timeout':
            return await _executeWithTimeout(operation, options);
          case 'circuit_breaker':
            return await _executeWithCircuitBreaker(operation, modelId);
          case 'model_switch':
            return await _executeWithModelSwitch(operation, modelId, fallbackType);
          case 'custom_fallback':
            if (_canUseCustomStrategies()) {
              return await _executeCustomFallback(operation, options);
            }
            continue;
          default:
            continue;
        }
      } catch (e) {
        debugPrint('策略 $strategy 执行失败: $e');
        continue;
      }
    }
    
    throw AIException(
      '所有降级策略都失败了',
      code: 'ALL_FALLBACKS_FAILED',
    );
  }

  Future<T> _executeWithRetry<T>(
    Future<T> Function() operation,
    Map<String, dynamic>? options,
  ) async {
    final maxRetries = _getMaxRetries();
    var retryCount = 0;
    
    while (true) {
      try {
        return await operation();
      } catch (e) {
        retryCount++;
        if (maxRetries != -1 && retryCount >= maxRetries) {
          rethrow;
        }
        await Future.delayed(_getRetryDelay(retryCount));
      }
    }
  }

  Future<T> _executeWithTimeout<T>(
    Future<T> Function() operation,
    Map<String, dynamic>? options,
  ) async {
    final timeout = _getTimeout();
    return await operation().timeout(timeout);
  }

  Future<T> _executeWithCircuitBreaker<T>(
    Future<T> Function() operation,
    String modelId,
  ) async {
    final breaker = _getCircuitBreaker(modelId);
    
    if (breaker.isOpen()) {
      if (breaker.shouldAttemptReset()) {
        // 尝试半开状态
        breaker.halfOpen();
      } else {
        throw AIException(
          '服务熔断中',
          code: 'CIRCUIT_BREAKER_OPEN',
        );
      }
    }

    try {
      final result = await operation();
      breaker.recordSuccess();
      return result;
    } catch (e) {
      breaker.recordFailure();
      rethrow;
    }
  }

  Future<T> _executeWithModelSwitch<T>(
    Future<T> Function() operation,
    String modelId,
    String fallbackType,
  ) async {
    try {
      return await operation();
    } catch (e) {
      // 切换到降级模型
      final fallbackModel = await getFallbackModel(modelId);
      // TODO: 使用降级模型重试操作
      rethrow;
    }
  }

  Future<T> _executeCustomFallback<T>(
    Future<T> Function() operation,
    Map<String, dynamic>? options,
  ) async {
    // TODO: 实现自定义降级策略
    throw UnimplementedError();
  }

  CircuitBreaker _getCircuitBreaker(String modelId) {
    return _circuitBreakers[modelId] ??= CircuitBreaker(
      failureThreshold: 5,
      resetTimeout: Duration(seconds: 60),
    );
  }

  Future<void> _openCircuitBreaker(String modelId) async {
    final breaker = _getCircuitBreaker(modelId);
    breaker.open();
    
    // 记录熔断事件
    await _trackFallbackEvent(
      modelId,
      'circuit_breaker',
      success: true,
      metadata: {'action': 'open'},
    );
  }

  Future<String> _selectBestFallback(List<String> fallbacks) async {
    // TODO: 实现降级模型选择逻辑
    return fallbacks.first;
  }

  List<String> _getAvailableStrategies() {
    final plan = _subscriptionService.currentPlan;
    return _fallbackConfig[plan]!['strategies'] as List<String>;
  }

  int _getMaxRetries() {
    final plan = _subscriptionService.currentPlan;
    return _fallbackConfig[plan]!['max_retries'] as int;
  }

  Duration _getTimeout() {
    final plan = _subscriptionService.currentPlan;
    return _fallbackConfig[plan]!['timeout'] as Duration;
  }

  Duration _getRetryDelay(int retryCount) {
    // 指数退避
    return Duration(milliseconds: 100 * (1 << retryCount));
  }

  bool _canUseCustomStrategies() {
    final features = _getCurrentFeatures();
    return features.contains('custom_strategies');
  }

  Set<String> _getCurrentFeatures() {
    final plan = _subscriptionService.currentPlan;
    return _fallbackConfig[plan]!['features'] as Set<String>;
  }

  Future<void> _trackFallbackEvent(
    String modelId,
    String strategy,
    {
    required bool success,
    dynamic error,
    Map<String, dynamic>? metadata,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'fallback_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'system',
      assistantName: 'system',
      type: AIEventType.fallback,
      data: {
        'model_id': modelId,
        'strategy': strategy,
        'success': success,
        'error': error?.toString(),
        'metadata': metadata,
      },
    ));
  }

  void _initializeFallbacks() {
    // TODO: 从配置加载降级模型映射
    _fallbackModels.addAll({
      'xiaoi': ['xiaoi_basic_v1', 'xiaoi_fallback_v1'],
      'laoke': ['laoke_basic_v1', 'laoke_fallback_v1'],
      'xiaoke': ['xiaoke_basic_v1', 'xiaoke_fallback_v1'],
    });
  }
} 