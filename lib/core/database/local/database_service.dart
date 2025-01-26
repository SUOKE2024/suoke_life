import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/database/database_config.dart';

/// 本地数据库服务类，封装 sqflite 数据库操作
///
/// 提供便捷的 API，用于执行 CRUD 操作，例如插入、查询、更新、删除数据。
class DatabaseService {
  Database? _database;

  /// 初始化数据库服务
  Future<Database> get database async {
    if (_database != null) {
      return _database!;
    }
    _database = await _initializeDatabase();
    return _database!;
  }

  /// 初始化数据库
  Future<Database> _initializeDatabase() async {
    return DatabaseConfig.getDatabase();
  }

  /// 插入数据
  ///
  /// [table] 表名
  /// [values] 要插入的键值对
  Future<int> insert(String table, Map<String, dynamic> values) async {
    final db = await database;
    return await db.insert(table, values);
  }

  /// 查询数据
  ///
  /// [table] 表名
  /// [columns] 要查询的列，默认为 null 查询所有列
  /// [where] 查询条件，默认为 null 无条件查询
  /// [whereArgs] 查询条件参数
  Future<List<Map<String, dynamic>>> query(
    String table, {
    List<String>? columns,
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.query(table, columns: columns, where: where, whereArgs: whereArgs);
  }

  /// 更新数据
  ///
  /// [table] 表名
  /// [values] 要更新的键值对
  /// [where] 更新条件，不能为空
  /// [whereArgs] 更新条件参数
  Future<int> update(
    String table,
    Map<String, dynamic> values, {
    required String where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.update(table, values, where: where, whereArgs: whereArgs);
  }

  /// 删除数据
  ///
  /// [table] 表名
  /// [where] 删除条件，不能为空
  /// [whereArgs] 删除条件参数
  Future<int> delete(
    String table, {
    required String where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.delete(table, where: where, whereArgs: whereArgs);
  }
} 