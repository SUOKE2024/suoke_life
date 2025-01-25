import '../../../core/database/database_service.dart';
import '../models/message.dart';

class MessageHistoryService {
  final DatabaseService _db;

  MessageHistoryService(this._db);

  Future<void> _ensureTableExists() async {
    final tables = await _db.query(
      'SELECT name FROM sqlite_master WHERE type = ? AND name = ?',
      ['table', 'message_history'],
    );
    
    if (tables.isEmpty) {
      await _db.execute('''
        CREATE TABLE message_history (
          id TEXT PRIMARY KEY,
          session_id TEXT,
          role TEXT,
          content TEXT,
          timestamp INTEGER,
          FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
      ''');
    }
  }

  Future<List<Message>> getMessageHistory(String sessionId, {int page = 1, int pageSize = 20}) async {
    await _ensureTableExists();
    final offset = (page - 1) * pageSize;
    final results = await _db.query(
      '''
      SELECT 
        id,
        content,
        role as sender_id,
        timestamp,
        1 as is_read
      FROM message_history 
      WHERE session_id = ? 
      ORDER BY timestamp DESC 
      LIMIT ? OFFSET ?
      ''',
      [sessionId, pageSize, offset],
    );
    return results.map((map) => Message.fromMap(map)).toList();
  }

  Future<int> getTotalMessages(String sessionId) async {
    await _ensureTableExists();
    final result = await _db.query(
      'SELECT COUNT(*) as count FROM message_history WHERE session_id = ?',
      [sessionId],
    );
    return result.first['count'] as int;
  }

  Future<void> saveMessage(Message message, String sessionId, String role) async {
    await _ensureTableExists();
    await _db.insert('message_history', {
      'id': message.id,
      'session_id': sessionId,
      'role': role,
      'content': message.content,
      'timestamp': message.timestamp.millisecondsSinceEpoch,
    });
  }

  Future<void> deleteSessionHistory(String sessionId) async {
    await _ensureTableExists();
    await _db.delete(
      'message_history',
      'session_id = ?',
      [sessionId],
    );
  }
} 