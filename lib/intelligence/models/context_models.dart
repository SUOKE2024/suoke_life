class AIContext {
  final String userId;
  final String assistantName;
  final List<String> history;
  final Map<String, dynamic>? metadata;

  const AIContext({
    required this.userId,
    required this.assistantName,
    required this.history,
    this.metadata,
  });

  Map<String, dynamic> toMap() => {
    'user_id': userId,
    'assistant_name': assistantName,
    'history': history,
    'metadata': metadata,
  };

  factory AIContext.fromMap(Map<String, dynamic> map) => AIContext(
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    history: List<String>.from(map['history']),
    metadata: map['metadata'],
  );

  AIContext copyWith({
    List<String>? history,
    Map<String, dynamic>? metadata,
  }) => AIContext(
    userId: userId,
    assistantName: assistantName,
    history: history ?? this.history,
    metadata: metadata ?? this.metadata,
  );
} 