class Message {
  final String content;
  final String role;
  final DateTime timestamp;
  final Map<String, dynamic>? context;
  final Map<String, dynamic>? metadata;
  final dynamic voiceData;

  Message({
    required this.content,
    required this.role,
    DateTime? timestamp,
    this.context,
    this.metadata,
    this.voiceData,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() => {
    'content': content,
    'role': role,
    'timestamp': timestamp.toIso8601String(),
    'context': context,
    'metadata': metadata,
    'voiceData': voiceData,
  };

  factory Message.fromJson(Map<String, dynamic> json) => Message(
    content: json['content'] as String,
    role: json['role'] as String,
    timestamp: DateTime.parse(json['timestamp'] as String),
    context: json['context'] as Map<String, dynamic>?,
    metadata: json['metadata'] as Map<String, dynamic>?,
    voiceData: json['voiceData'],
  );

  Message copyWith({
    String? content,
    String? role,
    DateTime? timestamp,
    Map<String, dynamic>? context,
    Map<String, dynamic>? metadata,
    dynamic voiceData,
  }) => Message(
    content: content ?? this.content,
    role: role ?? this.role,
    timestamp: timestamp ?? this.timestamp,
    context: context ?? this.context,
    metadata: metadata ?? this.metadata,
    voiceData: voiceData ?? this.voiceData,
  );
} 