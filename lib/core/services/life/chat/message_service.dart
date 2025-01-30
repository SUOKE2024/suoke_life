import '../models/message.dart';
import '../../../core/database/database_service.dart';

class MessageService {
  final DatabaseService _db;

  MessageService(this._db);

  Future<void> _ensureTableExists() async {
    final tables = await _db.query(
      'SELECT name FROM sqlite_master WHERE type = ? AND name = ?',
      ['table', 'messages'],
    );
    
    if (tables.isEmpty) {
      await _db.execute('''
        CREATE TABLE messages (
          id TEXT PRIMARY KEY,
          content TEXT,
          sender_id TEXT,
          timestamp INTEGER,
          is_read INTEGER DEFAULT 0
        )
      ''');
    }
  }

  Future<void> saveMessage(Message message) async {
    await _ensureTableExists();
    await _db.insert('messages', message.toMap());
  }

  Future<Message?> getMessage(String id) async {
    await _ensureTableExists();
    final results = await _db.query(
      'SELECT * FROM messages WHERE id = ?',
      [id],
    );
    
    if (results.isEmpty) return null;
    return Message.fromMap(results.first);
  }

  Future<void> markAsRead(String id) async {
    await _db.update(
      'messages',
      {'is_read': 1},
      'id = ?',
      [id],
    );
  }

  Future<int> getUnreadCount(String senderId) async {
    final results = await _db.query(
      'SELECT COUNT(*) as count FROM messages WHERE sender_id = ? AND is_read = 0',
      [senderId],
    );
    return results.first['count'] as int;
  }

  Future<List<Message>> getMessagesBySender(String senderId) async {
    final results = await _db.query(
      'SELECT * FROM messages WHERE sender_id = ? ORDER BY timestamp DESC',
      [senderId],
    );
    return results.map((map) => Message.fromMap(map)).toList();
  }
} 