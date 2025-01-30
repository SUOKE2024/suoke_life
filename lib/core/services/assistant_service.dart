import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'ai_service.dart';

class AssistantService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AiService _aiService = Get.find();

  final conversations = <String, List<Map<String, dynamic>>>{}.obs;
  final assistantState = <String, dynamic>{}.obs;
  final isProcessing = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initAssistant();
  }

  Future<void> _initAssistant() async {
    try {
      await _loadConversations();
      await _loadAssistantState();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize assistant', data: {'error': e.toString()});
    }
  }

  // 发送消息
  Future<Map<String, dynamic>> sendMessage(
    String sessionId,
    String message, {
    Map<String, dynamic>? context,
  }) async {
    if (isProcessing.value) {
      return {'error': '正在处理上一条消息'};
    }

    try {
      isProcessing.value = true;

      // 准备消息
      final userMessage = {
        'role': 'user',
        'content': message,
        'timestamp': DateTime.now().toIso8601String(),
      };

      // 添加到对话历史
      if (!conversations.containsKey(sessionId)) {
        conversations[sessionId] = [];
      }
      conversations[sessionId]!.add(userMessage);

      // 获取助手回复
      final response = await _getAssistantResponse(sessionId, message, context);

      // 添加助手回复到对话历史
      final assistantMessage = {
        'role': 'assistant',
        'content': response['reply'],
        'timestamp': DateTime.now().toIso8601String(),
      };
      conversations[sessionId]!.add(assistantMessage);

      // 保存对话历史
      await _saveConversations();

      // 更新助手状态
      await _updateAssistantState(sessionId, response['state']);

      return response;
    } catch (e) {
      await _loggingService.log('error', 'Failed to send message', data: {'session_id': sessionId, 'error': e.toString()});
      return {'error': e.toString()};
    } finally {
      isProcessing.value = false;
    }
  }

  // 获取建议
  Future<List<String>> getSuggestions(String input) async {
    try {
      final response = await _aiService.queryKnowledge(
        'get_suggestions',
        parameters: {'input': input},
      );
      return List<String>.from(response['suggestions'] ?? []);
    } catch (e) {
      await _loggingService.log('error', 'Failed to get suggestions', data: {'error': e.toString()});
      return [];
    }
  }

  // 执行任务
  Future<Map<String, dynamic>> executeTask(
    String taskType,
    Map<String, dynamic> parameters,
  ) async {
    try {
      return await _aiService.queryKnowledge(
        'execute_task',
        parameters: {
          'task_type': taskType,
          'parameters': parameters,
        },
      );
    } catch (e) {
      await _loggingService.log('error', 'Failed to execute task', data: {'task_type': taskType, 'error': e.toString()});
      return {'error': e.toString()};
    }
  }

  // 获取对话历史
  Future<List<Map<String, dynamic>>> getConversationHistory(String sessionId) async {
    try {
      return conversations[sessionId] ?? [];
    } catch (e) {
      await _loggingService.log('error', 'Failed to get conversation history', data: {'session_id': sessionId, 'error': e.toString()});
      return [];
    }
  }

  // 清除对话历史
  Future<void> clearConversation(String sessionId) async {
    try {
      conversations.remove(sessionId);
      await _saveConversations();
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear conversation', data: {'session_id': sessionId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadConversations() async {
    try {
      final saved = await _storageService.getLocal('assistant_conversations');
      if (saved != null) {
        conversations.value = Map<String, List<Map<String, dynamic>>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadAssistantState() async {
    try {
      final state = await _storageService.getLocal('assistant_state');
      if (state != null) {
        assistantState.value = Map<String, dynamic>.from(state);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveConversations() async {
    try {
      await _storageService.saveLocal('assistant_conversations', conversations.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _updateAssistantState(String sessionId, Map<String, dynamic>? state) async {
    try {
      if (state != null) {
        assistantState[sessionId] = state;
        await _storageService.saveLocal('assistant_state', assistantState.value);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getAssistantResponse(
    String sessionId,
    String message,
    Map<String, dynamic>? context,
  ) async {
    try {
      final history = conversations[sessionId] ?? [];
      final state = assistantState[sessionId];

      return await _aiService.chatWithAssistant(
        message,
        'conversation',
        parameters: {
          'session_id': sessionId,
          'history': history,
          'state': state,
          'context': context,
        },
      );
    } catch (e) {
      rethrow;
    }
  }
} 