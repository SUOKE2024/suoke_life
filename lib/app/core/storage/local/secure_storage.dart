/// Secure storage implementation using flutter_secure_storage
class SecureStorage extends BaseStorage {
  late final FlutterSecureStorage _storage;
  final StorageConfig _config;

  SecureStorage._(this._storage, this._config);

  static Future<SecureStorage> initialize({StorageConfig? config}) async {
    try {
      final storage = FlutterSecureStorage(
        aOptions: AndroidOptions(
          encryptedSharedPreferences: true,
        ),
        iOptions: IOSOptions(
          accessibility: KeychainAccessibility.first_unlock,
        ),
      );

      return SecureStorage._(
        storage,
        config ?? const StorageConfig(
          path: 'storage/secure',
          name: 'secure_storage',
        ),
      );
    } catch (e) {
      throw StorageException(
        'Failed to initialize secure storage',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<T?> get<T>(String key, {T? defaultValue}) async {
    try {
      final value = await _storage.read(key: key);
      if (value == null) return defaultValue;
      return _deserialize<T>(value);
    } catch (e) {
      throw StorageException(
        'Failed to get value for key: $key',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<void> set<T>(String key, T value) async {
    try {
      final serialized = _serialize(value);
      await _storage.write(key: key, value: serialized);
    } catch (e) {
      throw StorageException(
        'Failed to set value for key: $key',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<void> remove(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (e) {
      throw StorageException(
        'Failed to remove value for key: $key',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _storage.deleteAll();
    } catch (e) {
      throw StorageException(
        'Failed to clear storage',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<bool> containsKey(String key) async {
    try {
      final value = await _storage.read(key: key);
      return value != null;
    } catch (e) {
      throw StorageException(
        'Failed to check key: $key',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<List<String>> getKeys() async {
    try {
      final all = await _storage.readAll();
      return all.keys.toList();
    } catch (e) {
      throw StorageException(
        'Failed to get keys',
        type: StorageType.secure,
        error: e,
      );
    }
  }

  @override
  Future<void> dispose() async {
    // FlutterSecureStorage doesn't need disposal
  }

  /// Serialize value for secure storage
  String _serialize(dynamic value) {
    if (value == null) return '';
    return json.encode(value);
  }

  /// Deserialize value from secure storage
  T? _deserialize<T>(String value) {
    if (value.isEmpty) return null;
    final dynamic decoded = json.decode(value);
    if (decoded is T) return decoded;
    return null;
  }
} 