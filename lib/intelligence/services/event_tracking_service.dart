class EventTrackingService extends GetxService {
  final AnalysisService _analysisService;
  final SubscriptionService _subscriptionService;
  final DataStorageService _storageService;
  
  EventTrackingService({
    required AnalysisService analysisService,
    required SubscriptionService subscriptionService,
    required DataStorageService storageService,
  })  : _analysisService = analysisService,
        _subscriptionService = subscriptionService,
        _storageService = storageService;

  Future<void> trackEvent(AIEvent event) async {
    try {
      // 记录事件
      await _storageService.saveEvent(event);
      
      // 高级用户进行实时分析
      if (_subscriptionService.currentFeatures.advancedAnalysis) {
        await _analysisService.analyzeEvent(event);
      }
    } catch (e) {
      debugPrint('事件追踪失败: $e');
    }
  }

  Future<List<AIEvent>> getEvents({
    required String userId,
    required String assistantName,
    DateTime? startTime,
    DateTime? endTime,
    String? type,
    int limit = 100,
  }) async {
    try {
      return await _storageService.getEvents(
        userId: userId,
        assistantName: assistantName,
        startTime: startTime,
        endTime: endTime,
        type: type,
        limit: limit,
      );
    } catch (e) {
      throw AIException(
        '获取事件失败',
        code: 'GET_EVENTS_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> generateEventReport(
    String userId,
    String assistantName,
  ) async {
    try {
      final features = _subscriptionService.currentFeatures;
      if (!features.advancedAnalysis) {
        return {
          'message': '需要升级到高级版本以使用此功能',
        };
      }

      final events = await getEvents(
        userId: userId,
        assistantName: assistantName,
        startTime: DateTime.now().subtract(Duration(days: 30)),
      );

      return await _analysisService.generateEventReport(events);
    } catch (e) {
      throw AIException(
        '生成事件报告失败',
        code: 'GENERATE_REPORT_ERROR',
        details: e,
      );
    }
  }
} 