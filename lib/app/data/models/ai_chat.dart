class AiChat {
  final String id;
  final String role;
  final String content;
  final DateTime time;

  AiChat({
    required this.id,
    required this.role,
    required this.content,
    required this.time,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'role': role,
    'content': content,
    'time': time.toIso8601String(),
  };

  factory AiChat.fromMap(Map<String, dynamic> map) => AiChat(
    id: map['id'],
    role: map['role'],
    content: map['content'],
    time: DateTime.parse(map['time']),
  );
} 