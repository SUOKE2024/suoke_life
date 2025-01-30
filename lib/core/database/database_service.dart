import 'dart:convert';
import 'package:injectable/injectable.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as path;
import 'package:meta/meta.dart';
import '../logger/app_logger.dart';
import 'table_definitions.dart';

@singleton
class DatabaseService {
  static Database? _database;
  final AppLogger _logger;

  DatabaseService(this._logger);

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final dbFile = path.join(dbPath, 'suoke_life.db');

    try {
      return await openDatabase(
        dbFile,
        version: 1,
        onCreate: _onCreate,
        onUpgrade: _onUpgrade,
        onConfigure: _onConfigure,
      );
    } catch (e, stack) {
      _logger.error('Failed to initialize database', e, stack);
      rethrow;
    }
  }

  Future<void> _onConfigure(Database db) async {
    await db.execute('PRAGMA foreign_keys = ON');
  }

  Future<void> _onCreate(Database db, int version) async {
    try {
      await db.transaction((txn) async {
        // 创建用户表
        await txn.execute(TableDefinitions.createUserTable);
        
        // 创建聊天会话表
        await txn.execute(TableDefinitions.createChatSessionTable);
        
        // 创建消息表
        await txn.execute(TableDefinitions.createMessageTable);
        
        // 创建健康数据表
        await txn.execute(TableDefinitions.createHealthDataTable);
        
        // 创建设置表
        await txn.execute(TableDefinitions.createSettingsTable);

        // 创建农业数据表
        await txn.execute(TableDefinitions.createAgricultureDataTable);

        // 创建知识库表
        await txn.execute(TableDefinitions.createKnowledgeBaseTable);
      });
    } catch (e, stack) {
      _logger.error('Failed to create database tables', e, stack);
      rethrow;
    }
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    try {
      await db.transaction((txn) async {
        if (oldVersion < 2) {
          // 版本1到2的迁移
          await txn.execute('ALTER TABLE users ADD COLUMN avatar TEXT;');
          await txn.execute('ALTER TABLE users ADD COLUMN last_active INTEGER;');
        }
        if (oldVersion < 3) {
          // 版本2到3的迁移
          await txn.execute('ALTER TABLE chat_sessions ADD COLUMN is_pinned INTEGER DEFAULT 0;');
          await txn.execute('ALTER TABLE messages ADD COLUMN is_read INTEGER DEFAULT 0;');
        }
      });
    } catch (e, stack) {
      _logger.error('Failed to upgrade database', e, stack);
      rethrow;
    }
  }

  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }

  /// 通用查询方法
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
    try {
      final db = await database;
      return await db.query(
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
    } catch (e, stack) {
      _logger.error('Failed to query database', e, stack);
      rethrow;
    }
  }

  /// 通用插入方法
  Future<int> insert(String table, Map<String, Object?> values) async {
    try {
      final db = await database;
      return await db.insert(table, values);
    } catch (e, stack) {
      _logger.error('Failed to insert into database', e, stack);
      rethrow;
    }
  }

  /// 通用更新方法
  Future<int> update(
    String table,
    Map<String, Object?> values, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    try {
      final db = await database;
      return await db.update(
        table,
        values,
        where: where,
        whereArgs: whereArgs,
      );
    } catch (e, stack) {
      _logger.error('Failed to update database', e, stack);
      rethrow;
    }
  }

  /// 通用删除方法
  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    try {
      final db = await database;
      return await db.delete(
        table,
        where: where,
        whereArgs: whereArgs,
      );
    } catch (e, stack) {
      _logger.error('Failed to delete from database', e, stack);
      rethrow;
    }
  }

  /// 执行原始SQL查询
  Future<List<Map<String, dynamic>>> rawQuery(
    String sql, [
    List<Object?>? arguments,
  ]) async {
    try {
      final db = await database;
      return await db.rawQuery(sql, arguments);
    } catch (e, stack) {
      _logger.error('Failed to execute raw query', e, stack);
      rethrow;
    }
  }

  /// 执行批量操作
  Future<List<Object?>> batch(Future<void> Function(Batch batch) operations) async {
    try {
      final db = await database;
      final batch = db.batch();
      await operations(batch);
      return await batch.commit();
    } catch (e, stack) {
      _logger.error('Failed to execute batch operations', e, stack);
      rethrow;
    }
  }
} 