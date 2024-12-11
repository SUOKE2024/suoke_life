/// Base interface for all storage implementations
abstract class BaseStorage {
  /// Initialize storage
  static Future<BaseStorage> initialize();

  /// Get a value from storage
  Future<T?> get<T>(String key, {T? defaultValue});

  /// Set a value in storage
  Future<void> set<T>(String key, T value);

  /// Remove a value from storage
  Future<void> remove(String key);

  /// Clear all values in storage
  Future<void> clear();

  /// Check if key exists
  Future<bool> containsKey(String key);

  /// Get all keys
  Future<List<String>> getKeys();

  /// Dispose storage resources
  Future<void> dispose();
}

/// Storage configuration
class StorageConfig {
  final String path;
  final String name;
  final Map<String, dynamic> options;

  const StorageConfig({
    required this.path,
    required this.name,
    this.options = const {},
  });
}

/// Storage exception
class StorageException implements Exception {
  final String message;
  final StorageType type;
  final dynamic error;

  StorageException(
    this.message, {
    required this.type,
    this.error,
  });

  @override
  String toString() => 'StorageException(${type.name}): $message';
} 