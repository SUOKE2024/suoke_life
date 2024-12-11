class Message {
  final String content;
  final String role;
  final DateTime timestamp;
  
  Message({
    required this.content,
    required this.role,
    required this.timestamp,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'content': content,
      'role': role,
      'timestamp': timestamp.toIso8601String(),
    };
  }
  
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      content: json['content'] as String,
      role: json['role'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
} 