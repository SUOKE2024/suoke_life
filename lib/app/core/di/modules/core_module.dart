import 'package:injectable/injectable.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

@module
abstract class CoreModule {
  @singleton
  Future<Database> get database async {
    return openDatabase(
      join(await getDatabasesPath(), 'suoke.db'),
      version: 1,
      onCreate: (Database db, int version) async {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0
          )
        ''');
        
        await db.execute('''
          CREATE TABLE IF NOT EXISTS chat_info (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            last_message TEXT,
            last_message_time INTEGER
          )
        ''');
        
        await db.execute('''
          CREATE TABLE IF NOT EXISTS life_records (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at INTEGER NOT NULL
          )
        ''');
      },
    );
  }
} 