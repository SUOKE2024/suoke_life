import 'package:logger/logger.dart';
import '../../models/chat_history.dart';
import 'base_dao_impl.dart';
import 'chat_history_dao.dart';

/// 聊天历史数据访问对象实现
class ChatHistoryDaoImpl extends BaseDaoImpl<ChatHistory> implements ChatHistoryDao {
  final Logger _logger = Logger();

  @override
  String get tableName => ChatHistory.tableName;

  @override
  ChatHistory fromMap(Map<String, dynamic> map) => ChatHistory.fromMap(map);

  @override
  Map<String, dynamic> toMap(ChatHistory entity) => entity.toMap();

  @override
  Future<List<ChatHistory>> findBySessionId(String sessionId) async {
    try {
      return await findWhere(
        where: 'session_id = ?',
        whereArgs: [sessionId],
        orderBy: 'timestamp ASC',
      );
    } catch (e) {
      _logger.e('Error finding chat history by session ID: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> findByTimeRange(int startTime, int endTime) async {
    try {
      return await findWhere(
        where: 'timestamp BETWEEN ? AND ?',
        whereArgs: [startTime, endTime],
        orderBy: 'timestamp ASC',
      );
    } catch (e) {
      _logger.e('Error finding chat history by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> findRecent(int limit) async {
    try {
      return await findWhere(
        orderBy: 'timestamp DESC',
        limit: limit,
      );
    } catch (e) {
      _logger.e('Error finding recent chat history: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllSessionIds() async {
    try {
      final db = await getDatabase();
      final List<Map<String, dynamic>> maps = await db.query(
        tableName,
        distinct: true,
        columns: ['session_id'],
      );
      return maps.map((map) => map['session_id'] as String).toList();
    } catch (e) {
      _logger.e('Error getting all session IDs: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteBySessionId(String sessionId) async {
    try {
      final db = await getDatabase();
      await db.delete(
        tableName,
        where: 'session_id = ?',
        whereArgs: [sessionId],
      );
    } catch (e) {
      _logger.e('Error deleting chat history by session ID: $e');
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      final db = await getDatabase();
      await db.delete(tableName);
    } catch (e) {
      _logger.e('Error clearing chat history: $e');
      rethrow;
    }
  }

  @override
  Future<int> getSessionMessageCount(String sessionId) async {
    try {
      final db = await getDatabase();
      final result = await db.rawQuery(
        'SELECT COUNT(*) as count FROM $tableName WHERE session_id = ?',
        [sessionId],
      );
      return Sqflite.firstIntValue(result) ?? 0;
    } catch (e) {
      _logger.e('Error getting session message count: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> search(String keyword) async {
    try {
      return await findWhere(
        where: 'message LIKE ?',
        whereArgs: ['%$keyword%'],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error searching chat history: $e');
      rethrow;
    }
  }

  @override
  Future<List<ChatHistory>> findByMessageType(String messageType) async {
    try {
      return await findWhere(
        where: 'message_type = ?',
        whereArgs: [messageType],
        orderBy: 'timestamp DESC',
      );
    } catch (e) {
      _logger.e('Error finding chat history by message type: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveAll(List<ChatHistory> messages) async {
    try {
      final batch = (await getDatabase()).batch();
      
      for (var message in messages) {
        batch.insert(
          tableName,
          toMap(message),
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
      
      await batch.commit();
    } catch (e) {
      _logger.e('Error saving multiple chat messages: $e');
      rethrow;
    }
  }
} 