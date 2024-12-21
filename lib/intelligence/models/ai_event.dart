enum AIEventType {
  sessionStart,
  sessionEnd,
  message,
  error,
  modelSwitch,
  featureUsage,
  subscriptionChange,
  userFeedback,
}

class AIEvent {
  final String id;
  final String userId;
  final String assistantName;
  final AIEventType type;
  final Map<String, dynamic> data;
  final DateTime timestamp;
  final String? sessionId;
  final Map<String, dynamic>? metadata;

  const AIEvent({
    required this.id,
    required this.userId,
    required this.assistantName,
    required this.type,
    required this.data,
    DateTime? timestamp,
    this.sessionId,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'assistant_name': assistantName,
    'type': type.toString(),
    'data': data,
    'timestamp': timestamp.toIso8601String(),
    'session_id': sessionId,
    'metadata': metadata,
  };

  factory AIEvent.fromMap(Map<String, dynamic> map) => AIEvent(
    id: map['id'],
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    type: AIEventType.values.firstWhere(
      (e) => e.toString() == map['type'],
      orElse: () => AIEventType.message,
    ),
    data: Map<String, dynamic>.from(map['data']),
    timestamp: DateTime.parse(map['timestamp']),
    sessionId: map['session_id'],
    metadata: map['metadata'] != null ? 
      Map<String, dynamic>.from(map['metadata']) : null,
  );

  AIEvent copyWith({
    String? id,
    String? userId,
    String? assistantName,
    AIEventType? type,
    Map<String, dynamic>? data,
    DateTime? timestamp,
    String? sessionId,
    Map<String, dynamic>? metadata,
  }) => AIEvent(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    assistantName: assistantName ?? this.assistantName,
    type: type ?? this.type,
    data: data ?? this.data,
    timestamp: timestamp ?? this.timestamp,
    sessionId: sessionId ?? this.sessionId,
    metadata: metadata ?? this.metadata,
  );
} 