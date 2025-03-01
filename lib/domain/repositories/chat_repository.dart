import '../entities/chat.dart';
import '../entities/message.dart';

/// 聊天仓库接口
/// 定义应用中聊天数据相关的业务操作
abstract class ChatRepository {
  /// 获取用户的所有聊天会话
  Future<List<Chat>> getUserChats(String userId, {int limit = 20, int offset = 0});
  
  /// 获取特定类型的聊天会话
  Future<List<Chat>> getChatsByType(String userId, ChatType type, {int limit = 20, int offset = 0});
  
  /// 通过ID获取聊天会话
  Future<Chat> getChatById(String chatId);
  
  /// 创建新的聊天会话
  Future<Chat> createChat(Chat chat);
  
  /// 更新聊天会话信息
  Future<void> updateChat(Chat chat);
  
  /// 删除聊天会话
  Future<void> deleteChat(String chatId);
  
  /// 获取聊天会话中的消息
  Future<List<Message>> getChatMessages(String chatId, {int limit = 50, int offset = 0});
  
  /// 发送消息
  Future<Message> sendMessage(Message message);
  
  /// 更新消息状态
  Future<void> updateMessageStatus(String messageId, MessageStatus status);
  
  /// 删除消息
  Future<void> deleteMessage(String messageId);
  
  /// 标记消息为已读
  Future<void> markMessagesAsRead(String chatId, String userId);
  
  /// 获取未读消息数量
  Future<int> getUnreadMessagesCount(String userId);
  
  /// 搜索聊天记录
  Future<List<Message>> searchMessages(String userId, String query, {int limit = 20, int offset = 0});
  
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
  
  /// 发送AI消息
  Future<Message> sendAiMessage(String chatId, String userId, String content);
  
  /// 获取AI回复
  Future<Message> getAiReply(String chatId, String messageContent);
} 