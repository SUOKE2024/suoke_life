enum LogLevel {
  trace,
  debug,
  info,
  warning,
  error,
  critical,
}

class AILogEntry {
  final String id;
  final String userId;
  final String assistantName;
  final String message;
  final LogLevel level;
  final DateTime timestamp;
  final String? sessionId;
  final Map<String, dynamic>? metadata;

  const AILogEntry({
    required this.id,
    required this.userId,
    required this.assistantName,
    required this.message,
    required this.level,
    required this.timestamp,
    this.sessionId,
    this.metadata,
  });

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'assistant_name': assistantName,
    'message': message,
    'level': level.toString(),
    'timestamp': timestamp.toIso8601String(),
    'session_id': sessionId,
    'metadata': metadata,
  };

  factory AILogEntry.fromMap(Map<String, dynamic> map) => AILogEntry(
    id: map['id'],
    userId: map['user_id'],
    assistantName: map['assistant_name'],
    message: map['message'],
    level: LogLevel.values.firstWhere(
      (e) => e.toString() == map['level'],
      orElse: () => LogLevel.info,
    ),
    timestamp: DateTime.parse(map['timestamp']),
    sessionId: map['session_id'],
    metadata: map['metadata'] != null ? 
      Map<String, dynamic>.from(map['metadata']) : null,
  );
} 