class CacheManagerService extends GetxService {
  final DataStorageService _storageService;
  final SubscriptionService _subscriptionService;
  
  // 内存缓存
  final Map<String, dynamic> _memoryCache = {};
  final Map<String, DateTime> _expiryTimes = {};
  
  // 缓存配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _cacheConfig = {
    SubscriptionPlan.basic: {
      'max_size': 100,  // 最大缓存条目数
      'ttl': Duration(minutes: 30),  // 缓存生存时间
      'types': {'chat', 'basic_context'},  // 允许缓存的类型
    },
    SubscriptionPlan.pro: {
      'max_size': 500,
      'ttl': Duration(hours: 2),
      'types': {'chat', 'context', 'analysis'},
    },
    SubscriptionPlan.premium: {
      'max_size': 2000,
      'ttl': Duration(hours: 12),
      'types': {'chat', 'context', 'analysis', 'custom'},
    },
  };
  
  CacheManagerService({
    required DataStorageService storageService,
    required SubscriptionService subscriptionService,
  })  : _storageService = storageService,
        _subscriptionService = subscriptionService {
    _startPeriodicCleanup();
  }

  Future<void> set(
    String key,
    dynamic value, {
    required String type,
    Duration? ttl,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 检查缓存权限
      if (!_canCache(type)) return;

      // 检查缓存大小限制
      if (_isAtCapacity()) {
        _evictOldest();
      }

      // 计算过期时间
      final expiry = DateTime.now().add(ttl ?? _getDefaultTTL());

      // 保存到内存缓存
      _memoryCache[key] = {
        'value': value,
        'type': type,
        'metadata': metadata,
        'created_at': DateTime.now().toIso8601String(),
      };
      _expiryTimes[key] = expiry;

      // 持久化到存储
      await _persistToStorage(key, value, type, expiry, metadata);
    } catch (e) {
      debugPrint('缓存设置失败: $e');
    }
  }

  Future<T?> get<T>(String key, {String? type}) async {
    try {
      // 检查内存缓存
      if (_memoryCache.containsKey(key)) {
        if (_isExpired(key)) {
          _removeFromCache(key);
          return null;
        }
        
        final cached = _memoryCache[key];
        if (type != null && cached['type'] != type) return null;
        return cached['value'] as T;
      }

      // 检查持久化存储
      final stored = await _storageService.getCacheEntry(key);
      if (stored != null) {
        if (_isStoredExpired(stored)) {
          await _storageService.removeCacheEntry(key);
          return null;
        }
        
        if (type != null && stored['type'] != type) return null;
        
        // 加载到内存缓存
        _memoryCache[key] = stored;
        _expiryTimes[key] = DateTime.parse(stored['expiry']);
        
        return stored['value'] as T;
      }

      return null;
    } catch (e) {
      debugPrint('缓存获取失败: $e');
      return null;
    }
  }

  Future<void> remove(String key) async {
    try {
      _removeFromCache(key);
      await _storageService.removeCacheEntry(key);
    } catch (e) {
      debugPrint('缓存删除失败: $e');
    }
  }

  Future<void> clear({String? type}) async {
    try {
      if (type != null) {
        // 清除指定类型的缓存
        final keysToRemove = _memoryCache.entries
            .where((entry) => entry.value['type'] == type)
            .map((entry) => entry.key)
            .toList();
        
        for (final key in keysToRemove) {
          await remove(key);
        }
      } else {
        // 清除所有缓存
        _memoryCache.clear();
        _expiryTimes.clear();
        await _storageService.clearCache();
      }
    } catch (e) {
      debugPrint('缓存清理失败: $e');
    }
  }

  bool _canCache(String type) {
    final plan = _subscriptionService.currentPlan;
    final config = _cacheConfig[plan]!;
    return config['types'].contains(type);
  }

  bool _isAtCapacity() {
    final plan = _subscriptionService.currentPlan;
    final maxSize = _cacheConfig[plan]!['max_size'] as int;
    return _memoryCache.length >= maxSize;
  }

  void _evictOldest() {
    if (_memoryCache.isEmpty) return;
    
    final oldestKey = _expiryTimes.entries
        .reduce((a, b) => a.value.isBefore(b.value) ? a : b)
        .key;
    
    _removeFromCache(oldestKey);
  }

  Duration _getDefaultTTL() {
    final plan = _subscriptionService.currentPlan;
    return _cacheConfig[plan]!['ttl'] as Duration;
  }

  bool _isExpired(String key) {
    final expiry = _expiryTimes[key];
    return expiry != null && DateTime.now().isAfter(expiry);
  }

  bool _isStoredExpired(Map<String, dynamic> stored) {
    final expiry = DateTime.parse(stored['expiry']);
    return DateTime.now().isAfter(expiry);
  }

  void _removeFromCache(String key) {
    _memoryCache.remove(key);
    _expiryTimes.remove(key);
  }

  Future<void> _persistToStorage(
    String key,
    dynamic value,
    String type,
    DateTime expiry,
    Map<String, dynamic>? metadata,
  ) async {
    final entry = {
      'key': key,
      'value': value,
      'type': type,
      'expiry': expiry.toIso8601String(),
      'metadata': metadata,
      'created_at': DateTime.now().toIso8601String(),
    };

    await _storageService.setCacheEntry(key, entry);
  }

  void _startPeriodicCleanup() {
    Timer.periodic(Duration(minutes: 15), (_) => _cleanup());
  }

  Future<void> _cleanup() async {
    try {
      final now = DateTime.now();
      
      // 清理内存缓存
      _expiryTimes.removeWhere((key, expiry) {
        if (now.isAfter(expiry)) {
          _memoryCache.remove(key);
          return true;
        }
        return false;
      });

      // 清理存储缓存
      await _storageService.cleanExpiredCache();
    } catch (e) {
      debugPrint('缓存清理失败: $e');
    }
  }

  @override
  void onClose() {
    _cleanup();
    super.onClose();
  }
} 