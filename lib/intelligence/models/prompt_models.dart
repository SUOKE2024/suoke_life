enum PromptType {
  basic,      // 基础提示词
  template,   // 模板提示词
  advanced,   // 高级提示词
  conditional,// 条件提示词
  dynamic,    // 动态提示词
  public,     // 公共提示词
}

class AIPrompt {
  final String id;
  final String name;
  final String content;
  final PromptType type;
  final String assistantName;
  final String userId;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  const AIPrompt({
    required this.id,
    required this.name,
    required this.content,
    required this.type,
    required this.assistantName,
    required this.userId,
    DateTime? createdAt,
    this.updatedAt,
    this.metadata,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'name': name,
    'content': content,
    'type': type.toString(),
    'assistant_name': assistantName,
    'user_id': userId,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt?.toIso8601String(),
    'metadata': metadata,
  };

  factory AIPrompt.fromMap(Map<String, dynamic> map) => AIPrompt(
    id: map['id'],
    name: map['name'],
    content: map['content'],
    type: PromptType.values.firstWhere(
      (e) => e.toString() == map['type'],
      orElse: () => PromptType.basic,
    ),
    assistantName: map['assistant_name'],
    userId: map['user_id'],
    createdAt: DateTime.parse(map['created_at']),
    updatedAt: map['updated_at'] != null ? 
      DateTime.parse(map['updated_at']) : null,
    metadata: map['metadata'],
  );

  AIPrompt copyWith({
    String? name,
    String? content,
    PromptType? type,
    String? assistantName,
    Map<String, dynamic>? metadata,
  }) => AIPrompt(
    id: id,
    name: name ?? this.name,
    content: content ?? this.content,
    type: type ?? this.type,
    assistantName: assistantName ?? this.assistantName,
    userId: userId,
    createdAt: createdAt,
    updatedAt: DateTime.now(),
    metadata: metadata ?? this.metadata,
  );
} 