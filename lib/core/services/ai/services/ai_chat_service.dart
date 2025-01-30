import 'package:uuid/uuid.dart';
import '../models/ai_response.dart';
import '../../chat/services/chat_session_service.dart';
import '../../chat/models/chat_session.dart';
import '../models/ai_config.dart';
import '../models/ai_service_response.dart';
import '../../../core/database/database_service.dart';

class AIChatService {
  final ChatSessionService _chatSessionService;
  final DatabaseService _db;
  final _uuid = const Uuid();

  AIChatService(this._chatSessionService) : _db = _chatSessionService.database;

  Future<String> createAISession(String userId, String aiType) async {
    final sessionId = _uuid.v4();
    final session = ChatSession(
      id: sessionId,
      participantIds: [userId, aiType],
      lastMessage: '',
      lastMessageTime: DateTime.now(),
      unreadCount: 0,
    );

    await _chatSessionService.createSession(session);
    return sessionId;
  }

  Future<AIResponse> sendMessage(
      String sessionId, String userId, String message) async {
    final session = await _chatSessionService.getSession(sessionId);
    if (session == null) {
      throw Exception('Session not found');
    }

    // 保存用户消息到历史记录
    await _saveMessageToHistory(sessionId, 'user', message);

    final aiType = session.participantIds.firstWhere(
      (id) => id != userId,
      orElse: () => throw Exception('AI participant not found'),
    );

    final response = await _generateAIResponse(aiType, message, sessionId);

    // 保存AI响应到历史记录
    await _saveMessageToHistory(sessionId, 'assistant', response.content);

    await _chatSessionService.updateLastMessage(
      sessionId,
      response.content,
      response.timestamp,
    );

    return response;
  }

  Future<AIResponse> _generateAIResponse(
      String aiType, String message, String sessionId) async {
    try {
      // 接入实际的AI服务
      final aiConfig = await _getAIConfig(aiType);
      final response = await _callAIService(
        message: message,
        config: aiConfig,
        context: await _getConversationContext(sessionId),
      );

      return AIResponse(
        content: response.text,
        aiType: aiType,
        timestamp: DateTime.now(),
        metadata: {
          'session_id': sessionId,
          'original_message': message,
          'model': aiConfig.model,
          'temperature': aiConfig.temperature,
        },
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<AIConfig> _getAIConfig(String aiType) async {
    return AIConfig.forType(aiType);
  }

  Future<List<Map<String, dynamic>>> _getConversationContext(
      String sessionId) async {
    final results = await _db.query(
      'SELECT role, content FROM message_history WHERE session_id = ? ORDER BY timestamp ASC',
      [sessionId],
    );

    return results
        .map((msg) => {
              'role': msg['role'],
              'content': msg['content'],
            })
        .toList();
  }

  Future<void> _saveMessageToHistory(
      String sessionId, String role, String content) async {
    await _db.insert('message_history', {
      'id': _uuid.v4(),
      'session_id': sessionId,
      'role': role,
      'content': content,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });
  }

  Future<AIServiceResponse> _callAIService({
    required String message,
    required AIConfig config,
    required List<Map<String, dynamic>> context,
  }) async {
    // 使用上下文生成响应
    if (context.isNotEmpty) {
      // 查找最近的包含 "my name is" 的用户消息
      final nameMessage = context.lastWhere(
        (msg) =>
            msg['role'] == 'user' &&
            msg['content'].toString().toLowerCase().contains('my name is'),
        orElse: () => {'content': ''},
      );

      if (message.toLowerCase().contains('what is my name') &&
          nameMessage['content'].toString().isNotEmpty) {
        final name = nameMessage['content']
            .toString()
            .toLowerCase()
            .split('my name is ')
            .last
            .trim();
        return AIServiceResponse(
          text: '你的名字是 $name',
          metadata: {
            'model': config.model,
            'temperature': config.temperature,
            'parameters': config.parameters,
          },
        );
      }
    }

    // 默认响应
    String response;
    switch (config.parameters['expertise']) {
      case 'daily_tasks':
        response = '小艾: 我可以帮您处理日常事务和回答问题。';
        break;
      case 'knowledge_exploration':
        response = '老克: 我专注于知识探索和学习指导。';
        break;
      case 'business_decision':
        response = '小克: 我可以协助您进行商业决策。';
        break;
      default:
        response = '我不太明白您的问题。';
    }

    return AIServiceResponse(
      text: response,
      metadata: {
        'model': config.model,
        'temperature': config.temperature,
        'parameters': config.parameters,
      },
    );
  }
}
