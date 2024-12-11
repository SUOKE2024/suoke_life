import '../models/conversation_context.dart';
import '../models/message.dart';
import '../models/intent.dart';
import 'intent_recognition_service.dart';
import 'coze_service.dart';
import '../../service/services/voice_service.dart';
import '../../service/services/task_executor_service.dart';

class AIAssistantService {
  final VoiceService _voiceService;
  final IntentRecognitionService _intentService;
  final CozeService _cozeService;
  final TaskExecutorService _taskExecutor;
  late ConversationContext _context;
  
  AIAssistantService({
    required String nasBasePath,
    required String botId,
    required String apiKey,
  }) : _voiceService = VoiceService(nasBasePath: nasBasePath),
       _intentService = IntentRecognitionService(),
       _cozeService = CozeService(botId: botId, apiKey: apiKey),
       _taskExecutor = TaskExecutorService(workingDirectory: nasBasePath) {
    _context = ConversationContext();
  }
  
  Future<void> initialize() async {
    await _voiceService.initialize();
  }
  
  Future<Message> processUserInput(String input) async {
    // 1. 更新对话上下文
    _context.addUserMessage(input);
    
    // 2. 意图识别和语义理解
    final intent = _intentService.recognizeIntent(input, _context);
    
    // 3. 根据意图生成回复
    final response = await _generateResponse(input, intent);
    final assistantMessage = Message(
      content: response,
      role: 'assistant',
      timestamp: DateTime.now(),
    );
    
    // 4. 更新上下文
    _context.addAssistantMessage(response);
    
    // 5. 语音播报回复
    await _voiceService.speak(response);
    
    return assistantMessage;
  }
  
  Future<String> _generateResponse(String input, Intent intent) async {
    // 1. 对于任务执行意图，尝试执行任务
    if (intent.type == Intent.TASK_EXECUTION && intent.confidence > 0.8) {
      final result = await _taskExecutor.executeTask(intent);
      if (result.success) {
        return result.message;
      }
    }
    
    // 2. 对于其他高置信度的特定意图，使用模板回复
    if (intent.confidence > 0.8 && intent.type != Intent.GENERAL_CHAT) {
      return await _generateTemplateResponse(intent);
    }
    
    // 3. 其他情况使用 Coze 生成回复
    try {
      final analysis = await _cozeService.analyze(input);
      final enhancedContext = _context.messages.toList();
      
      // 添加意图信息到上下文
      enhancedContext.add(Message(
        content: '用户意图: ${intent.type}, 置信度: ${intent.confidence}',
        role: 'system',
        timestamp: DateTime.now(),
      ));
      
      // 添加语义分析结果到上下文
      if (analysis.isNotEmpty) {
        enhancedContext.add(Message(
          content: '语义分析: ${jsonEncode(analysis)}',
          role: 'system',
          timestamp: DateTime.now(),
        ));
      }
      
      final response = await _cozeService.chat(enhancedContext);
      return response;
    } catch (e) {
      print('Error generating response: $e');
      return await _generateTemplateResponse(intent);
    }
  }
  
  Future<String> _generateTemplateResponse(Intent intent) async {
    switch (intent.type) {
      case Intent.TASK_EXECUTION:
        final action = intent.parameters['action'] as String?;
        final target = intent.parameters['target'] as String?;
        return '好的，我将${action ?? '执行'}${target ?? '任务'}';
        
      case Intent.INFORMATION_QUERY:
        final queryType = intent.parameters['queryType'] as String?;
        final queryTarget = intent.parameters['queryTarget'] as String?;
        return '让我来告诉你${queryTarget ?? '这个问题'}';
        
      case Intent.SYSTEM_CONTROL:
        final setting = intent.parameters['setting'] as String?;
        final value = intent.parameters['value'] as String?;
        return '正在${setting ?? '设置'}${value != null ? '为$value' : ''}';
        
      case Intent.GENERAL_CHAT:
      default:
        return '我明白了，让我们继续聊聊这个话题...';
    }
  }
  
  Future<void> startListening({
    required Function(String) onInterimResult,
    required Function(Message) onFinalResult,
  }) async {
    await _voiceService.startListening(
      onResult: onInterimResult,
      onComplete: () async {
        if (_voiceService.isListening) {
          final lastRecord = (await _voiceService.getVoiceHistory()).first;
          final message = await processUserInput(lastRecord.content);
          onFinalResult(message);
        }
      },
    );
  }
  
  Future<void> stopListening() async {
    await _voiceService.stopListening();
  }
  
  Future<void> stopSpeaking() async {
    await _voiceService.stop();
  }
  
  bool get isListening => _voiceService.isListening;
  
  ConversationContext get context => _context;
} 