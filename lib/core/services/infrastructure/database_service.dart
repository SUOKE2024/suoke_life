import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:io';

/// 数据库服务类，负责管理 SQLite 数据库的创建和升级
class DatabaseService {
  static const String _databaseName = 'suoke_life.db';
  static const int _databaseVersion = 1;

  Database? _database;

  /// 获取数据库实例，如果数据库未初始化则先初始化
  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  /// 初始化数据库
  Future<Database> _initDatabase() async {
    final String path = join(await getDatabasesPath(), _databaseName);
    return await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  /// 创建数据库表
  Future<void> _onCreate(Database db, int version) async {
    // 用户表
    await db.execute('''
      CREATE TABLE users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        avatar_url TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
      )
    ''');

    // 聊天历史表
    await db.execute('''
      CREATE TABLE chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        is_user INTEGER NOT NULL,
        timestamp INTEGER NOT NULL
      )
    ''');

    // 健康数据表
    await db.execute('''
      CREATE TABLE health_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        data_type TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT,
        timestamp INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    ''');

    // 生活记录表
    await db.execute('''
      CREATE TABLE life_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        category TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    ''');

    // 用户设置表
    await db.execute('''
      CREATE TABLE user_settings (
        user_id TEXT PRIMARY KEY,
        theme_mode TEXT NOT NULL DEFAULT 'system',
        language_code TEXT NOT NULL DEFAULT 'zh_CN',
        notification_enabled INTEGER NOT NULL DEFAULT 1,
        privacy_level TEXT NOT NULL DEFAULT 'normal',
        FOREIGN KEY (user_id) REFERENCES users (id)
      )
    ''');
  }

  /// 数据库升级
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // 在这里处理数据库版本升级逻辑
    if (oldVersion < 2) {
      // 版本 1 升级到版本 2 的迁移脚本
    }
  }

  /// 关闭数据库连接
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }

  /// 清空所有表数据
  Future<void> clearAllTables() async {
    final db = await database;
    await db.transaction((txn) async {
      // 按照外键约束的顺序删除数据
      await txn.delete('user_settings');
      await txn.delete('health_data');
      await txn.delete('life_records');
      await txn.delete('chat_history');
      await txn.delete('users');
    });
  }

  /// 获取数据库大小（字节）
  Future<int> getDatabaseSize() async {
    final String path = join(await getDatabasesPath(), _databaseName);
    final stat = await File(path).stat();
    return stat.size;
  }

  /// 备份数据库
  Future<void> backupDatabase() async {
    final dbPath = await getDatabasesPath();
    final backupPath = '$dbPath.backup';
    await File(dbPath).copy(backupPath);
  }

  /// 恢复数据库
  Future<void> restoreDatabase(String backupPath) async {
    final String dbPath = join(await getDatabasesPath(), _databaseName);
    
    // 关闭当前数据库连接
    await close();
    
    // 复制备份文件到数据库位置
    await File(backupPath).copy(dbPath);
    
    // 重新初始化数据库连接
    _database = await _initDatabase();
  }
} 