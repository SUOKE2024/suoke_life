/// File-based storage implementation
class FileStorage extends BaseStorage {
  late final Box _box;
  final StorageConfig _config;

  FileStorage._(this._box, this._config);

  static Future<FileStorage> initialize({StorageConfig? config}) async {
    final defaultConfig = StorageConfig(
      path: 'storage/files',
      name: 'file_storage',
    );
    
    try {
      final box = await Hive.openBox(
        config?.name ?? defaultConfig.name,
        path: config?.path ?? defaultConfig.path,
      );

      return FileStorage._(box, config ?? defaultConfig);
    } catch (e) {
      throw StorageException(
        'Failed to initialize file storage',
        type: StorageType.file,
        error: e,
      );
    }
  }

  @override
  Future<T?> get<T>(String key, {T? defaultValue}) async {
    try {
      return _box.get(key, defaultValue: defaultValue);
    } catch (e) {
      throw StorageException(
        'Failed to get value for key: $key',
        type: StorageType.file,
        error: e,
      );
    }
  }

  @override
  Future<void> set<T>(String key, T value) async {
    try {
      await _box.put(key, value);
    } catch (e) {
      throw StorageException(
        'Failed to set value for key: $key',
        type: StorageType.file,
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
        type: StorageType.file,
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
        'Failed to clear storage',
        type: StorageType.file,
        error: e,
      );
    }
  }

  @override
  Future<bool> containsKey(String key) async {
    return _box.containsKey(key);
  }

  @override
  Future<List<String>> getKeys() async {
    return _box.keys.cast<String>().toList();
  }

  @override
  Future<void> dispose() async {
    try {
      await _box.close();
    } catch (e) {
      throw StorageException(
        'Failed to dispose storage',
        type: StorageType.file,
        error: e,
      );
    }
  }
} 