import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// 数据库助手类
/// 
/// 负责数据库的初始化、升级和基本访问
class DatabaseHelper {
  static const String _databaseName = 'suoke_database.db';
  static const int _databaseVersion = 1;

  // 单例实例
  static final DatabaseHelper _instance = DatabaseHelper._internal();

  // 数据库实例
  Database? _database;

  // 内部构造函数
  DatabaseHelper._internal();

  // 工厂构造函数
  factory DatabaseHelper() {
    return _instance;
  }

  // 获取数据库实例
  Future<Database> get database async {
    _database ??= await _initDatabase();
    return _database!;
  }

  // 初始化数据库
  Future<Database> _initDatabase() async {
    final String path = join(await getDatabasesPath(), _databaseName);
    return await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  // 创建数据库表
  Future<void> _onCreate(Database db, int version) async {
    // 创建知识节点表
    await db.execute('''
      CREATE TABLE knowledge_nodes(
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        topic TEXT NOT NULL,
        weight INTEGER NOT NULL DEFAULT 1,
        description TEXT,
        x REAL,
        y REAL,
        isFixed INTEGER DEFAULT 0
      )
    ''');

    // 创建知识关系表
    await db.execute('''
      CREATE TABLE knowledge_relations(
        id TEXT PRIMARY KEY,
        sourceId TEXT NOT NULL,
        targetId TEXT NOT NULL,
        type TEXT NOT NULL,
        strength INTEGER NOT NULL DEFAULT 1,
        description TEXT,
        isBidirectional INTEGER DEFAULT 0,
        FOREIGN KEY (sourceId) REFERENCES knowledge_nodes (id) ON DELETE CASCADE,
        FOREIGN KEY (targetId) REFERENCES knowledge_nodes (id) ON DELETE CASCADE
      )
    ''');
  }

  // 数据库升级
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // 未来版本升级处理逻辑
    }
  }

  // 关闭数据库
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
    }
  }
} 