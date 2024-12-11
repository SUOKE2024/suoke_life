class CacheStrategyManager {
  static final instance = CacheStrategyManager._();
  CacheStrategyManager._();

  final _storage = Get.find<StorageManager>();
  final _networkMonitor = Get.find<NetworkMonitor>();
  
  final _cacheConfigs = <String, CacheConfig>{};
  final _cacheStats = <String, CacheStats>{};

  static const _defaultConfig = CacheConfig(
    strategy: CacheStrategy.networkFirst,
    maxAge: Duration(hours: 1),
    maxItems: 100,
    compression: true,
  );

  Future<void> initialize() async {
    // 加载缓存配置
    await _loadCacheConfigs();
    
    // 初始化缓存统计
    await _initializeCacheStats();
    
    // 启动缓存清理
    _startCacheCleanup();
  }

  Future<void> _loadCacheConfigs() async {
    final configs = await _storage.getObject<Map<String, dynamic>>(
      'cache_configs',
      (json) => json,
    );

    if (configs != null) {
      for (final entry in configs.entries) {
        _cacheConfigs[entry.key] = CacheConfig.fromJson(entry.value);
      }
    }
  }

  Future<T?> getCachedData<T>(
    String key,
    Future<T> Function() fetcher,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    final config = _cacheConfigs[key] ?? _defaultConfig;
    final stats = _getCacheStats(key);

    // 检查缓存
    final cachedData = await _storage.getObject<T>(
      'cache_$key',
      fromJson,
    );

    final cacheAge = await _getCacheAge(key);
    final isCacheValid = cacheAge != null && 
                        cacheAge < config.maxAge &&
                        cachedData != null;

    switch (config.strategy) {
      case CacheStrategy.cacheFirst:
        if (isCacheValid) {
          stats.cacheHits++;
          return cachedData;
        }
        return await _fetchAndCache(key, fetcher, config, stats);

      case CacheStrategy.networkFirst:
        if (_networkMonitor.isOnline) {
          return await _fetchAndCache(key, fetcher, config, stats);
        } else if (isCacheValid) {
          stats.cacheHits++;
          return cachedData;
        }
        break;

      case CacheStrategy.cacheOnly:
        if (isCacheValid) {
          stats.cacheHits++;
          return cachedData;
        }
        break;

      case CacheStrategy.networkOnly:
        if (_networkMonitor.isOnline) {
          return await _fetchAndCache(key, fetcher, config, stats);
        }
        break;
    }

    stats.cacheMisses++;
    return null;
  }

  Future<T> _fetchAndCache<T>(
    String key,
    Future<T> Function() fetcher,
    CacheConfig config,
    CacheStats stats,
  ) async {
    final data = await fetcher();
    
    // 缓存数据
    if (data != null) {
      await _storage.setObject('cache_$key', data);
      await _storage.setInt('cache_${key}_timestamp', DateTime.now().millisecondsSinceEpoch);
      stats.lastUpdate = DateTime.now();
    }
    
    return data;
  }

  Future<Duration?> _getCacheAge(String key) async {
    final timestamp = await _storage.getInt('cache_${key}_timestamp');
    if (timestamp == null) return null;
    
    final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
    return DateTime.now().difference(cacheTime);
  }

  CacheStats _getCacheStats(String key) {
    return _cacheStats.putIfAbsent(
      key,
      () => CacheStats(key: key),
    );
  }

  void setCacheConfig(String key, CacheConfig config) {
    _cacheConfigs[key] = config;
    _saveCacheConfigs();
  }

  Future<void> _saveCacheConfigs() async {
    final configs = <String, dynamic>{};
    for (final entry in _cacheConfigs.entries) {
      configs[entry.key] = entry.value.toJson();
    }
    await _storage.setObject('cache_configs', configs);
  }

  Future<void> clearCache(String key) async {
    await _storage.remove('cache_$key');
    await _storage.remove('cache_${key}_timestamp');
    _cacheStats.remove(key);
  }

  Future<void> clearAllCaches() async {
    for (final key in _cacheConfigs.keys) {
      await clearCache(key);
    }
  }

  Map<String, CacheStats> getCacheStats() => Map.unmodifiable(_cacheStats);
}

class CacheConfig {
  final CacheStrategy strategy;
  final Duration maxAge;
  final int maxItems;
  final bool compression;

  const CacheConfig({
    required this.strategy,
    required this.maxAge,
    required this.maxItems,
    required this.compression,
  });

  Map<String, dynamic> toJson() => {
    'strategy': strategy.toString(),
    'maxAge': maxAge.inMilliseconds,
    'maxItems': maxItems,
    'compression': compression,
  };

  factory CacheConfig.fromJson(Map<String, dynamic> json) => CacheConfig(
    strategy: CacheStrategy.values.byName(json['strategy']),
    maxAge: Duration(milliseconds: json['maxAge']),
    maxItems: json['maxItems'],
    compression: json['compression'],
  );
}

class CacheStats {
  final String key;
  int cacheHits = 0;
  int cacheMisses = 0;
  DateTime? lastUpdate;
  int size = 0;

  CacheStats({required this.key});

  Map<String, dynamic> toJson() => {
    'key': key,
    'hits': cacheHits,
    'misses': cacheMisses,
    'lastUpdate': lastUpdate?.toIso8601String(),
    'size': size,
  };
}

enum CacheStrategy {
  cacheFirst,
  networkFirst,
  cacheOnly,
  networkOnly,
} 