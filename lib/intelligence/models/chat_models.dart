enum MessageType {
  user,
  assistant,
  system,
}

enum ExportFormat {
  json,
  csv,
}

class ChatMessage {
  final String id;
  final String userId;
  final String assistantName;
  final String sessionId;
  final String content;
  final MessageType type;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  const ChatMessage({
    required this.id,
    required this.userId,
    required this.assistantName,
    required this.sessionId,
    required this.content,
    required this.type,
    DateTime? timestamp,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'assistant_name': assistantName,
    'session_id': sessionId,
    'content': content,
    'type': type.toString(),
    'timestamp': timestamp.toIso8601String(),
    'metadata': metadata,
  };

  factory ChatMessage.fromMap(Map<String, dynamic> map) => ChatMessage(
    id: map['id'],
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    sessionId: map['session_id'],
    content: map['content'],
    type: MessageType.values.firstWhere(
      (e) => e.toString() == map['type'],
      orElse: () => MessageType.user,
    ),
    timestamp: DateTime.parse(map['timestamp']),
    metadata: map['metadata'],
  );

  ChatMessage copyWith({
    String? content,
    Map<String, dynamic>? metadata,
  }) => ChatMessage(
    id: id,
    userId: userId,
    assistantName: assistantName,
    sessionId: sessionId,
    content: content ?? this.content,
    type: type,
    timestamp: timestamp,
    metadata: metadata ?? this.metadata,
  );
} 