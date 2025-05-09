import 'package:suoke_life/domain/models/chat_contact_model.dart';

/// 聊天仓库接口
abstract class ChatRepository {
  /// 获取所有聊天联系人列表
  Future<List<ChatContact>> getAllContacts();

  /// 获取收藏的联系人列表
  Future<List<ChatContact>> getFavoriteContacts();
  
  /// 获取最近联系人列表
  Future<List<ChatContact>> getRecentContacts(int limit);
  
  /// 获取所有智能体联系人
  Future<List<ChatContact>> getAgentContacts();
  
  /// 获取所有名医联系人
  Future<List<ChatContact>> getDoctorContacts();
  
  /// 获取所有供应商联系人
  Future<List<ChatContact>> getProviderContacts();
  
  /// 根据联系人ID获取聊天对话列表
  Future<List<ChatMessage>> getChatMessages(String contactId, {int limit = 20, int offset = 0});
  
  /// 发送聊天消息
  Future<ChatMessage> sendMessage(String contactId, String content, {ChatMessageType type = ChatMessageType.text});
  
  /// 标记消息为已读
  Future<void> markMessagesAsRead(String contactId);
  
  /// 将联系人添加到收藏
  Future<void> addContactToFavorites(String contactId);
  
  /// 将联系人从收藏中移除
  Future<void> removeContactFromFavorites(String contactId);
  
  /// 搜索联系人
  Future<List<ChatContact>> searchContacts(String query);
}

/// 聊天消息模型
class ChatMessage {
  /// 消息ID
  final String id;
  
  /// 发送者ID
  final String senderId;
  
  /// 接收者ID
  final String receiverId;
  
  /// 消息内容
  final String content;
  
  /// 消息类型
  final ChatMessageType type;
  
  /// 发送时间
  final DateTime sentTime;
  
  /// 是否已读
  final bool isRead;
  
  /// 消息状态
  final ChatMessageStatus status;
  
  /// 附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  ChatMessage({
    required this.id,
    required this.senderId,
    required this.receiverId,
    required this.content,
    required this.type,
    required this.sentTime,
    this.isRead = false,
    this.status = ChatMessageStatus.sent,
    this.extraData,
  });
}

/// 聊天消息类型
enum ChatMessageType {
  /// 文本消息
  text,
  
  /// 图片消息
  image,
  
  /// 语音消息
  voice,
  
  /// 视频消息
  video,
  
  /// 文件消息
  file,
  
  /// 位置消息
  location,
  
  /// 系统消息
  system,
}

/// 聊天消息状态
enum ChatMessageStatus {
  /// 发送中
  sending,
  
  /// 已发送
  sent,
  
  /// 已送达
  delivered,
  
  /// 已读
  read,
  
  /// 发送失败
  failed,
} 