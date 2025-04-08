import 'dart:async';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/database/database_schema.dart';

/// 数据库服务
///
/// 管理SQLite数据库的初始化、升级和访问
class DatabaseService {
  static const String _databaseName = 'suoke_life.db';
  static const int _databaseVersion = 1;

  Database? _database;
  final Completer<Database> _databaseCompleter = Completer<Database>();

  /// 获取数据库实例
  Future<Database> get database async {
    if (_database != null) return _database!;

    // 如果数据库尚未初始化，则初始化它
    await _initDatabase();
    return _databaseCompleter.future;
  }

  /// 初始化数据库
  Future<void> _initDatabase() async {
    try {
      final databasesPath = await getDatabasesPath();
      final path = join(databasesPath, _databaseName);

      // 打开数据库
      _database = await openDatabase(
        path,
        version: _databaseVersion,
        onCreate: _onCreate,
        onUpgrade: _onUpgrade,
      );

      _databaseCompleter.complete(_database);
    } catch (e) {
      print('数据库初始化错误: $e');
      _databaseCompleter.completeError(e);
    }
  }

  /// 创建数据库表
  Future<void> _onCreate(Database db, int version) async {
    try {
      // 创建用户表
      await db.execute(DatabaseSchema.createUserTable);

      // 创建健康数据表
      await db.execute(DatabaseSchema.createHealthDataTable);

      // 创建体质数据表
      await db.execute(DatabaseSchema.createConstitutionDataTable);

      // 创建知识节点表
      await db.execute(DatabaseSchema.createKnowledgeNodeTable);

      // 创建知识关系表
      await db.execute(DatabaseSchema.createKnowledgeRelationTable);

      // 创建向量存储表
      await db.execute(DatabaseSchema.createVectorStoreTable);

      print('数据库表创建成功');
    } catch (e) {
      print('创建数据库表错误: $e');
      rethrow;
    }
  }

  /// 升级数据库
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    try {
      if (oldVersion < 2 && newVersion >= 2) {
        // 版本1到版本2的升级逻辑
        // 例如：添加新表或修改现有表
      }

      print('数据库从版本 $oldVersion 升级到版本 $newVersion 成功');
    } catch (e) {
      print('升级数据库错误: $e');
      rethrow;
    }
  }

  /// 关闭数据库
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
}
