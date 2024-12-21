class AIService extends GetxService {
  final ModelManagerService _modelManager;
  final ContextManagerService _contextManager;
  final ErrorHandlerService _errorHandler;
  final AnalysisService _analysisService;
  final QuotaManagerService _quotaManager;
  final SecurityManagerService _securityManager;

  AIService({
    required ModelManagerService modelManager,
    required ContextManagerService contextManager,
    required ErrorHandlerService errorHandler,
    required AnalysisService analysisService,
    required QuotaManagerService quotaManager,
    required SecurityManagerService securityManager,
  }) : _modelManager = modelManager,
       _contextManager = contextManager,
       _errorHandler = errorHandler,
       _analysisService = analysisService,
       _quotaManager = quotaManager,
       _securityManager = securityManager;

  Future<String> chat(
    String message, {
    required String sessionId,
    Map<String, dynamic>? context,
  }) async {
    try {
      // 安全检查
      await _securityManager.validateRequest(
        message,
        sessionId: sessionId,
      );

      // 配额检查
      await _quotaManager.checkAndUpdateQuota(sessionId);

      // 获取会话模型
      final model = await _modelManager.getSessionModel(sessionId);

      // 处理上下文
      final enrichedContext = await _contextManager.processContext(
        context,
        sessionId,
      );

      // 生成响应
      final response = await model.generate(
        message,
        context: enrichedContext,
      );

      // 分析响应
      await _analysisService.analyzeResponse(
        message,
        response,
        sessionId,
      );

      return response;

    } catch (e) {
      throw await _errorHandler.handleAIError(e);
    }
  }

  Future<Map<String, dynamic>> analyze(
    String content, {
    required String type,
    required String sessionId,
    Map<String, dynamic>? options,
  }) async {
    try {
      // 安全检查
      await _securityManager.validateAnalysis(
        content,
        type: type,
        sessionId: sessionId,
      );

      // 配额检查
      await _quotaManager.checkAnalysisQuota(sessionId);

      // 获取分析模型
      final model = await _modelManager.getAnalysisModel(type);

      // 执行分析
      final results = await model.analyze(
        content,
        options: options,
      );

      // 记录分析
      await _analysisService.recordAnalysis(
        type,
        results,
        sessionId,
      );

      return results;

    } catch (e) {
      throw await _errorHandler.handleAnalysisError(e);
    }
  }

  @override
  void onInit() {
    super.onInit();
    _initializeService();
  }

  Future<void> _initializeService() async {
    try {
      await Future.wait([
        _modelManager.initialize(),
        _contextManager.initialize(),
        _analysisService.initialize(),
      ]);
    } catch (e) {
      debugPrint('AI服务初始化失败: $e');
    }
  }
} 