enum FeedbackType {
  helpful,
  notHelpful,
  inappropriate,
  bugReport,
  suggestion,
  other,
}

enum FeedbackPriority {
  low,
  medium,
  high,
  urgent,
}

class AIFeedback {
  final String id;
  final String userId;
  final String assistantName;
  final FeedbackType type;
  final String content;
  final int rating;
  final DateTime timestamp;
  final String? sessionId;
  final String? messageId;
  final FeedbackPriority priority;
  final Map<String, dynamic>? metadata;

  const AIFeedback({
    required this.id,
    required this.userId,
    required this.assistantName,
    required this.type,
    required this.content,
    required this.rating,
    DateTime? timestamp,
    this.sessionId,
    this.messageId,
    this.priority = FeedbackPriority.medium,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'assistant_name': assistantName,
    'type': type.toString(),
    'content': content,
    'rating': rating,
    'timestamp': timestamp.toIso8601String(),
    'session_id': sessionId,
    'message_id': messageId,
    'priority': priority.toString(),
    'metadata': metadata,
  };

  factory AIFeedback.fromMap(Map<String, dynamic> map) => AIFeedback(
    id: map['id'],
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    type: FeedbackType.values.firstWhere(
      (e) => e.toString() == map['type'],
      orElse: () => FeedbackType.other,
    ),
    content: map['content'],
    rating: map['rating'],
    timestamp: DateTime.parse(map['timestamp']),
    sessionId: map['session_id'],
    messageId: map['message_id'],
    priority: FeedbackPriority.values.firstWhere(
      (e) => e.toString() == map['priority'],
      orElse: () => FeedbackPriority.medium,
    ),
    metadata: map['metadata'] != null ? 
      Map<String, dynamic>.from(map['metadata']) : null,
  );

  AIFeedback copyWith({
    String? id,
    String? userId,
    String? assistantName,
    FeedbackType? type,
    String? content,
    int? rating,
    DateTime? timestamp,
    String? sessionId,
    String? messageId,
    FeedbackPriority? priority,
    Map<String, dynamic>? metadata,
  }) => AIFeedback(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    assistantName: assistantName ?? this.assistantName,
    type: type ?? this.type,
    content: content ?? this.content,
    rating: rating ?? this.rating,
    timestamp: timestamp ?? this.timestamp,
    sessionId: sessionId ?? this.sessionId,
    messageId: messageId ?? this.messageId,
    priority: priority ?? this.priority,
    metadata: metadata ?? this.metadata,
  );
} 