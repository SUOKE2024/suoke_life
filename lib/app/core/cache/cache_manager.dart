import 'package:get_it/get_it.dart';
import 'package:sqflite/sqflite.dart';
import '../storage/storage_service.dart';

class CacheManager {
  // 内存缓存
  final _memoryCache = <String, dynamic>{};
  
  // SQLite数据库
  final Database _db;
  
  // 文件存储
  final StorageService _storage;

  CacheManager(this._db, this._storage);

  Future<T?> get<T>(String key) async {
    // 1. 检查内存缓存
    if (_memoryCache.containsKey(key)) {
      return _memoryCache[key] as T;
    }

    // 2. 检查SQLite缓存
    final result = await _db.query(
      'cache',
      where: 'key = ? AND expire_at > ?',
      whereArgs: [key, DateTime.now().millisecondsSinceEpoch],
    );

    if (result.isNotEmpty) {
      final value = result.first['value'];
      // 更新内存缓存
      _memoryCache[key] = value;
      return value as T;
    }

    // 3. 检查文件缓存
    return await _storage.get<T>(key);
  }

  Future<void> set<T>(
    String key,
    T value, {
    Duration? ttl,
    bool persistToFile = false,
  }) async {
    // 1. 更新内存缓存
    _memoryCache[key] = value;

    // 2. 更新SQLite缓存
    final expireAt = ttl != null
        ? DateTime.now().add(ttl).millisecondsSinceEpoch
        : null;

    await _db.insert(
      'cache',
      {
        'key': key,
        'value': value,
        'expire_at': expireAt,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );

    // 3. 可选：持久化到文件
    if (persistToFile) {
      await _storage.set(key, value);
    }
  }

  Future<void> clear() async {
    // 清除所有缓存
    _memoryCache.clear();
    await _db.delete('cache');
    await _storage.clear();
  }

  Future<void> remove(String key) async {
    // 移除指定缓存
    _memoryCache.remove(key);
    await _db.delete('cache', where: 'key = ?', whereArgs: [key]);
    await _storage.remove(key);
  }

  Future<void> clearExpired() async {
    // 清理过期缓存
    final now = DateTime.now().millisecondsSinceEpoch;
    await _db.delete(
      'cache',
      where: 'expire_at < ?',
      whereArgs: [now],
    );
  }
} 