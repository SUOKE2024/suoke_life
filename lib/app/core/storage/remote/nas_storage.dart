/// NAS storage implementation for remote file storage
class NasStorage extends BaseStorage {
  final String _basePath;
  final NetworkService _network;
  final CacheStorage _cache;
  final StorageConfig _config;
  bool _initialized = false;

  NasStorage._(
    this._basePath,
    this._network,
    this._cache,
    this._config,
  );

  static Future<NasStorage> initialize({
    required String basePath,
    required NetworkService network,
    required CacheStorage cache,
    StorageConfig? config,
  }) async {
    final defaultConfig = StorageConfig(
      path: 'storage/nas',
      name: 'nas_storage',
    );

    try {
      final instance = NasStorage._(
        basePath,
        network,
        cache,
        config ?? defaultConfig,
      );
      
      await instance._validateConnection();
      instance._initialized = true;
      
      return instance;
    } catch (e) {
      throw StorageException(
        'Failed to initialize NAS storage',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<T?> get<T>(String key, {T? defaultValue}) async {
    try {
      // Try cache first
      final cached = await _cache.get<T>(key);
      if (cached != null) return cached;

      // Get from NAS
      final path = _getPath(key);
      final response = await _network.get(path);
      
      if (response.statusCode == 404) {
        return defaultValue;
      }

      final data = response.data as T;
      
      // Cache the result
      await _cache.set(key, data);
      
      return data;
    } catch (e) {
      throw StorageException(
        'Failed to get value for key: $key',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<void> set<T>(String key, T value) async {
    try {
      final path = _getPath(key);
      await _network.put(path, data: value);
      await _cache.set(key, value);
    } catch (e) {
      throw StorageException(
        'Failed to set value for key: $key',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<void> remove(String key) async {
    try {
      final path = _getPath(key);
      await _network.delete(path);
      await _cache.remove(key);
    } catch (e) {
      throw StorageException(
        'Failed to remove value for key: $key',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _network.delete(_basePath);
      await _cache.clear();
    } catch (e) {
      throw StorageException(
        'Failed to clear NAS storage',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<bool> containsKey(String key) async {
    try {
      if (await _cache.containsKey(key)) {
        return true;
      }

      final path = _getPath(key);
      final response = await _network.head(path);
      return response.statusCode == 200;
    } catch (e) {
      throw StorageException(
        'Failed to check key: $key',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<List<String>> getKeys() async {
    try {
      final response = await _network.get(_basePath);
      final List<dynamic> files = response.data as List;
      return files.cast<String>();
    } catch (e) {
      throw StorageException(
        'Failed to get keys',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  String _getPath(String key) => '$_basePath/$key';

  Future<void> _validateConnection() async {
    try {
      await _network.head(_basePath);
    } catch (e) {
      throw StorageException(
        'Failed to connect to NAS',
        type: StorageType.nas,
        error: e,
      );
    }
  }

  @override
  Future<void> dispose() async {
    _initialized = false;
  }
} 