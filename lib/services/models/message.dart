class Message {
  final String id;
  final String content;
  final String role;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  Message({
    String? id,
    required this.content,
    required this.role,
    DateTime? timestamp,
    this.metadata,
  })  : id = id ?? DateTime.now().millisecondsSinceEpoch.toString(),
        timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'role': role,
      'timestamp': timestamp.toIso8601String(),
      if (metadata != null) 'metadata': metadata,
    };
  }

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] as String,
      content: json['content'] as String,
      role: json['role'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Message copyWith({
    String? content,
    String? role,
    DateTime? timestamp,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id,
      content: content ?? this.content,
      role: role ?? this.role,
      timestamp: timestamp ?? this.timestamp,
      metadata: metadata ?? this.metadata,
    );
  }
} 