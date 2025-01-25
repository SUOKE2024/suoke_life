import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_life_app_app_app/app/core/database/database_service.dart';

class DatabaseHelper {
  static Future<Database> _initDatabase() async {
    return await databaseFactoryFfi.openDatabase(
      inMemoryDatabasePath,
      options: OpenDatabaseOptions(
        version: 1,
        onCreate: (db, version) async {
          await db.execute('''
            CREATE TABLE messages (
              id TEXT PRIMARY KEY,
              content TEXT,
              sender_id TEXT,
              timestamp INTEGER,
              is_read INTEGER DEFAULT 0
            )
          ''');

          await db.execute('''
            CREATE TABLE chat_sessions (
              id TEXT PRIMARY KEY,
              participant_ids TEXT,
              last_message TEXT,
              last_message_time INTEGER,
              unread_count INTEGER DEFAULT 0
            )
          ''');

          await db.execute('''
            CREATE TABLE message_history (
              id TEXT PRIMARY KEY,
              session_id TEXT,
              role TEXT,
              content TEXT,
              timestamp INTEGER,
              FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
          ''');
        },
      ),
    );
  }

  static Future<DatabaseService> getTestDatabase() async {
    final db = await _initDatabase();
    return DatabaseService(db);
  }
  
  static Future<void> closeDatabase(Database db) async {
    await db.close();
  }

  static Future<void> cleanDatabase(Database db) async {
    final tables = ['messages', 'chat_sessions', 'message_history'];
    
    for (final table in tables) {
      final exists = await db.query(
        'sqlite_master',
        where: 'type = ? AND name = ?',
        whereArgs: ['table', table],
      );
      
      if (exists.isNotEmpty) {
        await db.execute('DELETE FROM $table');
      }
    }
  }
} 