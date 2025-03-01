import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

/// 消息类型枚举
enum MessageType {
  text,
  image,
  audio,
  video,
  file,
  system,
}

/// 消息发送状态枚举
enum MessageStatus {
  sending,
  sent,
  delivered,
  read,
  failed,
}

/// 消息实体类
/// 定义应用中聊天消息的核心属性和行为
class Message extends Equatable {
  final String id;
  final String content;
  final DateTime timestamp;
  final String senderId;
  final String? receiverId;
  final String? chatId;
  final MessageType type;
  final MessageStatus status;
  final Map<String, dynamic>? metadata;

  const Message({
    required this.id,
    required this.content,
    required this.timestamp,
    required this.senderId,
    this.receiverId,
    this.chatId,
    this.type = MessageType.text,
    this.status = MessageStatus.sent,
    this.metadata,
  });

  /// 创建新的文本消息
  factory Message.text({
    required String content,
    required String senderId,
    String? receiverId,
    String? chatId,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: const Uuid().v4(),
      content: content,
      timestamp: DateTime.now(),
      senderId: senderId,
      receiverId: receiverId,
      chatId: chatId,
      type: MessageType.text,
      status: MessageStatus.sending,
      metadata: metadata,
    );
  }

  /// 创建新的系统消息
  factory Message.system({
    required String content,
    String? chatId,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: const Uuid().v4(),
      content: content,
      timestamp: DateTime.now(),
      senderId: 'system',
      chatId: chatId,
      type: MessageType.system,
      status: MessageStatus.delivered,
      metadata: metadata,
    );
  }

  /// 创建带有更新字段的新消息实例
  Message copyWith({
    String? id,
    String? content,
    DateTime? timestamp,
    String? senderId,
    String? receiverId,
    String? chatId,
    MessageType? type,
    MessageStatus? status,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? this.id,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      senderId: senderId ?? this.senderId,
      receiverId: receiverId ?? this.receiverId,
      chatId: chatId ?? this.chatId,
      type: type ?? this.type,
      status: status ?? this.status,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  List<Object?> get props => [
        id,
        content,
        timestamp,
        senderId,
        receiverId,
        chatId,
        type,
        status,
        metadata,
      ];
} 