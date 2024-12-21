import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseProvider {
  static Database? _database;
  
  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final path = await getDatabasesPath();
    final dbPath = join(path, 'suoke_life.db');

    return await openDatabase(
      dbPath,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE records (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            tags TEXT,
            attachments TEXT
          )
        ''');

        await db.execute('''
          CREATE TABLE tags (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            created_at TEXT NOT NULL
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
    final db = await database;
    return await db.query(
      table,
      where: where,
      whereArgs: whereArgs,
      orderBy: orderBy,
      limit: limit,
    );
  }

  Future<Map<String, dynamic>> queryOne(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final results = await query(
      table,
      where: where,
      whereArgs: whereArgs,
      limit: 1,
    );
    if (results.isEmpty) {
      throw Exception('Record not found');
    }
    return results.first;
  }

  Future<void> insert(String table, Map<String, dynamic> data) async {
    final db = await database;
    await db.insert(table, data);
  }

  Future<void> update(
    String table,
    Map<String, dynamic> data, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final db = await database;
    await db.update(
      table,
      data,
      where: where,
      whereArgs: whereArgs,
    );
  }

  Future<void> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final db = await database;
    await db.delete(
      table,
      where: where,
      whereArgs: whereArgs,
    );
  }
} 