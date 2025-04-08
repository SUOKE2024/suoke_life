import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:async';
import 'package:suoke_life/core/database/database_schema.dart';

/// 应用数据库管理类
///
/// 负责数据库的初始化、连接和基本操作
class AppDatabase {
  /// 单例实例
  static final AppDatabase _instance = AppDatabase._internal();
  
  /// 数据库实例
  static Database? _database;
  
  /// 私有构造函数
  AppDatabase._internal();
  
  /// 工厂构造函数
  factory AppDatabase() {
    return _instance;
  }
  
  /// 获取数据库实例
  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }
  
  /// 初始化数据库
  Future<Database> _initDatabase() async {
    // 获取数据库路径
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'suoke_life.db');
    
    // 打开数据库
    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }
  
  /// 创建数据库表
  Future<void> _onCreate(Database db, int version) async {
    // 用户表
    await db.execute('''
      CREATE TABLE ${DatabaseSchema.tableUsers} (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT,
        display_name TEXT,
        avatar TEXT,
        bio TEXT,
        role TEXT DEFAULT 'user',
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');
    
    // 健康数据表
    await db.execute('''
      CREATE TABLE ${DatabaseSchema.tableHealthData} (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        data_type TEXT NOT NULL,
        value TEXT NOT NULL,
        unit TEXT,
        timestamp TEXT NOT NULL,
        source TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES ${DatabaseSchema.tableUsers} (id) ON DELETE CASCADE
      )
    ''');
    
    // 知识节点表
    await db.execute('''
      CREATE TABLE ${DatabaseSchema.tableKnowledgeNodes} (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        source TEXT,
        category TEXT,
        tags TEXT,
        vector BLOB,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');
    
    // 会话历史表
    await db.execute('''
      CREATE TABLE ${DatabaseSchema.tableConversations} (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES ${DatabaseSchema.tableUsers} (id) ON DELETE CASCADE
      )
    ''');
    
    // 消息表
    await db.execute('''
      CREATE TABLE ${DatabaseSchema.tableMessages} (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        metadata TEXT,
        FOREIGN KEY (conversation_id) REFERENCES ${DatabaseSchema.tableConversations} (id) ON DELETE CASCADE
      )
    ''');
  }
  
  /// 数据库升级
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // 处理不同版本之间的表结构变化
    if (oldVersion < 2) {
      // 版本1升级到版本2的变更
    }
  }
  
  /// 关闭数据库
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
  
  /// 执行原始SQL查询
  Future<List<Map<String, dynamic>>> rawQuery(String sql, [List<dynamic>? arguments]) async {
    final db = await database;
    return await db.rawQuery(sql, arguments);
  }
  
  /// 查询表
  Future<List<Map<String, dynamic>>> query(
    String table, {
    List<String>? columns,
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
    int? limit,
    int? offset,
  }) async {
    final db = await database;
    return await db.query(
      table,
      columns: columns,
      where: where,
      whereArgs: whereArgs,
      orderBy: orderBy,
      limit: limit,
      offset: offset,
    );
  }
  
  /// 插入记录
  Future<int> insert(String table, Map<String, dynamic> values) async {
    final db = await database;
    return await db.insert(table, values);
  }
  
  /// 更新记录
  Future<int> update(
    String table,
    Map<String, dynamic> values, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.update(
      table,
      values,
      where: where,
      whereArgs: whereArgs,
    );
  }
  
  /// 删除记录
  Future<int> delete(
    String table, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.delete(
      table,
      where: where,
      whereArgs: whereArgs,
    );
  }
  
  /// 执行批量操作
  Future<void> batch(Function(Batch batch) operations) async {
    final db = await database;
    final batch = db.batch();
    operations(batch);
    await batch.commit();
  }
} 