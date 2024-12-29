import 'package:redis/redis.dart';
import 'package:sqflite/sqflite.dart';
import '../security/encryption_service.dart';

class CacheService {
  final RedisConnection _redis;
  final Database _sqlite;
  final EncryptionService _encryption;
  
  // 内存缓存
  final _memoryCache = <String, _CacheItem>{};
  
  CacheService(this._redis, this._sqlite, this._encryption);

  Future<T?> get<T>(String key, {bool useLocalOnly = false}) async {
    // 1. 检查内存缓存
    if (_memoryCache.containsKey(key)) {
      final item = _memoryCache[key]!;
      if (!item.isExpired) {
        return item.value as T;
      }
      _memoryCache.remove(key);
    }

    // 2. 检查本地SQLite缓存
    final localResult = await _getFromSQLite<T>(key);
    if (localResult != null) {
      return localResult;
    }

    // 3. 如果允许远程缓存，检查Redis
    if (!useLocalOnly) {
      return await _getFromRedis<T>(key);
    }

    return null;
  }

  Future<void> set<T>(
    String key,
    T value, {
    Duration? ttl,
    bool localOnly = false,
    bool encrypt = false,
  }) async {
    // 1. 加密处理
    final processedValue = encrypt 
        ? await _encryption.encrypt(value) 
        : value;

    // 2. 更新内存缓存
    _memoryCache[key] = _CacheItem(
      value: processedValue,
      expireAt: ttl != null ? DateTime.now().add(ttl) : null,
    );

    // 3. 更新SQLite缓存
    await _setToSQLite(key, processedValue, ttl);

    // 4. 如果需要，更新Redis缓存
    if (!localOnly) {
      await _setToRedis(key, processedValue, ttl);
    }
  }

  Future<T?> _getFromSQLite<T>(String key) async {
    final result = await _sqlite.query(
      'cache',
      where: 'key = ? AND (expire_at IS NULL OR expire_at > ?)',
      whereArgs: [key, DateTime.now().millisecondsSinceEpoch],
    );

    if (result.isNotEmpty) {
      return result.first['value'] as T;
    }
    return null;
  }

  Future<T?> _getFromRedis<T>(String key) async {
    final command = await _redis.connect();
    try {
      final value = await command.get(key);
      if (value != null) {
        return value as T;
      }
    } finally {
      command.close();
    }
    return null;
  }

  Future<void> _setToSQLite(
    String key,
    dynamic value,
    Duration? ttl,
  ) async {
    final expireAt = ttl != null
        ? DateTime.now().add(ttl).millisecondsSinceEpoch
        : null;

    await _sqlite.insert(
      'cache',
      {
        'key': key,
        'value': value,
        'expire_at': expireAt,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> _setToRedis(
    String key,
    dynamic value,
    Duration? ttl,
  ) async {
    final command = await _redis.connect();
    try {
      if (ttl != null) {
        await command.setex(key, ttl.inSeconds, value);
      } else {
        await command.set(key, value);
      }
    } finally {
      command.close();
    }
  }
}

class _CacheItem {
  final dynamic value;
  final DateTime? expireAt;

  bool get isExpired => 
      expireAt != null && DateTime.now().isAfter(expireAt!);

  _CacheItem({
    required this.value,
    this.expireAt,
  });
} 