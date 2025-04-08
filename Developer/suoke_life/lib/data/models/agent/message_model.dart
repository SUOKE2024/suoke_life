enum MessageRole {
  user,
  assistant,
  system,
}

class MessageModel {
  final String id;
  final String content;
  final dynamic role;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;
  final bool isPlaceholder;

  MessageModel({
    required this.id,
    required this.content,
    required this.role,
    required this.timestamp,
    this.metadata,
    this.isPlaceholder = false,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'],
      content: json['content'],
      role: json['role'],
      timestamp: DateTime.parse(json['timestamp']),
      metadata: json['metadata'],
      isPlaceholder: json['isPlaceholder'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'role': role,
      'timestamp': timestamp.toIso8601String(),
      'metadata': metadata,
      'isPlaceholder': isPlaceholder,
    };
  }

  MessageModel copyWith({
    String? id,
    String? content,
    dynamic role,
    DateTime? timestamp,
    Map<String, dynamic>? metadata,
    bool? isPlaceholder,
  }) {
    return MessageModel(
      id: id ?? this.id,
      content: content ?? this.content,
      role: role ?? this.role,
      timestamp: timestamp ?? this.timestamp,
      metadata: metadata ?? this.metadata,
      isPlaceholder: isPlaceholder ?? this.isPlaceholder,
    );
  }
} 