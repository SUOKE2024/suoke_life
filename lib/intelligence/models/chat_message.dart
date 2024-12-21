enum MessageRole {
  user,
  assistant,
  system,
  error
}

class ChatMessage {
  final String content;
  final MessageRole role;
  final DateTime timestamp;
  final String? userId;
  final String? assistantName;
  final Map<String, dynamic>? metadata;

  ChatMessage({
    required this.content,
    required this.role,
    DateTime? timestamp,
    this.userId,
    this.assistantName,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'content': content,
      'role': role.toString(),
      'timestamp': timestamp.toIso8601String(),
      'userId': userId,
      'assistantName': assistantName,
      'metadata': metadata,
    };
  }

  factory ChatMessage.fromMap(Map<String, dynamic> map) {
    return ChatMessage(
      content: map['content'],
      role: MessageRole.values.firstWhere(
        (e) => e.toString() == map['role'],
        orElse: () => MessageRole.user,
      ),
      timestamp: DateTime.parse(map['timestamp']),
      userId: map['userId'],
      assistantName: map['assistantName'],
      metadata: map['metadata'],
    );
  }

  ChatMessage copyWith({
    String? content,
    MessageRole? role,
    DateTime? timestamp,
    String? userId,
    String? assistantName,
    Map<String, dynamic>? metadata,
  }) {
    return ChatMessage(
      content: content ?? this.content,
      role: role ?? this.role,
      timestamp: timestamp ?? this.timestamp,
      userId: userId ?? this.userId,
      assistantName: assistantName ?? this.assistantName,
      metadata: metadata ?? this.metadata,
    );
  }
} 