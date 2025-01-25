/// Base storage service that defines common storage operations
abstract class BaseStorageService extends BaseService {
  Future<T?> get<T>(String key, {T? defaultValue});
  Future<void> set<T>(String key, T value);
  Future<void> remove(String key);
  Future<void> clear();
  Future<bool> containsKey(String key);
} 