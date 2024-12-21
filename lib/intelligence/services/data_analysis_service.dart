class DataAnalysisService extends GetxService {
  final AIService _aiService;
  final StorageService _storageService;
  final EventTrackingService _eventTracking;
  final SubscriptionService _subscriptionService;
  
  // 分析配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _analysisConfig = {
    SubscriptionPlan.basic: {
      'max_data_points': 1000,
      'analysis_types': {'basic', 'trend'},
      'update_interval': Duration(hours: 24),
    },
    SubscriptionPlan.pro: {
      'max_data_points': 10000,
      'analysis_types': {'basic', 'trend', 'correlation', 'prediction'},
      'update_interval': Duration(hours: 6),
    },
    SubscriptionPlan.premium: {
      'max_data_points': -1,  // 无限制
      'analysis_types': {'basic', 'trend', 'correlation', 'prediction', 'custom'},
      'update_interval': Duration(hours: 1),
    },
  };
  
  DataAnalysisService({
    required AIService aiService,
    required StorageService storageService,
    required EventTrackingService eventTracking,
    required SubscriptionService subscriptionService,
  })  : _aiService = aiService,
        _storageService = storageService,
        _eventTracking = eventTracking,
        _subscriptionService = subscriptionService;

  Future<Map<String, dynamic>> analyzeUserData(
    String userId,
    String dataType, {
    DateTime? startTime,
    DateTime? endTime,
    String? analysisType,
    Map<String, dynamic>? options,
  }) async {
    try {
      // 验证分析类型
      if (!_canPerformAnalysis(analysisType ?? 'basic')) {
        throw AIException(
          '当前订阅计划不支持此类分析',
          code: 'ANALYSIS_TYPE_NOT_ALLOWED',
        );
      }

      // 获取数据
      final data = await _getData(
        userId,
        dataType,
        startTime: startTime,
        endTime: endTime,
      );

      // 执行分析
      final results = await _performAnalysis(
        data,
        analysisType ?? 'basic',
        options: options,
      );

      // 记录分析事件
      await _trackAnalysisEvent(
        userId,
        dataType,
        analysisType ?? 'basic',
        success: true,
      );

      return results;
    } catch (e) {
      await _trackAnalysisEvent(
        userId,
        dataType,
        analysisType ?? 'basic',
        success: false,
        error: e,
      );
      rethrow;
    }
  }

  Future<Map<String, dynamic>> generateInsights(
    String userId,
    List<String> dataTypes,
  ) async {
    try {
      final insights = <String, dynamic>{};
      
      for (final dataType in dataTypes) {
        // 获取数据
        final data = await _getData(
          userId,
          dataType,
          startTime: DateTime.now().subtract(Duration(days: 30)),
        );
        
        // 生成洞察
        insights[dataType] = await _generateDataInsights(data, dataType);
      }
      
      // 生成综合洞察
      insights['overall'] = await _generateOverallInsights(insights);
      
      return insights;
    } catch (e) {
      throw AIException(
        '生成洞察失败',
        code: 'GENERATE_INSIGHTS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> predictTrends(
    String userId,
    String dataType, {
    required Duration predictionWindow,
    Map<String, dynamic>? options,
  }) async {
    try {
      // 验证预测功能
      if (!_canPerformAnalysis('prediction')) {
        throw AIException(
          '当前订阅计划不支持预测功能',
          code: 'PREDICTION_NOT_ALLOWED',
        );
      }

      // 获取历史数据
      final historicalData = await _getData(
        userId,
        dataType,
        startTime: DateTime.now().subtract(predictionWindow * 2),
      );

      // 执行预测
      return await _performPrediction(
        historicalData,
        predictionWindow,
        options: options,
      );
    } catch (e) {
      throw AIException(
        '预测趋势失败',
        code: 'PREDICT_TRENDS_ERROR',
        details: e,
      );
    }
  }

  Future<List<Map<String, dynamic>>> _getData(
    String userId,
    String dataType, {
    DateTime? startTime,
    DateTime? endTime,
  }) async {
    try {
      final data = await _storageService.getData(
        userId: userId,
        dataType: dataType,
        startTime: startTime,
        endTime: endTime,
      );

      // 检查数据点限制
      final maxPoints = _getMaxDataPoints();
      if (maxPoints != -1 && data.length > maxPoints) {
        // 采样数据
        return _sampleData(data, maxPoints);
      }

      return data;
    } catch (e) {
      throw AIException(
        '获取数据失败',
        code: 'GET_DATA_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> _performAnalysis(
    List<Map<String, dynamic>> data,
    String analysisType, {
    Map<String, dynamic>? options,
  }) async {
    try {
      switch (analysisType) {
        case 'basic':
          return await _basicAnalysis(data);
        case 'trend':
          return await _trendAnalysis(data);
        case 'correlation':
          return await _correlationAnalysis(data);
        case 'prediction':
          return await _predictionAnalysis(data);
        case 'custom':
          return await _customAnalysis(data, options);
        default:
          throw AIException(
            '未知的分析类型',
            code: 'UNKNOWN_ANALYSIS_TYPE',
          );
      }
    } catch (e) {
      throw AIException(
        '执行分析失败',
        code: 'PERFORM_ANALYSIS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> _generateDataInsights(
    List<Map<String, dynamic>> data,
    String dataType,
  ) async {
    try {
      // 使用AI模型生成洞察
      final response = await _aiService.analyze(
        message: jsonEncode(data),
        type: 'insights',
        context: {
          'data_type': dataType,
          'data_size': data.length,
          'time_range': {
            'start': data.first['timestamp'],
            'end': data.last['timestamp'],
          },
        },
      );

      return response;
    } catch (e) {
      throw AIException(
        '生成数据洞察失败',
        code: 'GENERATE_DATA_INSIGHTS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> _generateOverallInsights(
    Map<String, dynamic> insights,
  ) async {
    try {
      // 使用AI模型生成综合洞察
      final response = await _aiService.analyze(
        message: jsonEncode(insights),
        type: 'overall_insights',
      );

      return response;
    } catch (e) {
      throw AIException(
        '生成综合洞察失败',
        code: 'GENERATE_OVERALL_INSIGHTS_ERROR',
        details: e,
      );
    }
  }

  bool _canPerformAnalysis(String analysisType) {
    final plan = _subscriptionService.currentPlan;
    final config = _analysisConfig[plan]!;
    return (config['analysis_types'] as Set<String>).contains(analysisType);
  }

  int _getMaxDataPoints() {
    final plan = _subscriptionService.currentPlan;
    return _analysisConfig[plan]!['max_data_points'] as int;
  }

  List<Map<String, dynamic>> _sampleData(
    List<Map<String, dynamic>> data,
    int maxPoints,
  ) {
    final step = data.length ~/ maxPoints;
    return data.asMap()
        .entries
        .where((entry) => entry.key % step == 0)
        .map((entry) => entry.value)
        .take(maxPoints)
        .toList();
  }

  Future<void> _trackAnalysisEvent(
    String userId,
    String dataType,
    String analysisType, {
    required bool success,
    dynamic error,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'analysis_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      assistantName: 'system',
      type: AIEventType.analysis,
      data: {
        'data_type': dataType,
        'analysis_type': analysisType,
        'success': success,
        'error': error?.toString(),
      },
    ));
  }
} 