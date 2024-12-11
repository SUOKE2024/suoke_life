/// 存储服务接口
abstract class StorageService {
  /// 初始化存储服务
  Future<void> init();

  /// 读取字符串
  Future<String?> getString(String key);

  /// 写入字符串
  Future<void> setString(String key, String value);

  /// 读取布尔值
  Future<bool?> getBool(String key);
/// Unified storage service that manages all storage operations
class StorageService extends BaseService {
  static final instance = StorageService._();
  StorageService._();

  late final SecureStorage _secureStorage;
  late final FileStorage _fileStorage;
  late final CacheStorage _cacheStorage;
  late final NasStorage _nasStorage;
  late final CloudStorage _cloudStorage;
  bool _initialized = false;

  @override
  List<Type> get dependencies => [];

  @override
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Initialize storage implementations
      _secureStorage = await SecureStorage.initialize();
      _fileStorage = await FileStorage.initialize();
      _cacheStorage = await CacheStorage.initialize();
      _nasStorage = await NasStorage.initialize();
      _cloudStorage = await CloudStorage.initialize();

      _initialized = true;
      LoggerService.info('Storage service initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize storage service', error: e);
      rethrow;
    }
  }

  /// Get a value from storage
  Future<T?> get<T>(
    String key, {
    StorageType type = StorageType.file,
    T? defaultValue,
  }) async {
    try {
      final storage = _getStorage(type);
      return await storage.get<T>(key, defaultValue: defaultValue);
    } catch (e) {
      LoggerService.error(
        'Failed to get value for key: $key from ${type.name}',
        error: e,
      );
      return defaultValue;
    }
  }

  /// Set a value in storage
  Future<void> set<T>(
    String key,
    T value, {
    StorageType type = StorageType.file,
  }) async {
    try {
      final storage = _getStorage(type);
      await storage.set<T>(key, value);
    } catch (e) {
      LoggerService.error(
        'Failed to set value for key: $key in ${type.name}',
        error: e,
      );
      rethrow;
    }
  }

  /// Remove a value from storage
  Future<void> remove(
    String key, {
    StorageType type = StorageType.file,
  }) async {
    try {
      final storage = _getStorage(type);
      await storage.remove(key);
    } catch (e) {
      LoggerService.error(
        'Failed to remove value for key: $key from ${type.name}',
        error: e,
      );
      rethrow;
    }
  }

  /// Clear all values in storage
  Future<void> clear({StorageType? type}) async {
    try {
      if (type != null) {
        final storage = _getStorage(type);
        await storage.clear();
      } else {
        // Clear all storages
        await Future.wait([
          _secureStorage.clear(),
          _fileStorage.clear(),
          _cacheStorage.clear(),
          _nasStorage.clear(),
          _cloudStorage.clear(),
        ]);
      }
    } catch (e) {
      LoggerService.error('Failed to clear storage', error: e);
      rethrow;
    }
  }

  /// Get storage implementation by type
  BaseStorage _getStorage(StorageType type) {
    switch (type) {
      case StorageType.secure:
        return _secureStorage;
      case StorageType.file:
        return _fileStorage;
      case StorageType.cache:
        return _cacheStorage;
      case StorageType.nas:
        return _nasStorage;
      case StorageType.cloud:
        return _cloudStorage;
    }
  }

  @override
  Future<void> dispose() async {
    if (!_initialized) return;
    
    await Future.wait([
      _secureStorage.dispose(),
      _fileStorage.dispose(),
      _cacheStorage.dispose(),
      _nasStorage.dispose(),
      _cloudStorage.dispose(),
    ]);

    _initialized = false;
  }
}

enum StorageType {
  secure,
  file,
  cache,
  nas,
  cloud,
} 