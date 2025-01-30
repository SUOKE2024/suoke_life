class AIResponse {
  final String content;
  final String aiType;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  AIResponse({
    required this.content,
    required this.aiType,
    required this.timestamp,
    this.metadata,
  });

  Map<String, dynamic> toMap() {
    return {
      'content': content,
      'ai_type': aiType,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'metadata': metadata,
    };
  }

  factory AIResponse.fromMap(Map<String, dynamic> map) {
    return AIResponse(
      content: map['content'],
      aiType: map['ai_type'],
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp']),
      metadata: map['metadata'],
    );
  }
} 