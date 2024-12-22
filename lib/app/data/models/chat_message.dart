import 'package:json_annotation/json_annotation.dart';

class ChatMessage {
  final String id;
  final int conversationId;
  final String content;
  final String type;
  final String senderId;
  final String senderAvatar;
  final DateTime createdAt;
  final bool isRead;
  final int? duration;  // 语音消息的时长

  ChatMessage({
    required this.id,
    required this.conversationId,
    required this.content,
    required this.type,
    required this.senderId,
    required this.senderAvatar,
    required this.createdAt,
    required this.isRead,
    this.duration,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      conversationId: json['conversation_id'],
      content: json['content'],
      type: json['type'],
      senderId: json['sender_id'],
      senderAvatar: json['sender_avatar'],
      createdAt: DateTime.parse(json['created_at']),
      isRead: json['is_read'] == 1,
      duration: json['duration'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'conversation_id': conversationId,
      'content': content,
      'type': type,
      'sender_id': senderId,
      'sender_avatar': senderAvatar,
      'created_at': createdAt.toIso8601String(),
      'is_read': isRead ? 1 : 0,
      'duration': duration,
    };
  }

  // 消息类型常量
  static const String typeText = 'text';
  static const String typeImage = 'image';
  static const String typeVoice = 'voice';
  static const String typeFile = 'file';
  static const String typeSystem = 'system';

  // 发送者类型常量
  static const String senderUser = 'user';
  static const String senderAi = 'ai';
  static const String senderSystem = 'system';

  // 判断消息类型的便捷方法
  bool get isText => type == typeText;
  bool get isImage => type == typeImage;
  bool get isVoice => type == typeVoice;
  bool get isFile => type == typeFile;
  bool get isSystem => type == typeSystem;

  // 判断发送者的便捷方法
  bool get isFromUser => senderId == senderUser;
  bool get isFromAi => senderId == senderAi;
  bool get isFromSystem => senderId == senderSystem;
} 