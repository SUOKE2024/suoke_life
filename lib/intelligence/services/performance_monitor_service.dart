class PerformanceMonitorService extends GetxService {
  final StorageService _storageService;
  final EventTrackingService _eventTracking;
  final SubscriptionService _subscriptionService;
  
  // 性能监控配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _monitorConfig = {
    SubscriptionPlan.basic: {
      'metrics': ['response_time', 'error_rate'],
      'sample_interval': Duration(minutes: 15),
      'retention_days': 7,
      'features': {'basic_metrics'},
    },
    SubscriptionPlan.pro: {
      'metrics': ['response_time', 'error_rate', 'throughput', 'concurrency'],
      'sample_interval': Duration(minutes: 5),
      'retention_days': 30,
      'features': {'basic_metrics', 'advanced_metrics', 'alerts'},
    },
    SubscriptionPlan.premium: {
      'metrics': ['response_time', 'error_rate', 'throughput', 'concurrency', 'resource_usage', 'custom_metrics'],
      'sample_interval': Duration(minutes: 1),
      'retention_days': 90,
      'features': {'basic_metrics', 'advanced_metrics', 'alerts', 'custom_metrics', 'predictive_analytics'},
    },
  };
  
  // 性能数据缓存
  final Map<String, List<PerformanceMetric>> _metricsCache = {};
  final Map<String, DateTime> _lastSampleTime = {};
  
  PerformanceMonitorService({
    required StorageService storageService,
    required EventTrackingService eventTracking,
    required SubscriptionService subscriptionService,
  })  : _storageService = storageService,
        _eventTracking = eventTracking,
        _subscriptionService = subscriptionService {
    _startMetricsCollection();
  }

  Future<Map<String, dynamic>> getModelMetrics(String modelId) async {
    try {
      // 获取基础指标
      final basicMetrics = await _getBasicMetrics(modelId);
      
      // 获取高级指标（如果可用）
      final advancedMetrics = _canCollectAdvancedMetrics()
          ? await _getAdvancedMetrics(modelId)
          : null;
      
      // 获取自定义指标（如果可用）
      final customMetrics = _canCollectCustomMetrics()
          ? await _getCustomMetrics(modelId)
          : null;

      return {
        'basic': basicMetrics,
        if (advancedMetrics != null) 'advanced': advancedMetrics,
        if (customMetrics != null) 'custom': customMetrics,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      throw AIException(
        '获取性能指标失败',
        code: 'GET_METRICS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> getDetailedMetrics(String modelId) async {
    try {
      // 获取当前指标
      final currentMetrics = await getModelMetrics(modelId);
      
      // 获取历史数据
      final historicalData = await _getHistoricalData(modelId);
      
      // 计算趋势
      final trends = await _calculateTrends(historicalData);
      
      // 生成预测（如果可用）
      final predictions = _canUsePredictiveAnalytics()
          ? await _generatePredictions(historicalData)
          : null;

      return {
        'current': currentMetrics,
        'historical': historicalData,
        'trends': trends,
        if (predictions != null) 'predictions': predictions,
      };
    } catch (e) {
      throw AIException(
        '获取详细性能指标失败',
        code: 'GET_DETAILED_METRICS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> getSystemMetrics() async {
    try {
      return {
        'cpu_usage': await _getCPUUsage(),
        'memory_usage': await _getMemoryUsage(),
        'disk_usage': await _getDiskUsage(),
        'network_stats': await _getNetworkStats(),
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      throw AIException(
        '获取系统指标失败',
        code: 'GET_SYSTEM_METRICS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> getResourceUsage(String modelId) async {
    try {
      return {
        'memory': await _getModelMemoryUsage(modelId),
        'cpu': await _getModelCPUUsage(modelId),
        'gpu': await _getModelGPUUsage(modelId),
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      throw AIException(
        '获取资源使用情况失败',
        code: 'GET_RESOURCE_USAGE_ERROR',
        details: e,
      );
    }
  }

  Future<void> recordMetric(PerformanceMetric metric) async {
    try {
      // 更新缓存
      _updateMetricsCache(metric);
      
      // 保存到存储
      await _storageService.saveMetric(metric);
      
      // 检查告警条件
      if (_canUseAlerts()) {
        await _checkAlertConditions(metric);
      }
    } catch (e) {
      debugPrint('记录性能指标失败: $e');
    }
  }

  Future<Map<String, dynamic>> _getBasicMetrics(String modelId) async {
    final metrics = _metricsCache[modelId] ?? [];
    if (metrics.isEmpty) return {};
    
    // 计算基础指标
    return {
      'response_time': _calculateAverageResponseTime(metrics),
      'error_rate': _calculateErrorRate(metrics),
      'request_count': metrics.length,
    };
  }

  Future<Map<String, dynamic>> _getAdvancedMetrics(String modelId) async {
    final metrics = _metricsCache[modelId] ?? [];
    if (metrics.isEmpty) return {};
    
    // 计算高级指标
    return {
      'throughput': _calculateThroughput(metrics),
      'concurrency': _calculateConcurrency(metrics),
      'p95_response_time': _calculatePercentile(metrics, 95),
      'p99_response_time': _calculatePercentile(metrics, 99),
    };
  }

  Future<Map<String, dynamic>> _getCustomMetrics(String modelId) async {
    // TODO: 实现自定义指标收集
    return {};
  }

  Future<List<Map<String, dynamic>>> _getHistoricalData(String modelId) async {
    final retentionDays = _getRetentionDays();
    final startTime = DateTime.now().subtract(Duration(days: retentionDays));
    
    return await _storageService.getMetricsHistory(
      modelId,
      startTime: startTime,
    );
  }

  Future<Map<String, dynamic>> _calculateTrends(
    List<Map<String, dynamic>> historicalData,
  ) async {
    // TODO: 实现趋势分析
    return {};
  }

  Future<Map<String, dynamic>> _generatePredictions(
    List<Map<String, dynamic>> historicalData,
  ) async {
    // TODO: 实现预测分析
    return {};
  }

  void _updateMetricsCache(PerformanceMetric metric) {
    final metrics = _metricsCache[metric.modelId] ?? [];
    metrics.add(metric);
    
    // 保留最近的数据
    final maxCacheSize = 1000;
    if (metrics.length > maxCacheSize) {
      metrics.removeRange(0, metrics.length - maxCacheSize);
    }
    
    _metricsCache[metric.modelId] = metrics;
    _lastSampleTime[metric.modelId] = DateTime.now();
  }

  Future<void> _checkAlertConditions(PerformanceMetric metric) async {
    final thresholds = await _getAlertThresholds(metric.modelId);
    
    // 检查各项指标是否超过阈值
    if (metric.responseTime > thresholds['response_time']) {
      await _triggerAlert(
        metric.modelId,
        'response_time',
        metric.responseTime,
        thresholds['response_time'],
      );
    }
    
    if (metric.errorRate > thresholds['error_rate']) {
      await _triggerAlert(
        metric.modelId,
        'error_rate',
        metric.errorRate,
        thresholds['error_rate'],
      );
    }
  }

  Future<void> _triggerAlert(
    String modelId,
    String metricName,
    dynamic currentValue,
    dynamic threshold,
  ) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'alert_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'system',
      assistantName: 'system',
      type: AIEventType.alert,
      data: {
        'model_id': modelId,
        'metric': metricName,
        'current_value': currentValue,
        'threshold': threshold,
        'severity': _calculateAlertSeverity(
          currentValue,
          threshold,
        ),
      },
    ));
  }

  bool _canCollectAdvancedMetrics() {
    final features = _getCurrentFeatures();
    return features.contains('advanced_metrics');
  }

  bool _canCollectCustomMetrics() {
    final features = _getCurrentFeatures();
    return features.contains('custom_metrics');
  }

  bool _canUseAlerts() {
    final features = _getCurrentFeatures();
    return features.contains('alerts');
  }

  bool _canUsePredictiveAnalytics() {
    final features = _getCurrentFeatures();
    return features.contains('predictive_analytics');
  }

  Set<String> _getCurrentFeatures() {
    final plan = _subscriptionService.currentPlan;
    return _monitorConfig[plan]!['features'] as Set<String>;
  }

  int _getRetentionDays() {
    final plan = _subscriptionService.currentPlan;
    return _monitorConfig[plan]!['retention_days'] as int;
  }

  Duration _getSampleInterval() {
    final plan = _subscriptionService.currentPlan;
    return _monitorConfig[plan]!['sample_interval'] as Duration;
  }

  void _startMetricsCollection() {
    Timer.periodic(_getSampleInterval(), (_) {
      _collectMetrics();
    });
  }

  Future<void> _collectMetrics() async {
    try {
      // 收集所有模型的指标
      for (final modelId in _metricsCache.keys) {
        await _collectModelMetrics(modelId);
      }
      
      // 清理过期数据
      _cleanupOldMetrics();
    } catch (e) {
      debugPrint('收集性能指标失败: $e');
    }
  }

  Future<void> _collectModelMetrics(String modelId) async {
    try {
      final metric = PerformanceMetric(
        modelId: modelId,
        timestamp: DateTime.now(),
        responseTime: await _measureResponseTime(modelId),
        errorRate: await _measureErrorRate(modelId),
        throughput: await _measureThroughput(modelId),
      );
      
      await recordMetric(metric);
    } catch (e) {
      debugPrint('收集模型指标失败: $modelId - $e');
    }
  }

  void _cleanupOldMetrics() {
    final retentionDays = _getRetentionDays();
    final cutoff = DateTime.now().subtract(Duration(days: retentionDays));
    
    for (final metrics in _metricsCache.values) {
      metrics.removeWhere((metric) => metric.timestamp.isBefore(cutoff));
    }
  }

  // ... 其他辅助方法的实现 ...
} 