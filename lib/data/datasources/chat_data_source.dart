import '../models/chat_model.dart';
import '../models/message_model.dart';

/// 聊天数据源接口
/// 定义聊天数据的获取和持久化方法
abstract class ChatDataSource {
  /// 获取用户的所有聊天会话
  Future<List<ChatModel>> getUserChats(String userId, {int limit = 20, int offset = 0});
  
  /// 获取特定类型的聊天会话
  Future<List<ChatModel>> getChatsByType(String userId, String type, {int limit = 20, int offset = 0});
  
  /// 通过ID获取聊天会话
  Future<ChatModel> getChatById(String chatId);
  
  /// 创建新的聊天会话
  Future<ChatModel> createChat(ChatModel chat);
  
  /// 更新聊天会话信息
  Future<void> updateChat(ChatModel chat);
  
  /// 删除聊天会话
  Future<void> deleteChat(String chatId);
  
  /// 获取聊天会话中的消息
  Future<List<MessageModel>> getChatMessages(String chatId, {int limit = 50, int offset = 0});
  
  /// 发送消息
  Future<MessageModel> sendMessage(MessageModel message);
  
  /// 更新消息状态
  Future<void> updateMessageStatus(String messageId, String status);
  
  /// 删除消息
  Future<void> deleteMessage(String messageId);
  
  /// 标记消息为已读
  Future<void> markMessagesAsRead(String chatId, String userId);
  
  /// 获取未读消息数量
  Future<int> getUnreadMessagesCount(String userId);
  
  /// 搜索聊天记录
  Future<List<MessageModel>> searchMessages(String userId, String query, {int limit = 20, int offset = 0});
  
  /// 获取最后一条消息的时间戳
  Future<DateTime?> getLastMessageTimestamp(String chatId);
  
  /// 添加用户到聊天会话
  Future<void> addUserToChat(String chatId, String userId);
  
  /// 从聊天会话中移除用户
  Future<void> removeUserFromChat(String chatId, String userId);
  
  /// 置顶聊天会话
  Future<void> pinChat(String chatId, String userId);
  
  /// 取消置顶聊天会话
  Future<void> unpinChat(String chatId, String userId);
  
  /// 静音聊天会话
  Future<void> muteChat(String chatId, String userId);
  
  /// 取消静音聊天会话
  Future<void> unmuteChat(String chatId, String userId);
  
  /// 归档聊天会话
  Future<void> archiveChat(String chatId, String userId);
  
  /// 取消归档聊天会话
  Future<void> unarchiveChat(String chatId, String userId);
} 