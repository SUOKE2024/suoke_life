enum SessionStatus {
  active,
  paused,
  ended,
  error,
}

class AISession {
  final String id;
  final String userId;
  final String assistantName;
  final AIModel model;
  final SessionStatus status;
  final Map<String, dynamic>? metadata;

  const AISession({
    required this.id,
    required this.userId,
    required this.assistantName,
    required this.model,
    this.status = SessionStatus.active,
    this.metadata,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'assistant_name': assistantName,
    'model': model.toMap(),
    'status': status.toString(),
    'metadata': metadata,
  };

  factory AISession.fromMap(Map<String, dynamic> map) => AISession(
    id: map['id'],
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    model: AIModel.fromMap(map['model']),
    status: SessionStatus.values.firstWhere(
      (e) => e.toString() == map['status'],
      orElse: () => SessionStatus.active,
    ),
    metadata: map['metadata'],
  );

  AISession copyWith({
    AIModel? model,
    SessionStatus? status,
    Map<String, dynamic>? metadata,
  }) => AISession(
    id: id,
    userId: userId,
    assistantName: assistantName,
    model: model ?? this.model,
    status: status ?? this.status,
    metadata: metadata ?? this.metadata,
  );
} 