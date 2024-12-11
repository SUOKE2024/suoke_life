/// Service that handles local data storage.
/// 
/// Features:
/// - Key-value storage
/// - Secure storage
/// - Cache management
/// - Data encryption
class StorageService extends BaseService {
  static final instance = StorageService._();
  StorageService._();

  late final Box _box;
  late final FlutterSecureStorage _secureStorage;
  bool _initialized = false;

  @override
  List<Type> get dependencies => [];

  @override
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Initialize Hive
      final appDir = await getApplicationDocumentsDirectory();
      await Hive.initFlutter(appDir.path);
      
      // Open default box
      _box = await Hive.openBox('app_storage');
      
      // Initialize secure storage
      _secureStorage = const FlutterSecureStorage(
        aOptions: AndroidOptions(
          encryptedSharedPreferences: true,
        ),
        iOptions: IOSOptions(
          accessibility: KeychainAccessibility.first_unlock,
        ),
      );

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
    T? defaultValue,
    bool secure = false,
  }) async {
    try {
      if (secure) {
        final value = await _secureStorage.read(key: key);
        if (value == null) return defaultValue;
        return _deserialize<T>(value);
      } else {
        return _box.get(key, defaultValue: defaultValue);
      }
    } catch (e) {
      LoggerService.error('Failed to get value for key: $key', error: e);
      return defaultValue;
    }
  }

  /// Set a value in storage
  Future<void> set<T>(
    String key,
    T value, {
    bool secure = false,
  }) async {
    try {
      if (secure) {
        final serialized = _serialize(value);
        await _secureStorage.write(key: key, value: serialized);
      } else {
        await _box.put(key, value);
      }
    } catch (e) {
      LoggerService.error('Failed to set value for key: $key', error: e);
      rethrow;
    }
  }

  /// Remove a value from storage
  Future<void> remove(String key, {bool secure = false}) async {
    try {
      if (secure) {
        await _secureStorage.delete(key: key);
      } else {
        await _box.delete(key);
      }
    } catch (e) {
      LoggerService.error('Failed to remove value for key: $key', error: e);
      rethrow;
    }
  }

  /// Remove multiple values matching a pattern
  Future<void> removeWhere(bool Function(String key) test) async {
    try {
      final keys = _box.keys.where(test).cast<String>().toList();
      await _box.deleteAll(keys);
    } catch (e) {
      LoggerService.error('Failed to remove values', error: e);
      rethrow;
    }
  }

  /// Clear all storage
  Future<void> clear({bool secure = false}) async {
    try {
      if (secure) {
        await _secureStorage.deleteAll();
      } else {
        await _box.clear();
      }
    } catch (e) {
      LoggerService.error('Failed to clear storage', error: e);
      rethrow;
    }
  }

  /// Check if a key exists
  Future<bool> containsKey(String key, {bool secure = false}) async {
    try {
      if (secure) {
        final value = await _secureStorage.read(key: key);
        return value != null;
      } else {
        return _box.containsKey(key);
      }
    } catch (e) {
      LoggerService.error('Failed to check key: $key', error: e);
      return false;
    }
  }

  /// Get all keys
  List<String> get keys => _box.keys.cast<String>().toList();

  /// Get all values
  List<T> getAll<T>() => _box.values.whereType<T>().toList();

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

  @override
  Future<void> dispose() async {
    if (!_initialized) return;
    await _box.close();
    _initialized = false;
  }
}

/// Storage exception
class StorageException implements Exception {
  final String message;
  StorageException(this.message);

  @override
  String toString() => 'StorageException: $message';
} 