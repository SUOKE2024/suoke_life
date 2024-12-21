class AIModel {
  final String id;
  final String version;
  final String type;
  final int maxTokens;
  final bool priority;
  final Map<String, dynamic>? config;

  const AIModel({
    required this.id,
    required this.version,
    required this.type,
    required this.maxTokens,
    this.priority = false,
    this.config,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'version': version,
    'type': type,
    'max_tokens': maxTokens,
    'priority': priority,
    'config': config,
  };

  factory AIModel.fromMap(Map<String, dynamic> map) => AIModel(
    id: map['id'],
    version: map['version'],
    type: map['type'],
    maxTokens: map['max_tokens'],
    priority: map['priority'] ?? false,
    config: map['config'],
  );

  AIModel copyWith({
    String? id,
    String? version,
    String? type,
    int? maxTokens,
    bool? priority,
    Map<String, dynamic>? config,
  }) => AIModel(
    id: id ?? this.id,
    version: version ?? this.version,
    type: type ?? this.type,
    maxTokens: maxTokens ?? this.maxTokens,
    priority: priority ?? this.priority,
    config: config ?? this.config,
  );
} 