import 'dart:async';
import 'dart:io';

import 'package:path/path.dart' as path;
import 'package:sqflite/sqflite.dart';
import 'base_storage.dart';

/// 离线数据存储实现
class OfflineStorage extends BaseStorage {
  late Database _db;
  final _controller = StreamController<MapEntry<String, dynamic>>.broadcast();
  final StorageConfig config;
  
  OfflineStorage({
    this.config = const StorageConfig(
      type: StorageType.offline,
      maxSize: 500 * 1024 * 1024, // 500MB
      encrypt: true,
      compress: true,
    ),
  });
  
  @override
  Future<void> initialize() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final dbPath = path.join(dir.path, 'suoke_offline.db');
      
      // 打开数据库
      _db = await openDatabase(
        dbPath,
        version: 1,
        onCreate: (Database db, int version) async {
          await db.execute('''
            CREATE TABLE offline_data (
              key TEXT PRIMARY KEY,
              value BLOB,
              size INTEGER,
              created_at INTEGER,
              updated_at INTEGER
            )
          ''');
        },
      );
    } catch (e) {
      throw StorageException('Failed to initialize OfflineStorage', e);
    }
  }
  
  @override
  Future<void> clear() async {
    try {
      await _db.delete('offline_data');
    } catch (e) {
      throw StorageException('Failed to clear OfflineStorage', e);
    }
  }
  
  @override
  Future<void> write(String key, dynamic value) async {
    try {
      final batch = _db.batch();
      final now = DateTime.now().millisecondsSinceEpoch;
      
      // 将数据转换为二进制
      List<int> data;
      if (value is List<int>) {
        data = value;
      } else {
        data = value.toString().codeUnits;
      }
      
      if (config.encrypt) {
        // TODO: 实现加密
      }
      if (config.compress) {
        // TODO: 实现压缩
      }
      
      // 检查存储大小限制
      final currentSize = await getSize();
      if (currentSize + data.length > config.maxSize) {
        // 清理部分数据
        await _cleanOldestData(data.length);
      }
      
      // 更新或插入数据
      batch.insert(
        'offline_data',
        {
          'key': key,
          'value': data,
          'size': data.length,
          'created_at': now,
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      
      await batch.commit();
      _controller.add(MapEntry(key, value));
    } catch (e) {
      throw StorageException('Failed to write offline data', e);
    }
  }
  
  @override
  Future<T?> read<T>(String key) async {
    try {
      final result = await _db.query(
        'offline_data',
        columns: ['value'],
        where: 'key = ?',
        whereArgs: [key],
      );
      
      if (result.isEmpty) return null;
      
      final data = result.first['value'] as List<int>;
      
      if (config.encrypt) {
        // TODO: 实现解密
      }
      if (config.compress) {
        // TODO: 实现解压
      }
      
      if (T == List<int>) {
        return data as T;
      } else {
        return String.fromCharCodes(data) as T;
      }
    } catch (e) {
      throw StorageException('Failed to read offline data', e);
    }
  }
  
  @override
  Future<void> delete(String key) async {
    try {
      await _db.delete(
        'offline_data',
        where: 'key = ?',
        whereArgs: [key],
      );
      _controller.add(MapEntry(key, null));
    } catch (e) {
      throw StorageException('Failed to delete offline data', e);
    }
  }
  
  @override
  Future<bool> exists(String key) async {
    final result = await _db.query(
      'offline_data',
      columns: ['key'],
      where: 'key = ?',
      whereArgs: [key],
    );
    return result.isNotEmpty;
  }
  
  @override
  Future<int> getSize() async {
    try {
      final result = await _db.rawQuery(
        'SELECT SUM(size) as total_size FROM offline_data'
      );
      return (result.first['total_size'] as int?) ?? 0;
    } catch (e) {
      throw StorageException('Failed to get offline data size', e);
    }
  }
  
  @override
  Stream<MapEntry<String, dynamic>> watch(String key) {
    return _controller.stream.where((event) => event.key == key);
  }
  
  /// 清理最旧的数据直到有足够空间
  Future<void> _cleanOldestData(int neededSpace) async {
    try {
      while (await getSize() + neededSpace > config.maxSize) {
        final oldestData = await _db.query(
          'offline_data',
          orderBy: 'updated_at ASC',
          limit: 1,
        );
        
        if (oldestData.isEmpty) break;
        
        await delete(oldestData.first['key'] as String);
      }
    } catch (e) {
      throw StorageException('Failed to clean oldest offline data', e);
    }
  }
  
  /// 获取数据统计信息
  Future<Map<String, dynamic>> getStats() async {
    try {
      final result = await _db.rawQuery('''
        SELECT 
          COUNT(*) as total_items,
          SUM(size) as total_size,
          MIN(created_at) as oldest_item,
          MAX(updated_at) as newest_item
        FROM offline_data
      ''');
      
      return {
        'totalItems': result.first['total_items'],
        'totalSize': result.first['total_size'],
        'oldestItem': DateTime.fromMillisecondsSinceEpoch(
          result.first['oldest_item'] as int
        ),
        'newestItem': DateTime.fromMillisecondsSinceEpoch(
          result.first['newest_item'] as int
        ),
      };
    } catch (e) {
      throw StorageException('Failed to get offline data stats', e);
    }
  }
  
  /// 释放资源
  Future<void> dispose() async {
    await _db.close();
    _controller.close();
  }
} 