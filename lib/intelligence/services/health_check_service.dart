class HealthCheckService extends GetxService {
  final ModelManagerService _modelManager;
  final PerformanceMonitorService _performanceMonitor;
  final EventTrackingService _eventTracking;
  final SubscriptionService _subscriptionService;
  
  // 健康检查配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _healthConfig = {
    SubscriptionPlan.basic: {
      'check_interval': Duration(minutes: 15),
      'metrics': ['error_rate', 'response_time'],
      'features': {'basic_monitoring'},
    },
    SubscriptionPlan.pro: {
      'check_interval': Duration(minutes: 5),
      'metrics': ['error_rate', 'response_time', 'throughput', 'availability'],
      'features': {'basic_monitoring', 'alerts', 'diagnostics'},
    },
    SubscriptionPlan.premium: {
      'check_interval': Duration(minutes: 1),
      'metrics': ['error_rate', 'response_time', 'throughput', 'availability', 'resource_usage'],
      'features': {'basic_monitoring', 'alerts', 'diagnostics', 'auto_recovery'},
    },
  };
  
  // 服务状态缓存
  final Map<String, ModelStatus> _statusCache = {};
  final Map<String, DateTime> _lastCheckTime = {};
  
  HealthCheckService({
    required ModelManagerService modelManager,
    required PerformanceMonitorService performanceMonitor,
    required EventTrackingService eventTracking,
    required SubscriptionService subscriptionService,
  })  : _modelManager = modelManager,
        _performanceMonitor = performanceMonitor,
        _eventTracking = eventTracking,
        _subscriptionService = subscriptionService {
    _startHealthCheck();
  }

  Future<ModelStatus> checkModel(String modelId) async {
    try {
      // 检查缓存
      if (_canUseCache(modelId)) {
        return _statusCache[modelId]!;
      }

      // 执行健康检查
      final metrics = await _performanceMonitor.getModelMetrics(modelId);
      final status = await _evaluateHealth(modelId, metrics);
      
      // 更新缓存
      _updateStatusCache(modelId, status);

      // 记录事件
      await _trackHealthEvent(
        'model_health_check',
        modelId,
        status: status,
      );

      return status;
    } catch (e) {
      throw AIException(
        '健康检查失败',
        code: 'HEALTH_CHECK_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> getSystemHealth() async {
    try {
      // 获取所有模型状态
      final modelStatuses = await _getAllModelStatuses();
      
      // 获取系统指标
      final systemMetrics = await _performanceMonitor.getSystemMetrics();
      
      // 评估系统健康状态
      final systemStatus = await _evaluateSystemHealth(
        modelStatuses,
        systemMetrics,
      );

      return {
        'status': systemStatus,
        'model_statuses': modelStatuses,
        'metrics': systemMetrics,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      throw AIException(
        '获取系统健康状态失败',
        code: 'GET_SYSTEM_HEALTH_ERROR',
        details: e,
      );
    }
  }

  Future<void> runDiagnostics(String modelId) async {
    try {
      // 检查权限
      if (!_canRunDiagnostics()) {
        throw AIException(
          '当前订阅计划不支持诊断功能',
          code: 'DIAGNOSTICS_NOT_ALLOWED',
        );
      }

      // 运行诊断
      final diagnosticResults = await _performDiagnostics(modelId);
      
      // 记录结果
      await _trackHealthEvent(
        'model_diagnostics',
        modelId,
        diagnostics: diagnosticResults,
      );

      // 如果发现问题，尝试自动恢复
      if (_shouldAttemptRecovery(diagnosticResults)) {
        await _attemptRecovery(modelId, diagnosticResults);
      }
    } catch (e) {
      throw AIException(
        '运行诊断失败',
        code: 'RUN_DIAGNOSTICS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> getModelMetrics(String modelId) async {
    try {
      final metrics = await _performanceMonitor.getModelMetrics(modelId);
      final status = await checkModel(modelId);
      
      return {
        'metrics': metrics,
        'status': status.toMap(),
        'history': await _getMetricsHistory(modelId),
      };
    } catch (e) {
      throw AIException(
        '获取模型指标失败',
        code: 'GET_METRICS_ERROR',
        details: e,
      );
    }
  }

  Future<ModelStatus> _evaluateHealth(
    String modelId,
    Map<String, dynamic> metrics,
  ) async {
    // 获取阈值配置
    final thresholds = await _getThresholds(modelId);
    
    // 检查各项指标
    final issues = <String>[];
    var isHealthy = true;

    if (metrics['error_rate'] > thresholds['error_rate']) {
      issues.add('错误率过高');
      isHealthy = false;
    }
    
    if (metrics['response_time'] > thresholds['response_time']) {
      issues.add('响应时间过长');
      isHealthy = false;
    }
    
    if (metrics['availability'] < thresholds['availability']) {
      issues.add('可用性不足');
      isHealthy = false;
    }

    return ModelStatus(
      isHealthy: isHealthy,
      status: isHealthy ? 'healthy' : 'unhealthy',
      message: issues.isEmpty ? null : issues.join(', '),
      details: {
        'metrics': metrics,
        'thresholds': thresholds,
      },
    );
  }

  Future<Map<String, ModelStatus>> _getAllModelStatuses() async {
    final statuses = <String, ModelStatus>{};
    final models = await _modelManager.getAvailableModels('system');
    
    for (final model in models) {
      try {
        statuses[model.id] = await checkModel(model.id);
      } catch (e) {
        debugPrint('获取模型状态失败: ${model.id} - $e');
      }
    }
    
    return statuses;
  }

  Future<String> _evaluateSystemHealth(
    Map<String, ModelStatus> modelStatuses,
    Map<String, dynamic> systemMetrics,
  ) async {
    // 检查模型健康状态
    final unhealthyModels = modelStatuses.values
        .where((status) => !status.isHealthy)
        .length;
    final totalModels = modelStatuses.length;
    
    // 检查系统指标
    final systemThresholds = await _getSystemThresholds();
    final systemHealthy = systemMetrics.entries
        .every((entry) => entry.value <= systemThresholds[entry.key]);
    
    // 评估整体健康状态
    if (unhealthyModels == 0 && systemHealthy) {
      return 'healthy';
    } else if (unhealthyModels < totalModels / 3) {
      return 'degraded';
    } else {
      return 'unhealthy';
    }
  }

  Future<Map<String, dynamic>> _performDiagnostics(String modelId) async {
    try {
      final model = await _modelManager.getModel(modelId);
      
      // 1. 基础连接性诊断
      final connectionDiagnostics = await _diagnoseConnection(model);
      if (!connectionDiagnostics['success']) {
        return {
          'status': 'connection_error',
          'details': connectionDiagnostics,
          'recommendations': [
            '检查网络连接',
            '验证模型服务是否在线',
            '检查认证配置',
          ],
        };
      }

      // 2. 性能诊断
      final performanceDiagnostics = await _diagnosePerformance(model);
      if (performanceDiagnostics['has_issues']) {
        return {
          'status': 'performance_issues',
          'details': performanceDiagnostics,
          'recommendations': _generatePerformanceRecommendations(
            performanceDiagnostics,
          ),
        };
      }

      // 3. 资源使用诊断
      final resourceDiagnostics = await _diagnoseResources(model);
      if (resourceDiagnostics['has_issues']) {
        return {
          'status': 'resource_issues',
          'details': resourceDiagnostics,
          'recommendations': _generateResourceRecommendations(
            resourceDiagnostics,
          ),
        };
      }

      // 4. 功能诊断
      final functionalDiagnostics = await _diagnoseFunctionality(model);
      if (!functionalDiagnostics['success']) {
        return {
          'status': 'functional_issues',
          'details': functionalDiagnostics,
          'recommendations': _generateFunctionalRecommendations(
            functionalDiagnostics,
          ),
        };
      }

      return {
        'status': 'healthy',
        'details': {
          'connection': connectionDiagnostics,
          'performance': performanceDiagnostics,
          'resources': resourceDiagnostics,
          'functionality': functionalDiagnostics,
        },
        'recommendations': [],
      };
    } catch (e) {
      return {
        'status': 'diagnostic_error',
        'error': e.toString(),
        'recommendations': [
          '联系技术支持',
          '检查诊断服务配置',
        ],
      };
    }
  }

  Future<void> _attemptRecovery(
    String modelId,
    Map<String, dynamic> diagnostics,
  ) async {
    if (!_canAttemptRecovery()) return;
    
    try {
      final status = diagnostics['status'];
      
      switch (status) {
        case 'connection_error':
          await _handleConnectionRecovery(modelId, diagnostics);
          break;
        case 'performance_issues':
          await _handlePerformanceRecovery(modelId, diagnostics);
          break;
        case 'resource_issues':
          await _handleResourceRecovery(modelId, diagnostics);
          break;
        case 'functional_issues':
          await _handleFunctionalRecovery(modelId, diagnostics);
          break;
        default:
          debugPrint('无法处理的状态: $status');
      }
    } catch (e) {
      debugPrint('自动恢复失败: $modelId - $e');
    }
  }

  Future<Map<String, dynamic>> _diagnoseConnection(AIModel model) async {
    try {
      // 1. 检查网络连接
      final networkCheck = await _checkNetworkConnectivity();
      if (!networkCheck['success']) {
        return {
          'success': false,
          'type': 'network_error',
          'details': networkCheck,
        };
      }

      // 2. 检查服务可用性
      final serviceCheck = await _checkServiceAvailability(model);
      if (!serviceCheck['success']) {
        return {
          'success': false,
          'type': 'service_error',
          'details': serviceCheck,
        };
      }

      // 3. 检查认证
      final authCheck = await _checkAuthentication(model);
      if (!authCheck['success']) {
        return {
          'success': false,
          'type': 'auth_error',
          'details': authCheck,
        };
      }

      return {
        'success': true,
        'latency': serviceCheck['latency'],
        'details': {
          'network': networkCheck,
          'service': serviceCheck,
          'auth': authCheck,
        },
      };
    } catch (e) {
      return {
        'success': false,
        'type': 'diagnostic_error',
        'error': e.toString(),
      };
    }
  }

  Future<Map<String, dynamic>> _diagnosePerformance(AIModel model) async {
    final metrics = await _performanceMonitor.getDetailedMetrics(model.id);
    final thresholds = await _getThresholds(model.id);
    
    final issues = <String, Map<String, dynamic>>{};
    
    // 检查各项性能指标
    if (metrics['response_time'] > thresholds['response_time']) {
      issues['response_time'] = {
        'current': metrics['response_time'],
        'threshold': thresholds['response_time'],
        'severity': 'high',
      };
    }
    
    if (metrics['error_rate'] > thresholds['error_rate']) {
      issues['error_rate'] = {
        'current': metrics['error_rate'],
        'threshold': thresholds['error_rate'],
        'severity': 'critical',
      };
    }
    
    return {
      'has_issues': issues.isNotEmpty,
      'metrics': metrics,
      'thresholds': thresholds,
      'issues': issues,
    };
  }

  Future<Map<String, dynamic>> _diagnoseResources(AIModel model) async {
    final resources = await _performanceMonitor.getResourceUsage(model.id);
    final limits = await _getResourceLimits(model.id);
    
    final issues = <String, Map<String, dynamic>>{};
    
    // 检查资源使用情况
    if (resources['memory'] > limits['memory']) {
      issues['memory'] = {
        'current': resources['memory'],
        'limit': limits['memory'],
        'severity': 'high',
      };
    }
    
    if (resources['cpu'] > limits['cpu']) {
      issues['cpu'] = {
        'current': resources['cpu'],
        'limit': limits['cpu'],
        'severity': 'medium',
      };
    }
    
    return {
      'has_issues': issues.isNotEmpty,
      'resources': resources,
      'limits': limits,
      'issues': issues,
    };
  }

  Future<Map<String, dynamic>> _diagnoseFunctionality(AIModel model) async {
    final testResults = await _runFunctionalTests(model);
    final failedTests = testResults.where((t) => !t['success']).toList();
    
    return {
      'success': failedTests.isEmpty,
      'total_tests': testResults.length,
      'failed_tests': failedTests.length,
      'details': failedTests,
    };
  }

  List<String> _generatePerformanceRecommendations(
    Map<String, dynamic> diagnostics,
  ) {
    final recommendations = <String>[];
    final issues = diagnostics['issues'] as Map<String, dynamic>;
    
    if (issues.containsKey('response_time')) {
      recommendations.addAll([
        '优化模型配置以提高响应速度',
        '考虑使用模型缓存',
        '检查网络延迟',
      ]);
    }
    
    if (issues.containsKey('error_rate')) {
      recommendations.addAll([
        '检查错误日志',
        '验证输入数据质量',
        '考虑降级策略',
      ]);
    }
    
    return recommendations;
  }

  List<String> _generateResourceRecommendations(
    Map<String, dynamic> diagnostics,
  ) {
    final recommendations = <String>[];
    final issues = diagnostics['issues'] as Map<String, dynamic>;
    
    if (issues.containsKey('memory')) {
      recommendations.addAll([
        '增加内存限制',
        '优化内存使用',
        '检查内存泄漏',
      ]);
    }
    
    if (issues.containsKey('cpu')) {
      recommendations.addAll([
        '增加CPU限制',
        '优化计算密集操作',
        '考虑任务调度',
      ]);
    }
    
    return recommendations;
  }

  bool _canUseCache(String modelId) {
    final lastCheck = _lastCheckTime[modelId];
    if (lastCheck == null) return false;
    
    final checkInterval = _getCheckInterval();
    return DateTime.now().difference(lastCheck) < checkInterval;
  }

  void _updateStatusCache(String modelId, ModelStatus status) {
    _statusCache[modelId] = status;
    _lastCheckTime[modelId] = DateTime.now();
  }

  Duration _getCheckInterval() {
    final plan = _subscriptionService.currentPlan;
    return _healthConfig[plan]!['check_interval'] as Duration;
  }

  bool _canRunDiagnostics() {
    final features = _getCurrentFeatures();
    return features.contains('diagnostics');
  }

  bool _canAttemptRecovery() {
    final features = _getCurrentFeatures();
    return features.contains('auto_recovery');
  }

  Set<String> _getCurrentFeatures() {
    final plan = _subscriptionService.currentPlan;
    return _healthConfig[plan]!['features'] as Set<String>;
  }

  Future<Map<String, dynamic>> _getThresholds(String modelId) async {
    // TODO: 从配置加载阈值
    return {
      'error_rate': 0.05,
      'response_time': 1000,
      'availability': 0.99,
    };
  }

  Future<Map<String, dynamic>> _getSystemThresholds() async {
    // TODO: 从配置加载系统阈值
    return {
      'cpu_usage': 0.8,
      'memory_usage': 0.8,
      'disk_usage': 0.8,
    };
  }

  bool _shouldAttemptRecovery(Map<String, dynamic> diagnostics) {
    // TODO: 根据诊断结果决定是否需要自动恢复
    return false;
  }

  Future<List<Map<String, dynamic>>> _getMetricsHistory(String modelId) async {
    // TODO: 实现指标历史记录获取
    return [];
  }

  Future<void> _trackHealthEvent(
    String action,
    String modelId, {
    ModelStatus? status,
    Map<String, dynamic>? diagnostics,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'health_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'system',
      assistantName: 'system',
      type: AIEventType.health,
      data: {
        'action': action,
        'model_id': modelId,
        'status': status?.toMap(),
        'diagnostics': diagnostics,
      },
    ));
  }

  void _startHealthCheck() {
    Timer.periodic(_getCheckInterval(), (_) {
      _runPeriodicHealthCheck();
    });
  }

  Future<void> _runPeriodicHealthCheck() async {
    try {
      final health = await getSystemHealth();
      
      if (health['status'] != 'healthy') {
        // 记录不健康状态
        await _trackHealthEvent(
          'system_health_check',
          'system',
          diagnostics: health,
        );
      }
    } catch (e) {
      debugPrint('定期健康检查失败: $e');
    }
  }
} 