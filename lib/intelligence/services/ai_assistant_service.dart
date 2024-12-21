import '../models/conversation_context.dart';
import '../models/message.dart';
import '../models/intent.dart';
import 'intent_recognition_service.dart';
import 'coze_service.dart';
import '../../service/services/voice_service.dart';
import '../../service/services/task_executor_service.dart';
import '../../core/exceptions.dart';
import 'base_assistant.dart';
import 'xiaoi_assistant.dart';
import 'xiaoke_assistant.dart';
import 'laoke_assistant.dart';
import 'session_manager_service.dart';
import 'context_manager_service.dart';
import 'error_handler_service.dart';
import 'validation_service.dart';
import 'analysis_service.dart';
import 'subscription_service.dart';

class AIAssistantService extends GetxService {
  final AIService _aiService;
  final SessionManagerService _sessionManager;
  final ContextManagerService _contextManager;
  final ErrorHandlerService _errorHandler;
  final ValidationService _validator;
  final AnalysisService _analysisService;
  final SubscriptionService _subscriptionService;

  // 助手实例缓存
  final Map<String, BaseAssistant> _assistants = {};

  AIAssistantService({
    required AIService aiService,
    required SessionManagerService sessionManager,
    required ContextManagerService contextManager,
    required ErrorHandlerService errorHandler,
    required ValidationService validator,
    required AnalysisService analysisService,
    required SubscriptionService subscriptionService,
  }) : _aiService = aiService,
       _sessionManager = sessionManager,
       _contextManager = contextManager,
       _errorHandler = errorHandler,
       _validator = validator,
       _analysisService = analysisService,
       _subscriptionService = subscriptionService;

  @override
  void onInit() {
    super.onInit();
    _initializeAssistants();
  }

  Future<void> _initializeAssistants() async {
    // 初始化各类助手
    _assistants.addAll({
      'xiaoi': XiaoiService(
        aiService: _aiService,
        sessionManager: _sessionManager,
        contextManager: _contextManager,
        errorHandler: _errorHandler,
        validator: _validator,
        analysisService: _analysisService,
      ),
      'laoke': LaokeService(
        aiService: _aiService,
        sessionManager: _sessionManager,
        contextManager: _contextManager,
        errorHandler: _errorHandler,
        validator: _validator,
        analysisService: _analysisService,
      ),
      'xiaoke': XiaokeService(
        aiService: _aiService,
        sessionManager: _sessionManager,
        contextManager: _contextManager,
        errorHandler: _errorHandler,
        validator: _validator,
        analysisService: _analysisService,
      ),
    });

    // 初始化所有助手
    await Future.wait(
      _assistants.values.map((assistant) => assistant.initialize())
    );
  }

  // 获取指定助手
  BaseAssistant getAssistant(String name) {
    final assistant = _assistants[name];
    if (assistant == null) {
      throw AIException('助手不存在: $name');
    }
    return assistant;
  }

  // 检查访问权限
  Future<AIFeatureAccess> checkAccess(String assistantName) async {
    final plan = await _subscriptionService.getCurrentPlan();
    return AIFeatureAccess(
      dailyQuota: plan.aiQuota,
      advancedAnalysis: plan.hasAdvancedAnalysis,
      customPrompts: plan.hasCustomPrompts,
      priorityResponse: plan.hasPriorityResponse,
    );
  }

  // 聊天接口
  Future<String> chat(
    String message, {
    required String assistantName,
    Map<String, dynamic>? context,
  }) async {
    try {
      final assistant = getAssistant(assistantName);
      final access = await checkAccess(assistantName);
      
      return await assistant.chat(
        message,
        access: access,
        context: context,
      );
    } catch (e) {
      throw await _errorHandler.handleError(e);
    }
  }

  // 重置助手
  Future<void> reset(String assistantName) async {
    final assistant = getAssistant(assistantName);
    await assistant.reset();
  }

  // 获取助手能力
  Future<Map<String, dynamic>> getCapabilities(String assistantName) async {
    final assistant = getAssistant(assistantName);
    return await assistant.getCapabilities();
  }

  @override
  void onClose() {
    for (final assistant in _assistants.values) {
      assistant.reset();
    }
    super.onClose();
  }
} 