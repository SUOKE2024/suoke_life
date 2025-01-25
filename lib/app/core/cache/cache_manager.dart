import 'package:injectable/injectable.dart';
import '../storage/storage_service.dart';

@lazySingleton
class CacheManager {
  final StorageService _storage;
  final Map<String, dynamic> _memoryCache = {};

  CacheManager(this._storage);

  Future<T?> get<T>(String key, {Duration? maxAge}) async {
    // 先检查内存缓存
    if (_memoryCache.containsKey(key)) {
      final cacheEntry = _memoryCache[key];
      if (cacheEntry is _CacheEntry && !cacheEntry.isExpired(maxAge)) {
        return cacheEntry.value as T?;
      }
      _memoryCache.remove(key); // 移除过期缓存
    }

    // 检查持久化存储
    final value = await _storage.read<T>(key);
    if (value != null) {
      _memoryCache[key] = _CacheEntry(value);
    }
    return value;
  }

  Future<void> set<T>(String key, T value) async {
    _memoryCache[key] = _CacheEntry(value);
    await _storage.write(key, value);
  }

  Future<void> remove(String key) async {
    _memoryCache.remove(key);
    await _storage.delete(key);
  }

  Future<void> clear() async {
    _memoryCache.clear();
    await _storage.clear();
  }
}

class _CacheEntry {
  final dynamic value;
  final DateTime timestamp;

  _CacheEntry(this.value) : timestamp = DateTime.now();

  bool isExpired(Duration? maxAge) {
    if (maxAge == null) return false;
    final age = DateTime.now().difference(timestamp);
    return age > maxAge;
  }
} 