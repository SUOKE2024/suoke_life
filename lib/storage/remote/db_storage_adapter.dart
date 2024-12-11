import 'dart:async';
import 'package:mysql1/mysql1.dart';
import '../local/base_storage.dart';

/// 数据库存储适配器
class DBStorageAdapter {
  late MySqlConnection _connection;
  final ConnectionSettings _settings;
  
  DBStorageAdapter({
    required String host,
    required int port,
    required String user,
    required String password,
    required String db,
  }) : _settings = ConnectionSettings(
    host: host,
    port: port,
    user: user,
    password: password,
    db: db,
  );
  
  /// 初始化连接
  Future<void> initialize() async {
    try {
      _connection = await MySqlConnection.connect(_settings);
      
      // 创建必要的表
      await _createTables();
    } catch (e) {
      throw StorageException('Failed to initialize database connection', e);
    }
  }
  
  /// 创建数据表
  Future<void> _createTables() async {
    try {
      // 创建基础数据表
      await _connection.query('''
        CREATE TABLE IF NOT EXISTS basic_data (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          storage_key VARCHAR(255) NOT NULL,
          storage_value TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_storage_key (storage_key)
        )
      ''');
      
      // 创建缓存数据表
      await _connection.query('''
        CREATE TABLE IF NOT EXISTS cache_data (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          storage_key VARCHAR(255) NOT NULL,
          storage_value LONGBLOB NOT NULL,
          expire_at TIMESTAMP NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_storage_key (storage_key)
        )
      ''');
      
      // 创建离线数据表
      await _connection.query('''
        CREATE TABLE IF NOT EXISTS offline_data (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          storage_key VARCHAR(255) NOT NULL,
          storage_value LONGBLOB NOT NULL,
          version INT NOT NULL DEFAULT 1,
          sync_status TINYINT NOT NULL DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_storage_key (storage_key)
        )
      ''');
    } catch (e) {
      throw StorageException('Failed to create database tables', e);
    }
  }
  
  /// 写入数据
  Future<void> write(StorageType type, String key, dynamic value) async {
    final table = _getTableName(type);
    try {
      await _connection.query(
        'INSERT INTO $table (storage_key, storage_value) VALUES (?, ?) '
        'ON DUPLICATE KEY UPDATE storage_value = ?',
        [key, value.toString(), value.toString()],
      );
    } catch (e) {
      throw StorageException('Failed to write data to database', e);
    }
  }
  
  /// 读取数据
  Future<String?> read(StorageType type, String key) async {
    final table = _getTableName(type);
    try {
      final results = await _connection.query(
        'SELECT storage_value FROM $table WHERE storage_key = ?',
        [key],
      );
      
      if (results.isEmpty) return null;
      return results.first['storage_value'] as String;
    } catch (e) {
      throw StorageException('Failed to read data from database', e);
    }
  }
  
  /// 删除数据
  Future<void> delete(StorageType type, String key) async {
    final table = _getTableName(type);
    try {
      await _connection.query(
        'DELETE FROM $table WHERE storage_key = ?',
        [key],
      );
    } catch (e) {
      throw StorageException('Failed to delete data from database', e);
    }
  }
  
  /// 清空数据
  Future<void> clear(StorageType type) async {
    final table = _getTableName(type);
    try {
      await _connection.query('TRUNCATE TABLE $table');
    } catch (e) {
      throw StorageException('Failed to clear database table', e);
    }
  }
  
  /// 检查数据是否存在
  Future<bool> exists(StorageType type, String key) async {
    final table = _getTableName(type);
    try {
      final results = await _connection.query(
        'SELECT 1 FROM $table WHERE storage_key = ?',
        [key],
      );
      return results.isNotEmpty;
    } catch (e) {
      throw StorageException('Failed to check data existence in database', e);
    }
  }
  
  /// 获取表中数据数量
  Future<int> count(StorageType type) async {
    final table = _getTableName(type);
    try {
      final results = await _connection.query(
        'SELECT COUNT(*) as count FROM $table',
      );
      return results.first['count'] as int;
    } catch (e) {
      throw StorageException('Failed to get count from database', e);
    }
  }
  
  /// 获取所有键
  Future<List<String>> getAllKeys(StorageType type) async {
    final table = _getTableName(type);
    try {
      final results = await _connection.query(
        'SELECT storage_key FROM $table',
      );
      return results.map((row) => row['storage_key'] as String).toList();
    } catch (e) {
      throw StorageException('Failed to get all keys from database', e);
    }
  }
  
  /// 批量写入数据
  Future<void> batchWrite(StorageType type, Map<String, dynamic> data) async {
    final table = _getTableName(type);
    try {
      await _connection.transaction((conn) async {
        for (final entry in data.entries) {
          await conn.query(
            'INSERT INTO $table (storage_key, storage_value) VALUES (?, ?) '
            'ON DUPLICATE KEY UPDATE storage_value = ?',
            [entry.key, entry.value.toString(), entry.value.toString()],
          );
        }
      });
    } catch (e) {
      throw StorageException('Failed to batch write data to database', e);
    }
  }
  
  /// 批量删除数据
  Future<void> batchDelete(StorageType type, List<String> keys) async {
    final table = _getTableName(type);
    try {
      await _connection.transaction((conn) async {
        for (final key in keys) {
          await conn.query(
            'DELETE FROM $table WHERE storage_key = ?',
            [key],
          );
        }
      });
    } catch (e) {
      throw StorageException('Failed to batch delete data from database', e);
    }
  }
  
  /// 获取表名
  String _getTableName(StorageType type) {
    switch (type) {
      case StorageType.basic:
        return 'basic_data';
      case StorageType.cache:
        return 'cache_data';
      case StorageType.offline:
        return 'offline_data';
    }
  }
  
  /// 关闭连接
  Future<void> dispose() async {
    await _connection.close();
  }
} 