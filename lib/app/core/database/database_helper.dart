import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../constants/database_constants.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._();
  static Database? _database;

  DatabaseHelper._();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    if (databaseFactory == null) {
      throw StateError('Database factory not initialized');
    }
    
    final path = await getDatabasesPath();
    final dbPath = join(path, 'suoke.db');

    return await openDatabase(
      dbPath,
      version: 1,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute(DatabaseConstants.createTableSyncLogs);
    await db.execute(DatabaseConstants.createTableTags);
    await db.execute(DatabaseConstants.createTableSyncConfigs);
    await db.execute(DatabaseConstants.createTableAiChats);

    await db.execute('''
      CREATE TABLE IF NOT EXISTS test_table (
        id TEXT PRIMARY KEY,
        name TEXT
      )
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // 处理数据库升级
  }

  Future<void> insert(String table, Map<String, dynamic> data) async {
    final db = await database;
    await db.insert(
      table,
      data,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<Map<String, dynamic>?> get(String table, String id) async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      table,
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return maps.first;
  }

  Future<List<Map<String, dynamic>>> getAll(String table) async {
    final db = await database;
    return await db.query(table);
  }

  Future<int> update(String table, Map<String, dynamic> data, String id) async {
    final db = await database;
    return await db.update(
      table,
      data,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> delete(String table, String id) async {
    final db = await database;
    return await db.delete(
      table,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> close() async {
    final db = await database;
    await db.close();
  }
} 