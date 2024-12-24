
class ChatMessage {
  final String id;
  final int conversationId;
  final String content;
  final String type;
  final String senderId;
  final String senderAvatar;
  final DateTime createdAt;
  final bool isRead;

  // 常量定义
  static const String typeText = 'text';
  static const String typeVoice = 'voice';
  static const String typeFile = 'file';
  static const String typeSystem = 'system';

  static const String senderUser = 'user';
  static const String senderAi = 'ai';
  static const String senderSystem = 'system';

  ChatMessage({
    required this.id,
    required this.conversationId,
    required this.content,
    required this.type,
    required this.senderId,
    required this.senderAvatar,
    required this.createdAt,
    this.isRead = false,
  });

  // 便捷方法
  bool get isTextMessage => type == typeText;
  bool get isVoiceMessage => type == typeVoice;
  bool get isFileMessage => type == typeFile;
  bool get isSystemMessage => type == typeSystem;

  bool get isFromUser => senderId == senderUser;
  bool get isFromAi => senderId == senderAi;
  bool get isFromSystem => senderId == senderSystem;

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
    };
  }

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
    );
  }
} 