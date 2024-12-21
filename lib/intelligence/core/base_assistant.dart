abstract class BaseAssistant extends GetxService {
  final AIService _aiService;
  final SessionManagerService _sessionManager;
  final ContextManagerService _contextManager;
  final ErrorHandlerService _errorHandler;
  final ValidationService _validator;
  final AnalysisService _analysisService;
  
  final String assistantName;
  final String defaultModel;
  final Map<String, dynamic> defaultConfig;
  
  String? _currentSessionId;
  AIModel? _currentModel;
  
  BaseAssistant({
    required this.assistantName,
    required this.defaultModel,
    required this.defaultConfig,
    required this.aiService,
    required this.sessionManager,
    required this.contextManager,
    required this.errorHandler,
    required this.validator,
    required this.analysisService,
  });

  Future<String> chat(String message, {
    required AIFeatureAccess access,
    Map<String, dynamic>? context
  });
  
  Future<void> initialize();
  Future<void> reset();
} 