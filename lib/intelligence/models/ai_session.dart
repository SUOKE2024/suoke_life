class AISession {
  final String id;
  final String userId;
  final String assistantName;
  final DateTime startTime;
  final AIModel model;
  final SubscriptionFeatures features;
  
  const AISession({
    required this.id,
    required this.userId,
    required this.assistantName,
    required this.startTime,
    required this.model,
    required this.features,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'assistant_name': assistantName,
    'start_time': startTime.toIso8601String(),
    'model': model.toMap(),
    'features': features.toMap(),
  };

  factory AISession.fromMap(Map<String, dynamic> map) => AISession(
    id: map['id'],
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    startTime: DateTime.parse(map['start_time']),
    model: AIModel.fromMap(map['model']),
    features: SubscriptionFeatures.fromMap(map['features']),
  );
} 