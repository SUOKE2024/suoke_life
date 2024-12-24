abstract class IStorageService {
  Future<void> init();
  Future<void> write(String key, dynamic value);
  T? read<T>(String key);
  Future<void> remove(String key);
  Future<void> clear();
} 