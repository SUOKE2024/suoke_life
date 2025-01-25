import 'package:injectable/injectable.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;

@singleton
class DatabaseProvider {
  late Database _db;
  
  Future<void> init([String? dbName]) async {
    final dbPath = await getDatabasesPath();
    final pathToDb = p.join(dbPath, dbName ?? 'chat.db');
    
    _db = await openDatabase(
      pathToDb,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            last_message TEXT,
            last_message_time TEXT
          )
        ''');
        
        await db.execute('''
          CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            content TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            synced INTEGER DEFAULT 0,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
          )
        ''');
      },
    );
  }

  Future<List<Map<String, dynamic>>> query(
    String table, {
    String? where,
    List<Object?>? whereArgs,
    String? orderBy,
    int? limit,
  }) async {
    return _db.query(
      table,
      where: where,
      whereArgs: whereArgs,
      orderBy: orderBy,
      limit: limit,
    );
  }

  Future<int> insert(String table, Map<String, dynamic> data) async {
    return _db.insert(table, data);
  }

  Future<int> update(
    String table,
    Map<String, dynamic> data, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    return _db.update(table, data, where: where, whereArgs: whereArgs);
  }

  Future<T> transaction<T>(Future<T> Function(Transaction txn) action) async {
    return _db.transaction(action);
  }

  Future<void> close() async {
    await _db.close();
  }

  String get path => _db.path;
} 