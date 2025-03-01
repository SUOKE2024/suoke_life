import 'dart:async';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:logger/logger.dart';
import '../../../core/database/database_schema.dart';

/// 数据库帮助类
/// 负责数据库的初始化、迁移和基本操作
class DatabaseHelper {
  static const String _databaseName = DatabaseSchema.databaseName;
  static const int _databaseVersion = DatabaseSchema.databaseVersion;
  
  // 单例实例
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  
  // 数据库实例
  Database? _database;
  // 使用可变的logger变量
  Logger _logger;
  
  // 私有构造函数
  DatabaseHelper._internal() : _logger = Logger();
  
  // 工厂构造函数
  factory DatabaseHelper({Logger? logger}) {
    if (logger != null) {
      _instance._logger = logger;
    }
    return _instance;
  }
  
  /// 获取数据库实例
  Future<Database> get database async {
    if (_database != null) {
      return _database!;
    }
    
    _database = await _initDatabase();
    return _database!;
  }
  
  /// 初始化数据库
  Future<Database> _initDatabase() async {
    final String path = join(await getDatabasesPath(), _databaseName);
    
    _logger.i('初始化数据库: $path');
    
    return openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }
  
  /// 创建数据库表
  Future<void> _onCreate(Database db, int version) async {
    _logger.i('创建数据库表，版本: $version');
    await DatabaseSchema.createAllTables(db);
  }
  
  /// 数据库升级
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    _logger.i('升级数据库，从版本 $oldVersion 到 $newVersion');
    await DatabaseSchema.upgradeDatabase(db, oldVersion, newVersion);
  }
  
  /// 插入数据
  Future<int> insert(String table, Map<String, dynamic> data) async {
    final Database db = await database;
    return db.insert(
      table,
      data,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
  
  /// 批量插入数据
  Future<int> insertBatch(String table, List<Map<String, dynamic>> dataList) async {
    final Database db = await database;
    int count = 0;
    
    await db.transaction((txn) async {
      for (var data in dataList) {
        await txn.insert(
          table,
          data,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
        count++;
      }
    });
    
    return count;
  }
  
  /// 查询所有数据
  Future<List<Map<String, dynamic>>> queryAll(String table) async {
    final Database db = await database;
    return db.query(table);
  }
  
  /// 根据条件查询
  Future<List<Map<String, dynamic>>> query(
    String table, {
    List<String>? columns,
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
    int? limit,
    int? offset,
    String? groupBy,
    String? having,
  }) async {
    final Database db = await database;
    return db.query(
      table,
      columns: columns,
      where: where,
      whereArgs: whereArgs,
      orderBy: orderBy,
      limit: limit,
      offset: offset,
      groupBy: groupBy,
      having: having,
    );
  }
  
  /// 查询单条记录
  Future<Map<String, dynamic>?> queryOne(
    String table, {
    List<String>? columns,
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final Database db = await database;
    final results = await db.query(
      table,
      columns: columns,
      where: where,
      whereArgs: whereArgs,
      limit: 1,
    );
    
    if (results.isEmpty) {
      return null;
    }
    return results.first;
  }
  
  /// 更新数据
  Future<int> update(
    String table,
    Map<String, dynamic> data, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final Database db = await database;
    return db.update(
      table,
      data,
      where: where,
      whereArgs: whereArgs,
    );
  }
  
  /// 删除数据
  Future<int> delete(
    String table, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final Database db = await database;
    return db.delete(
      table,
      where: where,
      whereArgs: whereArgs,
    );
  }
  
  /// 执行原始SQL
  Future<List<Map<String, dynamic>>> rawQuery(
    String sql, [
    List<dynamic>? arguments,
  ]) async {
    final Database db = await database;
    return db.rawQuery(sql, arguments);
  }
  
  /// 执行原始SQL更新
  Future<int> rawUpdate(
    String sql, [
    List<dynamic>? arguments,
  ]) async {
    final Database db = await database;
    return db.rawUpdate(sql, arguments);
  }
  
  /// 执行原始SQL删除
  Future<int> rawDelete(
    String sql, [
    List<dynamic>? arguments,
  ]) async {
    final Database db = await database;
    return db.rawDelete(sql, arguments);
  }
  
  /// 执行事务
  Future<T> transaction<T>(Future<T> Function(Transaction txn) action) async {
    final Database db = await database;
    return db.transaction(action);
  }
  
  /// 获取数据库批量操作对象
  Future<Batch> batch() async {
    final Database db = await database;
    return db.batch();
  }
  
  /// 获取表的所有列名
  Future<List<String>> getTableColumns(String table) async {
    final Database db = await database;
    final result = await db.rawQuery('PRAGMA table_info($table)');
    return result.map((column) => column['name'] as String).toList();
  }
  
  /// 检查表是否存在
  Future<bool> isTableExists(String tableName) async {
    final Database db = await database;
    final result = await db.rawQuery(
      "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
      [tableName],
    );
    return result.isNotEmpty;
  }
  
  /// 关闭数据库
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
}