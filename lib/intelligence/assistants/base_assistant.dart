abstract class BaseAssistant extends GetxService {
  final AIService _aiService;
  final SessionManagerService _sessionManager;
  final ContextManagerService _contextManager;
  final ErrorHandlerService _errorHandler;
  final ValidationService _validator;
  final AnalysisService _analysisService;
  
  // 助手配置
  final String assistantName;
  final String defaultModel;
  final Map<String, dynamic> defaultConfig;
  
  // 会话状态
  String? _currentSessionId;
  AIModel? _currentModel;
  
  BaseAssistant({
    required AIService aiService,
    required SessionManagerService sessionManager,
    required ContextManagerService contextManager,
    required ErrorHandlerService errorHandler,
    required ValidationService validator,
    required AnalysisService analysisService,
    required this.assistantName,
    required this.defaultModel,
    required this.defaultConfig,
  }) : _aiService = aiService,
       _sessionManager = sessionManager,
       _contextManager = contextManager,
       _errorHandler = errorHandler,
       _validator = validator,
       _analysisService = analysisService;

  // 核心聊天方法
  Future<String> chat(String message, {
    required AIFeatureAccess access,
    Map<String, dynamic>? context
  }) async {
    try {
      // 验证输入
      await _validator.validateInput(message);
      
      // 检查访问权限
      if (!_checkAccess(access)) {
        throw AIAccessException('无访问权限');
      }

      // 获取或创建会话
      _currentSessionId ??= await _sessionManager.createSession(
        assistantName,
        defaultModel,
        defaultConfig,
      );

      // 处理上下文
      final enrichedContext = await _contextManager.enrichContext(
        context,
        _currentSessionId!,
      );

      // 调用AI服务
      final response = await _aiService.chat(
        message,
        sessionId: _currentSessionId!,
        context: enrichedContext,
      );

      // 分析响应
      await _analysisService.analyzeResponse(response);

      return response;

    } catch (e) {
      return await _errorHandler.handleError(e);
    }
  }

  // 检查访问权限
  bool _checkAccess(AIFeatureAccess access) {
    // 实现访问权限检查逻辑
    return true; 
  }

  // 重置会话
  Future<void> reset() async {
    if (_currentSessionId != null) {
      await _sessionManager.endSession(_currentSessionId!);
      _currentSessionId = null;
      _currentModel = null;
    }
  }
} 