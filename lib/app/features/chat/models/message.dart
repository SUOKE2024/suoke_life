class Message {
  final String id;
  final String content;
  final String senderId;
  final DateTime timestamp;
  final bool isRead;

  Message({
    required this.id,
    required this.content,
    required this.senderId,
    required this.timestamp,
    required this.isRead,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'content': content,
      'sender_id': senderId,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'is_read': isRead ? 1 : 0,
    };
  }

  factory Message.fromMap(Map<String, dynamic> map) {
    return Message(
      id: map['id'] as String,
      content: map['content'] as String,
      senderId: map['sender_id'] as String,
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] as int),
      isRead: (map['is_read'] as int) == 1,
    );
  }
} 