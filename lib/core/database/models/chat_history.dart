import '../base/entity.dart';

/// 聊天历史实体
class ChatHistory extends Entity {
  final int? id;
  final String message;
  final bool isUser;
  final int timestamp;
  final String sessionId;
  final String messageType;

  ChatHistory({
    this.id,
    required this.message,
    required this.isUser,
    required this.timestamp,
    required this.sessionId,
    required this.messageType,
  });

  @override
  int? get id => this.id;

  @override
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'message': message,
      'is_user': isUser ? 1 : 0,
      'timestamp': timestamp,
      'session_id': sessionId,
      'message_type': messageType,
    };
  }

  factory ChatHistory.fromMap(Map<String, dynamic> map) {
    return ChatHistory(
      id: map['id'] as int?,
      message: map['message'] as String,
      isUser: map['is_user'] == 1,
      timestamp: map['timestamp'] as int,
      sessionId: map['session_id'] as String,
      messageType: map['message_type'] as String,
    );
  }

  static String get tableName => 'chat_history';

  static String get createTableSql => '''
    CREATE TABLE IF NOT EXISTS chat_history(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      message TEXT,
      is_user INTEGER,
      timestamp INTEGER,
      session_id TEXT,
      message_type TEXT
    )
  ''';

  static List<String> get createIndexSql => [
    'CREATE INDEX idx_chat_history_session ON chat_history(session_id)',
  ];

  ChatHistory copyWith({
    int? id,
    String? message,
    bool? isUser,
    int? timestamp,
    String? sessionId,
    String? messageType,
  }) {
    return ChatHistory(
      id: id ?? this.id,
      message: message ?? this.message,
      isUser: isUser ?? this.isUser,
      timestamp: timestamp ?? this.timestamp,
      sessionId: sessionId ?? this.sessionId,
      messageType: messageType ?? this.messageType,
    );
  }

  @override
  String toString() {
    return 'ChatHistory(id: $id, message: $message, isUser: $isUser, timestamp: $timestamp, sessionId: $sessionId, messageType: $messageType)';
  }
} 