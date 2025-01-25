abstract class BaseRepository<T> {
  Future<T?> get(String id);
  Future<List<T>> getAll();
  Future<void> save(T entity);
  Future<void> delete(String id);
  
  // 缓存管理
  Future<T?> getFromCache(String key);
  Future<void> saveToCache(String key, T data);
} 