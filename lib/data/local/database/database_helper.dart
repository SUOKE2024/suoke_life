import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._();
  static Database? _database;

  factory DatabaseHelper() => _instance;

  DatabaseHelper._();

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
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // 创建消息表
    await db.execute('''
      CREATE TABLE messages (
        id TEXT PRIMARY KEY,
        type INTEGER NOT NULL,
        content TEXT NOT NULL,
        is_from_user INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        duration INTEGER,
        thumbnail TEXT,
        metadata TEXT
      )
    ''');

    // 创建标签表
    await db.execute('''
      CREATE TABLE tags (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT
      )
    ''');

    // 创建生活记录表
    await db.execute('''
      CREATE TABLE life_records (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        time TEXT NOT NULL,
        location TEXT,
        images TEXT
      )
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // 处理数据库升级
  }
} 