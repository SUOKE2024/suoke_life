/// 存储管理器
class StorageManager {
  static final instance = StorageManager._();
  StorageManager._();

  final _providers = <String, StorageProvider>{};
  final _services = <String, StorageService>{};
  
  /// 初始化
  Future<void> initialize() async {
    try {
      // 初始化安全服务
      final encryption = Get.put(EncryptionService());
      final keyRotation = Get.put(KeyRotationService());
      final integrity = Get.put(IntegrityService());
      final secureEraser = Get.put(SecureEraser());
      
      await Future.wait([
        encryption.onInit(),
        keyRotation.onInit(),
        integrity.onInit(),
      ]);

      // 初始化共享首选项存储
      final sharedPrefs = SharedPreferencesProvider();
      await sharedPrefs.initialize();
      _providers['shared_prefs'] = sharedPrefs;

      // 初始化安全存储
      _providers['secure'] = SecureStorageProvider();

      // 初始化Hive存储
      final hive = HiveStorageProvider();
      await hive.initialize();
      _providers['hive'] = hive;

      // 创建存储服务
      _services['default'] = LocalStorageService(
        provider: _providers['shared_prefs']!,
      );

      _services['secure'] = LocalStorageService(
        provider: _providers['secure']!,
        options: const StorageOptions(
          encrypt: true,
          encryptionService: encryption,
          keyRotationService: keyRotation,
          integrityService: integrity,
          secureEraser: secureEraser,
        ),
      );

      _services['cache'] = LocalStorageService(
        provider: _providers['hive']!,
        options: const StorageOptions(
          maxSize: 524288000, // 500MB
          expireAfter: Duration(days: 7),
        ),
      );

      LoggerService.info('Storage manager initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize storage manager', error: e);
      rethrow;
    }
  }

  /// 获取存储服务
  StorageService getService([String name = 'default']) {
    final service = _services[name];
    if (service == null) {
      throw StorageException('Storage service not found: $name');
    }
    return service;
  }

  /// 关闭存储
  Future<void> dispose() async {
    for (final provider in _providers.values) {
      if (provider is HiveStorageProvider) {
        await provider.close();
      }
    }
    _providers.clear();
    _services.clear();
  }

  /// 清理过期缓存
  Future<void> cleanExpiredCache() async {
    final cache = getService('cache');
    final keys = await cache.getKeys();
    
    for (final key in keys) {
      final item = await cache.get(key);
      if (item is StorageItem && item.isExpired) {
        await cache.remove(key);
      }
    }
  }
} 