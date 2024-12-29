class CacheManager {
  final Redis redis;
  final Database sqlite;
  
  Future<T?> get<T>(String key, {Duration? maxAge}) async {
    // 多级缓存策略
    final redisData = await redis.get(key);
    if (redisData != null) {
      return redisData as T;
    }
    
    final sqliteData = await sqlite.get(key);
    if (sqliteData != null) {
      await redis.set(key, sqliteData, maxAge: maxAge);
      return sqliteData as T;
    }
    
    return null;
  }
} 