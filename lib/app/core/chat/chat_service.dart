import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../logger/logger.dart';
import '../ai/ai_service.dart';
import '../ai/graph_rag_service.dart';

@singleton
class ChatService {
  final NetworkService _network;
  final AIService _ai;
  final GraphRAGService _graphRag;
  final AppLogger _logger;

  ChatService(this._network, this._ai, this._graphRag, this._logger);

  Future<Map<String, dynamic>> sendMessage({
    required String chatId,
    required String content,
    required String senderId,
    String type = 'text',
  }) async {
    try {
      // 发送消息
      final response = await _network.post('/chat/send', {
        'chat_id': chatId,
        'content': content,
        'sender_id': senderId,
        'type': type,
        'timestamp': DateTime.now().toIso8601String(),
      });

      // 如果是AI助手对话，进行额外处理
      if (_isAIAssistant(chatId)) {
        await _processAIResponse(response);
      }

      return response;
    } catch (e, stack) {
      _logger.error('Error sending message', e, stack);
      rethrow;
    }
  }

  bool _isAIAssistant(String chatId) {
    return ['ai_xiaoi', 'ai_laoke', 'ai_xiaoke'].contains(chatId);
  }

  Future<void> _processAIResponse(Map<String, dynamic> response) async {
    try {
      // 分析用户意图
      final analysis = await _ai.analyze(response['content']);
      
      // 查询知识图谱
      if (analysis['requires_knowledge']) {
        final graphData = await _graphRag.queryKnowledgeGraph(
          response['content'],
        );
        response['knowledge_graph'] = graphData;
      }

      // 语音合成
      if (response['should_speak']) {
        await _ai.speak(response['content']);
      }
    } catch (e, stack) {
      _logger.error('Error processing AI response', e, stack);
    }
  }

  Future<List<Map<String, dynamic>>> getChatHistory(
    String chatId, {
    int limit = 20,
    String? lastMessageId,
  }) async {
    try {
      final response = await _network.get(
        '/chat/history/$chatId',
        params: {
          'limit': limit.toString(),
          if (lastMessageId != null) 'last_message_id': lastMessageId,
        },
      );
      return List<Map<String, dynamic>>.from(response['messages']);
    } catch (e, stack) {
      _logger.error('Error getting chat history', e, stack);
      rethrow;
    }
  }

  Future<void> markAsRead(String chatId, String messageId) async {
    try {
      await _network.post('/chat/read', {
        'chat_id': chatId,
        'message_id': messageId,
      });
    } catch (e, stack) {
      _logger.error('Error marking message as read', e, stack);
    }
  }
} 