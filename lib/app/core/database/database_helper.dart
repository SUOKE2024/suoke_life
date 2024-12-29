import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseHelper {
  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final path = await getDatabasesPath();
    final dbPath = join(path, 'suoke.db');

    return await openDatabase(
      dbPath,
      version: 1,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> init() async {
    await database;
  }

  Future<void> _onCreate(Database db, int version) async {
    // 创建用户表
    await db.execute('''
      CREATE TABLE users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        avatar TEXT,
        role TEXT,
        specialty TEXT,
        description TEXT,
        created_at INTEGER NOT NULL
      )
    ''');

    // 创建消息表
    await db.execute('''
      CREATE TABLE messages (
        id TEXT PRIMARY KEY,
        room_id TEXT NOT NULL,
        content TEXT NOT NULL,
        type TEXT NOT NULL,
        sender_id TEXT NOT NULL,
        timestamp INTEGER NOT NULL
      )
    ''');

    // 创建服务表
    await db.execute('''
      CREATE TABLE services (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        type TEXT NOT NULL,
        image_url TEXT,
        status TEXT,
        created_at INTEGER NOT NULL
      )
    ''');

    // 创建健康调查表
    await db.execute('''
      CREATE TABLE surveys (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at INTEGER NOT NULL
      )
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // 处理数据库升级
  }

  Future<List<Map<String, dynamic>>> query(
    String table, {
    bool? distinct,
    List<String>? columns,
    String? where,
    List<Object?>? whereArgs,
    String? groupBy,
    String? having,
    String? orderBy,
    int? limit,
    int? offset,
  }) async {
    final db = await database;
    return db.query(
      table,
      distinct: distinct,
      columns: columns,
      where: where,
      whereArgs: whereArgs,
      groupBy: groupBy,
      having: having,
      orderBy: orderBy,
      limit: limit,
      offset: offset,
    );
  }

  Future<int> insert(String table, Map<String, Object?> values) async {
    final db = await database;
    return db.insert(table, values);
  }

  Future<int> update(
    String table,
    Map<String, Object?> values, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final db = await database;
    return db.update(
      table,
      values,
      where: where,
      whereArgs: whereArgs,
    );
  }

  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final db = await database;
    return db.delete(
      table,
      where: where,
      whereArgs: whereArgs,
    );
  }

  Future<void> execute(String sql) async {
    final db = await database;
    await db.execute(sql);
  }
} 