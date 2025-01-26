import 'dart:async';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

abstract class LocalStorageService {
  Future<void> init();
}

class LocalStorageServiceImpl implements LocalStorageService {
  static const _databaseName = 'suoke_life.db';
  static const _databaseVersion = 1;

  Database? _database;

  @override
  Future<void> init() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, _databaseName);

    _database = await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
    );
  }

  Future _onCreate(Database db, int version) async {
    // 创建数据库表的 SQL 语句
    await db.execute('''
      CREATE TABLE user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        life_activity_data TEXT
      )
    ''');
    // 可以根据需要创建更多表
  }

  @override
} 