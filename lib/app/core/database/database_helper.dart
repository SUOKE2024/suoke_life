import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../constants/database_tables.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._();
  static Database? _database;

  DatabaseHelper._();

  Future<Database> get database async {
    _database ??= await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'suoke.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // 创建生活记录表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS life_records (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_sync INTEGER NOT NULL DEFAULT 0
      )
    ''');

    // 创建探索内容表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS explore_items (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        subtitle TEXT NOT NULL,
        image_url TEXT,
        type TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL
      )
    ''');

    // 创建健康记录表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS health_records (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        height REAL NOT NULL,
        weight REAL NOT NULL,
        blood_pressure TEXT NOT NULL,
        heart_rate INTEGER NOT NULL,
        recorded_at TEXT NOT NULL
      )
    ''');

    // 创建AI聊天记录表
    await db.execute('''
      CREATE TABLE IF NOT EXISTS ai_chats (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        assistant_type TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // 处理数据库升级
    if (oldVersion < 2) {
      // 添加新表或修改现有表
    }
  }

  Future<void> close() async {
    final db = await database;
    await db.close();
  }
} 