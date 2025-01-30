import '../../models/chat_history.dart';
import 'base_repository.dart';

/// 聊天历史仓库接口
abstract class ChatHistoryRepository extends BaseRepository<ChatHistory> {
  /// 获取指定会话的聊天记录
  Future<List<ChatHistory>> getSessionHistory(String sessionId);

  /// 获取指定时间范围的聊天记录
  Future<List<ChatHistory>> getHistoryByTimeRange(int startTime, int endTime);

  /// 获取最近的聊天记录
  Future<List<ChatHistory>> getRecentHistory(int limit);

  /// 获取所有会话ID
  Future<List<String>> getAllSessions();

  /// 删除指定会话的聊天记录
  Future<void> deleteSession(String sessionId);

  /// 清空所有聊天记录
  Future<void> clearAllHistory();

  /// 获取会话的消息数量
  Future<int> getMessageCount(String sessionId);

  /// 搜索聊天记录
  Future<List<ChatHistory>> searchHistory(String keyword);

  /// 获取指定类型的消息
  Future<List<ChatHistory>> getMessagesByType(String messageType);

  /// 批量保存聊天记录
  Future<void> saveMessages(List<ChatHistory> messages);

  /// 获取会话统计信息
  Future<Map<String, int>> getSessionStats(String sessionId);

  /// 导出会话聊天记录
  Future<String> exportSessionHistory(String sessionId, String format);

  /// 导入聊天记录
  Future<void> importHistory(String data, String format);
} 