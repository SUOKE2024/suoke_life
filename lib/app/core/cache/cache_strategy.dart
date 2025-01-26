class CacheStrategy {
  // 多级缓存
  static Future<T?> getWithStrategy<T>(
    String key,
    CacheService cacheService,
    RedisCacheService redisCache,
  ) async {
    // 1. 检查本地缓存
    final localData = await cacheService.get<T>(key);
    if (localData != null) return localData;

    // 2. 检查Redis缓存
    final redisData = await redisCache.get(key);
    if (redisData != null) {
      // 回填本地缓存
      await cacheService.set(key, redisData as T);
      return redisData;
    }

    return null;
  }

  // 缓存预热
  static Future<void> preloadCache(
    List<String> keys,
    RedisCacheService redisCache,
    CacheService localCache,
  ) async {
    for (final key in keys) {
      final data = await redisCache.get(key);
      if (data != null) {
        await localCache.set(key, data);
      }
    }
  }
}
