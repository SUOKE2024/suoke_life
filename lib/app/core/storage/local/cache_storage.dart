/// Cache storage implementation with expiration support
class CacheStorage extends BaseStorage {
  late final Box _box;
  final StorageConfig _config;
  final Duration _defaultExpiration;

  CacheStorage._(
    this._box,
    this._config, {
    Duration? defaultExpiration,
  }) : _defaultExpiration = defaultExpiration ?? const Duration(hours: 1);

  static Future<CacheStorage> initialize({
    StorageConfig? config,
    Duration? defaultExpiration,
  }) async {
    final defaultConfig = StorageConfig(
      path: 'storage/cache',
      name: 'cache_storage',
    );

    try {
      final box = await Hive.openBox(
        config?.name ?? defaultConfig.name,
        path: config?.path ?? defaultConfig.path,
      );

      return CacheStorage._(
        box,
        config ?? defaultConfig,
        defaultExpiration: defaultExpiration,
      );
    } catch (e) {
      throw StorageException(
        'Failed to initialize cache storage',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  @override
  Future<T?> get<T>(String key, {T? defaultValue}) async {
    try {
      final cacheEntry = await _getCacheEntry<T>(key);
      if (cacheEntry == null || cacheEntry.isExpired) {
        return defaultValue;
      }
      return cacheEntry.value;
    } catch (e) {
      throw StorageException(
        'Failed to get value for key: $key',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  @override
  Future<void> set<T>(
    String key,
    T value, {
    Duration? expiration,
  }) async {
    try {
      final entry = CacheEntry<T>(
        value: value,
        expiry: DateTime.now().add(expiration ?? _defaultExpiration),
      );
      await _box.put(key, entry.toJson());
    } catch (e) {
      throw StorageException(
        'Failed to set value for key: $key',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  @override
  Future<void> remove(String key) async {
    try {
      await _box.delete(key);
    } catch (e) {
      throw StorageException(
        'Failed to remove value for key: $key',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _box.clear();
    } catch (e) {
      throw StorageException(
        'Failed to clear cache',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  @override
  Future<bool> containsKey(String key) async {
    try {
      final entry = await _getCacheEntry(key);
      return entry != null && !entry.isExpired;
    } catch (e) {
      throw StorageException(
        'Failed to check key: $key',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  @override
  Future<List<String>> getKeys() async {
    try {
      final validKeys = <String>[];
      for (final key in _box.keys) {
        final entry = await _getCacheEntry(key as String);
        if (entry != null && !entry.isExpired) {
          validKeys.add(key);
        }
      }
      return validKeys;
    } catch (e) {
      throw StorageException(
        'Failed to get keys',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  /// Clean expired entries
  Future<void> cleanExpired() async {
    try {
      final expiredKeys = <String>[];
      for (final key in _box.keys) {
        final entry = await _getCacheEntry(key as String);
        if (entry == null || entry.isExpired) {
          expiredKeys.add(key);
        }
      }
      await _box.deleteAll(expiredKeys);
    } catch (e) {
      throw StorageException(
        'Failed to clean expired entries',
        type: StorageType.cache,
        error: e,
      );
    }
  }

  Future<CacheEntry<T>?> _getCacheEntry<T>(String key) async {
    final data = await _box.get(key);
    if (data == null) return null;
    return CacheEntry<T>.fromJson(data as Map<String, dynamic>);
  }

  @override
  Future<void> dispose() async {
    try {
      await _box.close();
    } catch (e) {
      throw StorageException(
        'Failed to dispose cache storage',
        type: StorageType.cache,
        error: e,
      );
    }
  }
}

/// Cache entry with expiration
class CacheEntry<T> {
  final T value;
  final DateTime expiry;

  CacheEntry({
    required this.value,
    required this.expiry,
  });

  bool get isExpired => DateTime.now().isAfter(expiry);

  Map<String, dynamic> toJson() => {
    'value': value,
    'expiry': expiry.toIso8601String(),
  };

  factory CacheEntry.fromJson(Map<String, dynamic> json) => CacheEntry(
    value: json['value'] as T,
    expiry: DateTime.parse(json['expiry'] as String),
  );
} 