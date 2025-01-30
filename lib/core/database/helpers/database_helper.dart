import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:async';

class DatabaseHelper {
  static Database? _database;
  static const String dbName = 'suoke.db';

  Future<Database> get database async {
    _database ??= await initDatabase();
    return _database!;
  }

  Future<Database> initDatabase() async {
    final path = join(await getDatabasesPath(), dbName);
    return openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await _createTables(db);
      },
      onUpgrade: (db, oldVersion, newVersion) async {
        // Handle database upgrade
      },
    );
  }

  Future<void> _createTables(Database db) async {
    try {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY,
          room_id TEXT NOT NULL,
          content TEXT NOT NULL,
          type TEXT NOT NULL,
          sender_id TEXT NOT NULL,
          timestamp INTEGER NOT NULL
        )
      ''');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id);');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          avatar TEXT NOT NULL,
          role TEXT,
          settings TEXT
        )
      ''');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS life_records (
          id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          title TEXT NOT NULL,
          content TEXT,
          type TEXT NOT NULL,
          created_at INTEGER NOT NULL,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      ''');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_life_records_user_id ON life_records(user_id);');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS health_advices (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          type TEXT NOT NULL,
          created_at INTEGER NOT NULL
        )
      ''');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_health_advices_title ON health_advices(title);');
    } catch (e) {
      print('Error creating tables: $e');
    }
  }

  Future<int> insert(String table, Map<String, dynamic> data) async {
    try {
      final db = await database;
      return await db.insert(table, data);
    } catch (e) {
      print('Error inserting into $table: $e');
      return -1;
    }
  }

  Future<List<Map<String, dynamic>>> query(
    String table, {
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
    int? limit,
  }) async {
    try {
      final db = await database;
      return await db.query(
        table,
        where: where,
        whereArgs: whereArgs,
        orderBy: orderBy,
        limit: limit,
      );
    } catch (e) {
      print('Error querying $table: $e');
      return [];
    }
  }

  Future<int> update(
    String table,
    Map<String, dynamic> data, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    try {
      final db = await database;
      return await db.update(
        table,
        data,
        where: where,
        whereArgs: whereArgs,
      );
    } catch (e) {
      print('Error updating $table: $e');
      return -1;
    }
  }

  Future<int> delete(
    String table, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    try {
      final db = await database;
      return await db.delete(
        table,
        where: where,
        whereArgs: whereArgs,
      );
    } catch (e) {
      print('Error deleting from $table: $e');
      return -1;
    }
  }
} 