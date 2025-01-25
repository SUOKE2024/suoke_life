import '../models/chat_session.dart';
import '../../../core/database/database_service.dart';

class ChatSessionService {
  final DatabaseService _db;

  ChatSessionService(this._db);

  DatabaseService get database => _db;

  Future<void> _ensureTableExists() async {
    final tables = await _db.query(
      'SELECT name FROM sqlite_master WHERE type = ? AND name = ?',
      ['table', 'chat_sessions'],
    );
    
    if (tables.isEmpty) {
      await _db.execute('''
        CREATE TABLE chat_sessions (
          id TEXT PRIMARY KEY,
          participant_ids TEXT,
          last_message TEXT,
          last_message_time INTEGER,
          unread_count INTEGER DEFAULT 0
        )
      ''');
    }
  }

  Future<void> createSession(ChatSession session) async {
    await _ensureTableExists();
    await _db.insert('chat_sessions', session.toMap());
  }

  Future<ChatSession?> getSession(String id) async {
    await _ensureTableExists();
    final results = await _db.query(
      'SELECT * FROM chat_sessions WHERE id = ?',
      [id],
    );
    
    if (results.isEmpty) return null;
    return ChatSession.fromMap(results.first);
  }

  Future<void> updateLastMessage(String id, String message, DateTime time) async {
    await _db.update(
      'chat_sessions',
      {
        'last_message': message,
        'last_message_time': time.millisecondsSinceEpoch,
      },
      'id = ?',
      [id],
    );
  }

  Future<void> incrementUnreadCount(String id) async {
    await _db.execute(
      'UPDATE chat_sessions SET unread_count = unread_count + 1 WHERE id = ?',
      [id],
    );
  }

  Future<List<ChatSession>> getSessionsByParticipant(String userId) async {
    await _ensureTableExists();
    final results = await _db.query(
      'SELECT * FROM chat_sessions WHERE participant_ids LIKE ? ORDER BY last_message_time DESC',
      ['%$userId%'],
    );
    return results.map((map) => ChatSession.fromMap(map)).toList();
  }
} 