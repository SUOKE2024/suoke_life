import 'package:sqflite/sqflite.dart';

/// 数据库服务
///
/// 负责处理所有与本地SQLite数据库相关的操作
/// 提供CRUD操作的通用接口和特定表的便捷方法
class DatabaseService {
  final Database _database;

  DatabaseService(this._database);

  /// 获取数据库实例
  Database get database => _database;

  // 通用CRUD操作

  /// 插入记录到指定表
  Future<int> insert(String table, Map<String, dynamic> data) async {
    return await _database.insert(
      table,
      data,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// 批量插入记录
  Future<List<int>> batchInsert(
    String table,
    List<Map<String, dynamic>> dataList,
  ) async {
    final batch = _database.batch();

    for (var data in dataList) {
      batch.insert(table, data, conflictAlgorithm: ConflictAlgorithm.replace);
    }

    final results = await batch.commit();
    return results.cast<int>();
  }

  /// 查询指定表的所有记录
  Future<List<Map<String, dynamic>>> queryAll(String table) async {
    return await _database.query(table);
  }

  /// 根据条件查询记录
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
    return await _database.query(
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
  }

  /// 更新记录
  Future<int> update(
    String table,
    Map<String, dynamic> data, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    return await _database.update(
      table,
      data,
      where: where,
      whereArgs: whereArgs,
    );
  }

  /// 删除记录
  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    return await _database.delete(table, where: where, whereArgs: whereArgs);
  }

  /// 执行原始SQL查询
  Future<List<Map<String, dynamic>>> rawQuery(
    String sql, [
    List<Object?>? arguments,
  ]) async {
    return await _database.rawQuery(sql, arguments);
  }

  // 特定表的便捷方法

  /// 保存用户数据
  Future<int> saveUser(Map<String, dynamic> user) async {
    return insert('users', user);
  }

  /// 获取用户数据
  Future<Map<String, dynamic>?> getUser(String userId) async {
    final results = await query('users', where: 'id = ?', whereArgs: [userId]);

    return results.isNotEmpty ? results.first : null;
  }

  /// 保存聊天会话
  Future<int> saveChat(Map<String, dynamic> chat) async {
    return insert('chats', chat);
  }

  /// 获取用户的所有聊天会话
  Future<List<Map<String, dynamic>>> getUserChats(String userId) async {
    return query(
      'chats',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'updated_at DESC',
    );
  }

  /// 保存消息
  Future<int> saveMessage(Map<String, dynamic> message) async {
    return insert('messages', message);
  }

  /// 获取聊天会话的所有消息
  Future<List<Map<String, dynamic>>> getChatMessages(String chatId) async {
    return query(
      'messages',
      where: 'chat_id = ?',
      whereArgs: [chatId],
      orderBy: 'created_at ASC',
    );
  }

  /// 保存健康数据
  Future<int> saveHealthData(Map<String, dynamic> healthData) async {
    return insert('health_data', healthData);
  }

  /// 批量保存健康数据
  Future<List<int>> saveHealthDataBatch(
    List<Map<String, dynamic>> healthDataList,
  ) async {
    return batchInsert('health_data', healthDataList);
  }

  /// 获取用户的健康数据
  Future<List<Map<String, dynamic>>> getUserHealthData(
    String userId, {
    String? dataType,
    String? fromDate,
    String? toDate,
  }) async {
    String where = 'user_id = ?';
    List<Object?> whereArgs = [userId];

    if (dataType != null) {
      where += ' AND data_type = ?';
      whereArgs.add(dataType);
    }

    if (fromDate != null) {
      where += ' AND timestamp >= ?';
      whereArgs.add(fromDate);
    }

    if (toDate != null) {
      where += ' AND timestamp <= ?';
      whereArgs.add(toDate);
    }

    return query(
      'health_data',
      where: where,
      whereArgs: whereArgs,
      orderBy: 'timestamp DESC',
    );
  }

  /// 获取未同步的健康数据
  Future<List<Map<String, dynamic>>> getUnsyncedHealthData(
    String userId,
  ) async {
    return query(
      'health_data',
      where: 'user_id = ? AND is_synced = 0',
      whereArgs: [userId],
    );
  }

  /// 标记健康数据为已同步
  Future<int> markHealthDataSynced(List<String> ids) async {
    final batch = _database.batch();

    for (var id in ids) {
      batch.update(
        'health_data',
        {'is_synced': 1},
        where: 'id = ?',
        whereArgs: [id],
      );
    }

    final results = await batch.commit();
    return results.length;
  }

  /// 关闭数据库连接
  Future<void> close() async {
    await _database.close();
  }
}
