class CacheManager {
  static final instance = CacheManager._();
  CacheManager._();

  final _memoryCache = <String, CacheItem>{};
  final _diskCache = GetStorage();
  
  Future<void> initialize() async {
    await GetStorage.init();
    await _cleanExpiredCache();
  }

  Future<void> set(
    String key,
    dynamic value, {
    Duration? expiration,
    bool persistToDisk = false,
  }) async {
    final item = CacheItem(
      value: value,
      expiration: expiration != null
          ? DateTime.now().add(expiration)
          : null,
    );

    _memoryCache[key] = item;
    
    if (persistToDisk) {
      await _diskCache.write(key, {
        'value': value,
        'expiration': item.expiration?.toIso8601String(),
      });
    }
  }

  T? get<T>(String key) {
    final memoryItem = _memoryCache[key];
    if (memoryItem != null) {
      if (!memoryItem.isExpired) {
        return memoryItem.value as T?;
      }
      _memoryCache.remove(key);
    }

    final diskItem = _diskCache.read(key);
    if (diskItem != null) {
      final expiration = diskItem['expiration'] != null
          ? DateTime.parse(diskItem['expiration'])
          : null;
      if (expiration == null || expiration.isAfter(DateTime.now())) {
        return diskItem['value'] as T?;
      }
      _diskCache.remove(key);
    }

    return null;
  }

  Future<void> _cleanExpiredCache() async {
    _memoryCache.removeWhere((_, item) => item.isExpired);
    
    final keys = _diskCache.getKeys();
    for (final key in keys) {
      final item = _diskCache.read(key);
      if (item != null && item['expiration'] != null) {
        final expiration = DateTime.parse(item['expiration']);
        if (expiration.isBefore(DateTime.now())) {
          await _diskCache.remove(key);
        }
      }
    }
  }
}

class CacheItem {
  final dynamic value;
  final DateTime? expiration;

  CacheItem({
    required this.value,
    this.expiration,
  });

  bool get isExpired =>
      expiration != null && expiration!.isBefore(DateTime.now());
} 