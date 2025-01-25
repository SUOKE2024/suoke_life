import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/database/database_config.dart';

class LocalStorageServiceImpl implements LocalStorageService {
  Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB();
    return _database!;
  }

  Future<Database> _initDB() async {
    final path = await DatabaseConfig.getDatabasePath();
    return await openDatabase(
      path,
      version: DatabaseConfig.databaseVersion,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        isUser INTEGER
      )
    ''');
  }

  Future<void> saveChat(String text, bool isUser) async {
    final db = await database;
    await db.insert('chats', {
      'text': text,
      'isUser': isUser ? 1 : 0,
    });
  }

  Future<List<Map<String, dynamic>>> getChatList() async {
    final db = await database;
    return await db.query('chats');
  }

  Future<void> clearChatHistory() async {
    final db = await database;
    await db.delete('chats');
  }

  Future<List<Map<String, dynamic>>> query(String table, {String? where, List<dynamic>? whereArgs}) async {
    final db = await database;
    return await db.query(table, where: where, whereArgs: whereArgs);
  }

  Future<int> insert(String table, Map<String, dynamic> values) async {
    final db = await database;
    return await db.insert(table, values);
  }

  Future<int> update(String table, Map<String, dynamic> values, {String? where, List<dynamic>? whereArgs}) async {
    final db = await database;
    return await db.update(table, values, where: where, whereArgs: whereArgs);
  }

  Future<int> delete(String table, {String? where, List<dynamic>? whereArgs}) async {
    final db = await database;
    return await db.delete(table, where: where, whereArgs: whereArgs);
  }
}

abstract class LocalStorageService {
  Future<Database> get database;
  Future<List<Map<String, dynamic>>> query(String table, {String? where, List<dynamic>? whereArgs});
  Future<int> insert(String table, Map<String, dynamic> values);
  Future<int> update(String table, Map<String, dynamic> values, {String? where, List<dynamic>? whereArgs});
  Future<int> delete(String table, {String? where, List<dynamic>? whereArgs});
  Future<void> saveChat(String text, bool isUser);
  Future<List<Map<String, dynamic>>> getChatList();
  Future<void> clearChatHistory();
} 