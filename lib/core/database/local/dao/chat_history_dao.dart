import '../../models/chat_history.dart';
import 'base_dao.dart';

/// 聊天历史数据访问对象接口
abstract class ChatHistoryDao extends BaseDao<ChatHistory> {
  /// 根据会话ID获取聊天记录
  Future<List<ChatHistory>> findBySessionId(String sessionId);

  /// 根据时间范围获取聊天记录
  Future<List<ChatHistory>> findByTimeRange(int startTime, int endTime);

  /// 获取最近的聊天记录
  Future<List<ChatHistory>> findRecent(int limit);

  /// 获取所有会话ID
  Future<List<String>> getAllSessionIds();

  /// 删除指定会话的聊天记录
  Future<void> deleteBySessionId(String sessionId);

  /// 清空所有聊天记录
  Future<void> clear();

  /// 获取会话的消息数量
  Future<int> getSessionMessageCount(String sessionId);

  /// 搜索聊天记录
  Future<List<ChatHistory>> search(String keyword);

  /// 获取指定类型的消息
  Future<List<ChatHistory>> findByMessageType(String messageType);

  /// 批量保存聊天记录
  Future<void> saveAll(List<ChatHistory> messages);
} 