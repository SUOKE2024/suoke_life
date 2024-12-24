

class Message {
  final String id;
  final String chatId;
  final String senderId;
  final String? content;
  final String type; // text, image, video, audio, file
  final DateTime timestamp;
  final bool isRead;
  final Map<String, dynamic>? extra;

  Message({
    required this.id,
    required this.chatId,
    required this.senderId,
    this.content,
    required this.type,
    required this.timestamp,
    this.isRead = false,
    this.extra,
  });

  factory Message.fromJson(Map<String, dynamic> json) => _$MessageFromJson(json);
  Map<String, dynamic> toJson() => _$MessageToJson(this);

  Message copyWith({
    String? id,
    String? chatId,
    String? senderId,
    String? content,
    String? type,
    DateTime? timestamp,
    bool? isRead,
    Map<String, dynamic>? extra,
  }) {
    return Message(
      id: id ?? this.id,
      chatId: chatId ?? this.chatId,
      senderId: senderId ?? this.senderId,
      content: content ?? this.content,
      type: type ?? this.type,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      extra: extra ?? this.extra,
    );
  }
} 