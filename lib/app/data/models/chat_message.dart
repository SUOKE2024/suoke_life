import 'package:flutter/foundation.dart';

/// 消息角色枚举
enum MessageRole {
  user,     // 用户
  assistant, // AI助手
  system    // 系统
}

/// 消息类型枚举
enum MessageType {
  text,
  image,
  voice,
  file,
}

/// 聊天消息模型
class ChatMessage {
  static const String userSenderId = 'user';
  static const String assistantSenderId = 'assistant';

  final String id;
  final String roomId;
  final String content;
  final String type;
  final String senderId;
  final String? senderAvatar;
  final DateTime timestamp;
  final String? senderType;

  bool get isFromUser => senderId == userSenderId;

  ChatMessage({
    required this.id,
    required this.roomId,
    required this.content,
    required this.type,
    required this.senderId,
    this.senderAvatar,
    required this.timestamp,
    this.senderType,
  });

  factory ChatMessage.fromMap(Map<String, dynamic> map) {
    return ChatMessage(
      id: map['id'] as String,
      roomId: map['room_id'] as String,
      content: map['content'] as String,
      type: map['type'] as String,
      senderId: map['sender_id'] as String,
      senderAvatar: map['sender_avatar'] as String?,
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] as int),
      senderType: map['sender_type'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'room_id': roomId,
      'content': content,
      'type': type,
      'sender_id': senderId,
      'sender_avatar': senderAvatar,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'sender_type': senderType,
    };
  }
} 