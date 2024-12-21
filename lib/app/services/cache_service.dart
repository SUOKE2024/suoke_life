import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class CacheService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final cacheSize = 0.obs;
  final cacheUsage = <String, int>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initCache();
  }

  Future<void> _initCache() async {
    try {
      await _loadCacheConfig();
      await _calculateCacheSize();
      await _cleanExpiredCache();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize cache', data: {'error': e.toString()});
    }
  }

  // 缓存数据
  Future<void> cacheData(String key, dynamic data, {Duration? expiry}) async {
    try {
      final cacheEntry = {
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
        'expiry': expiry?.inMilliseconds,
      };

      await _storageService.saveLocal('cache_$key', cacheEntry);
      await _updateCacheUsage(key, _calculateDataSize(data));
    } catch (e) {
      await _loggingService.log('error', 'Failed to cache data', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取缓存
  Future<dynamic> getCachedData(String key) async {
    try {
      final cacheEntry = await _storageService.getLocal('cache_$key');
      if (cacheEntry == null) return null;

      if (_isCacheExpired(cacheEntry)) {
        await removeCachedData(key);
        return null;
      }

      return cacheEntry['data'];
    } catch (e) {
      await _loggingService.log('error', 'Failed to get cached data', data: {'key': key, 'error': e.toString()});
      return null;
    }
  }

  // 清除缓存
  Future<void> clearCache() async {
    try {
      final keys = await _getCacheKeys();
      for (final key in keys) {
        await _storageService.removeLocal(key);
      }
      cacheSize.value = 0;
      cacheUsage.clear();
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear cache', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 移除缓存
  Future<void> removeCachedData(String key) async {
    try {
      await _storageService.removeLocal('cache_$key');
      await _updateCacheUsage(key, 0);
    } catch (e) {
      await _loggingService.log('error', 'Failed to remove cached data', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadCacheConfig() async {
    try {
      final config = await _storageService.getLocal('cache_config');
      if (config == null) {
        await _saveDefaultConfig();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDefaultConfig() async {
    try {
      await _storageService.saveLocal('cache_config', {
        'max_size': 100 * 1024 * 1024, // 100MB
        'default_expiry': 24 * 60 * 60 * 1000, // 24小时
        'auto_clean': true,
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _calculateCacheSize() async {
    try {
      final keys = await _getCacheKeys();
      int totalSize = 0;
      
      for (final key in keys) {
        final data = await _storageService.getLocal(key);
        if (data != null) {
          final size = _calculateDataSize(data);
          totalSize += size;
          cacheUsage[key] = size;
        }
      }
      
      cacheSize.value = totalSize;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _cleanExpiredCache() async {
    try {
      final keys = await _getCacheKeys();
      for (final key in keys) {
        final cacheEntry = await _storageService.getLocal(key);
        if (cacheEntry != null && _isCacheExpired(cacheEntry)) {
          await removeCachedData(key.replaceFirst('cache_', ''));
        }
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _getCacheKeys() async {
    try {
      // TODO: 实现获取所有缓存键
      return [];
    } catch (e) {
      return [];
    }
  }

  bool _isCacheExpired(Map<String, dynamic> cacheEntry) {
    if (cacheEntry['expiry'] == null) return false;
    
    final timestamp = DateTime.parse(cacheEntry['timestamp']);
    final expiry = Duration(milliseconds: cacheEntry['expiry']);
    return DateTime.now().difference(timestamp) > expiry;
  }

  int _calculateDataSize(dynamic data) {
    // TODO: 实现数据大小计算
    return 0;
  }

  Future<void> _updateCacheUsage(String key, int size) async {
    try {
      if (size == 0) {
        cacheUsage.remove('cache_$key');
      } else {
        cacheUsage['cache_$key'] = size;
      }
      
      cacheSize.value = cacheUsage.values.fold(0, (sum, size) => sum + size);
    } catch (e) {
      rethrow;
    }
  }
} 