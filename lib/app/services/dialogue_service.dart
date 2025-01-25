import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'ai_service.dart';
import 'nlp_service.dart';

class DialogueService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AiService _aiService = Get.find();
  final NlpService _nlpService = Get.find();

  final currentContext = <String, dynamic>{}.obs;
  final dialogueHistory = <Map<String, dynamic>>[].obs;
  final isProcessing = false.obs;

  // 处理用户输入
  Future<String> processInput(String input) async {
    if (isProcessing.value) return '正在处理上一条消息,请稍候...';
    
    try {
      isProcessing.value = true;
      
      // 意图识别
      final intent = await _nlpService.detectIntent(input);
      
      // 实体提取
      final entities = await _nlpService.extractEntities(input);
      
      // 更新对话上下文
      await _updateContext(intent, entities);
      
      // 生成回复
      final response = await _generateResponse(input, intent, entities);
      
      // 保存对���历史
      await _saveToHistory(input, response);
      
      return response;
    } catch (e) {
      await _loggingService.log('error', 'Failed to process input', data: {'error': e.toString()});
      return '抱歉,处理您的消息时出现错误';
    } finally {
      isProcessing.value = false;
    }
  }

  // 清除对话上下文
  Future<void> clearContext() async {
    try {
      currentContext.clear();
      await _storageService.removeLocal('dialogue_context');
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear context', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 获取对话历史
  Future<List<Map<String, dynamic>>> getHistory({int limit = 20}) async {
    try {
      final history = await _loadHistory();
      return history.take(limit).toList();
    } catch (e) {
      await _loggingService.log('error', 'Failed to get history', data: {'error': e.toString()});
      return [];
    }
  }

  Future<void> _updateContext(
    Map<String, dynamic> intent,
    List<Map<String, dynamic>> entities,
  ) async {
    try {
      currentContext.value = {
        ...currentContext,
        'last_intent': intent,
        'last_entities': entities,
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      await _storageService.saveLocal('dialogue_context', currentContext.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<String> _generateResponse(
    String input,
    Map<String, dynamic> intent,
    List<Map<String, dynamic>> entities,
  ) async {
    try {
      final response = await _aiService.chatWithAssistant(
        input,
        'dialogue',
        parameters: {
          'context': currentContext.value,
          'intent': intent,
          'entities': entities,
        },
      );
      
      return response;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveToHistory(String input, String response) async {
    try {
      final dialogue = {
        'input': input,
        'response': response,
        'context': Map<String, dynamic>.from(currentContext),
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      dialogueHistory.insert(0, dialogue);
      
      // 只保留最近100条记录
      if (dialogueHistory.length > 100) {
        dialogueHistory.removeRange(100, dialogueHistory.length);
      }
      
      await _storageService.saveLocal('dialogue_history', dialogueHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _loadHistory() async {
    try {
      final data = await _storageService.getLocal('dialogue_history');
      if (data != null) {
        dialogueHistory.value = List<Map<String, dynamic>>.from(data);
      }
      return dialogueHistory;
    } catch (e) {
      return [];
    }
  }

  @override
  void onInit() {
    super.onInit();
    _loadContext();
    _loadHistory();
  }

  Future<void> _loadContext() async {
    try {
      final context = await _storageService.getLocal('dialogue_context');
      if (context != null) {
        currentContext.value = Map<String, dynamic>.from(context);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to load context', data: {'error': e.toString()});
    }
  }
} 