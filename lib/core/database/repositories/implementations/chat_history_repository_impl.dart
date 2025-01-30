import 'dart:convert';
import 'package:logger/logger.dart';
import '../../models/chat_history.dart';
import '../../local/dao/chat_history_dao.dart';
import '../interfaces/chat_history_repository.dart';
import 'base_repository_impl.dart';

/// 聊天历史仓库实现
class ChatHistoryRepositoryImpl extends BaseRepositoryImpl<ChatHistory>
    implements ChatHistoryRepository {
  final ChatHistoryDao _dao;
  final Logger _logger = Logger();

  ChatHistoryRepositoryImpl(this._dao) : super(_dao);

  @override
  Future<List<ChatHistory>> getSessionHistory(String sessionId) async {
    try {
      return await _dao.findBySessionId(sessionId);
    } catch (e) {
      _logger.e('Error getting session history: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> getHistoryByTimeRange(int startTime, int endTime) async {
    try {
      return await _dao.findByTimeRange(startTime, endTime);
    } catch (e) {
      _logger.e('Error getting history by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> getRecentHistory(int limit) async {
    try {
      return await _dao.findRecent(limit);
    } catch (e) {
      _logger.e('Error getting recent history: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllSessions() async {
    try {
      return await _dao.getAllSessionIds();
    } catch (e) {
      _logger.e('Error getting all sessions: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteSession(String sessionId) async {
    try {
      await _dao.deleteBySessionId(sessionId);
    } catch (e) {
      _logger.e('Error deleting session: $e');
      rethrow;
    }
  }

  @override
  Future<void> clearAllHistory() async {
    try {
      await _dao.clear();
    } catch (e) {
      _logger.e('Error clearing all history: $e');
      rethrow;
    }
  }

  @override
  Future<int> getMessageCount(String sessionId) async {
    try {
      return await _dao.getSessionMessageCount(sessionId);
    } catch (e) {
      _logger.e('Error getting message count: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> searchHistory(String keyword) async {
    try {
      return await _dao.search(keyword);
    } catch (e) {
      _logger.e('Error searching history: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> getMessagesByType(String messageType) async {
    try {
      return await _dao.findByMessageType(messageType);
    } catch (e) {
      _logger.e('Error getting messages by type: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveMessages(List<ChatHistory> messages) async {
    try {
      await _dao.saveAll(messages);
    } catch (e) {
      _logger.e('Error saving messages: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, int>> getSessionStats(String sessionId) async {
    try {
      final messages = await getSessionHistory(sessionId);
      final stats = <String, int>{
        'total': messages.length,
        'user_messages': messages.where((m) => m.isUser).length,
        'ai_messages': messages.where((m) => !m.isUser).length,
      };
      
      // 按消息类型统计
      final typeStats = <String, int>{};
      for (var message in messages) {
        typeStats[message.messageType] = (typeStats[message.messageType] ?? 0) + 1;
      }
      stats.addAll(typeStats);

      return stats;
    } catch (e) {
      _logger.e('Error getting session stats: $e');
      rethrow;
    }
  }

  @override
  Future<String> exportSessionHistory(String sessionId, String format) async {
    try {
      final messages = await getSessionHistory(sessionId);
      
      switch (format.toLowerCase()) {
        case 'json':
          return json.encode(messages.map((m) => m.toMap()).toList());
        case 'text':
          return messages.map((m) => 
            '${m.isUser ? "User" : "AI"} (${DateTime.fromMillisecondsSinceEpoch(m.timestamp)}): ${m.message}'
          ).join('\n');
        default:
          throw ArgumentError('Unsupported format: $format');
      }
    } catch (e) {
      _logger.e('Error exporting session history: $e');
      rethrow;
    }
  }

  @override
  Future<void> importHistory(String data, String format) async {
    try {
      List<ChatHistory> messages;
      
      switch (format.toLowerCase()) {
        case 'json':
          final List<dynamic> jsonData = json.decode(data);
          messages = jsonData.map((m) => ChatHistory.fromMap(m)).toList();
          break;
        default:
          throw ArgumentError('Unsupported format: $format');
      }
      
      await saveMessages(messages);
    } catch (e) {
      _logger.e('Error importing history: $e');
      rethrow;
    }
  }
} 