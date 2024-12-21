class FeedbackService extends GetxService {
  final DataStorageService _storageService;
  final AnalysisService _analysisService;
  final EventTrackingService _eventTracking;
  
  FeedbackService({
    required DataStorageService storageService,
    required AnalysisService analysisService,
    required EventTrackingService eventTracking,
  })  : _storageService = storageService,
        _analysisService = analysisService,
        _eventTracking = eventTracking;

  Future<void> submitFeedback(AIFeedback feedback) async {
    try {
      // 保存反馈
      await _storageService.saveFeedback(feedback);
      
      // 记录反馈事件
      await _eventTracking.trackEvent(AIEvent(
        id: 'feedback_${DateTime.now().millisecondsSinceEpoch}',
        userId: feedback.userId,
        assistantName: feedback.assistantName,
        type: AIEventType.userFeedback,
        data: feedback.toMap(),
        sessionId: feedback.sessionId,
      ));
      
      // 分析反馈
      await _analysisService.analyzeFeedback(feedback);
    } catch (e) {
      throw AIException(
        '提交反馈失败',
        code: 'SUBMIT_FEEDBACK_ERROR',
        details: e,
      );
    }
  }

  Future<List<AIFeedback>> getFeedback({
    required String userId,
    String? assistantName,
    DateTime? startTime,
    DateTime? endTime,
    FeedbackType? type,
    int limit = 20,
  }) async {
    try {
      return await _storageService.getFeedback(
        userId: userId,
        assistantName: assistantName,
        startTime: startTime,
        endTime: endTime,
        type: type,
        limit: limit,
      );
    } catch (e) {
      throw AIException(
        '获取反馈失败',
        code: 'GET_FEEDBACK_ERROR',
        details: e,
      );
    }
  }

  Future<Map<String, dynamic>> generateFeedbackReport(
    String userId,
    String assistantName,
  ) async {
    try {
      final feedback = await getFeedback(
        userId: userId,
        assistantName: assistantName,
        startTime: DateTime.now().subtract(Duration(days: 30)),
      );

      return await _analysisService.generateFeedbackReport(feedback);
    } catch (e) {
      throw AIException(
        '生成反馈报告失败',
        code: 'GENERATE_FEEDBACK_REPORT_ERROR',
        details: e,
      );
    }
  }
} 