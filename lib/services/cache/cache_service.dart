class CacheService extends GetxService {
  final _cache = <String, dynamic>{};
  
  Future<T> getData<T>(String key, Future<T> Function() fetcher) async {
    // 1. 检查内存缓存
    if (_cache.containsKey(key)) {
      return _cache[key] as T;
    }
    
    // 2. 检查本地存储
    final localData = await Hive.box('cache').get(key);
    if (localData != null) {
      _cache[key] = localData;
      return localData as T;
    }
    
    // 3. 从远程获取
    final data = await fetcher();
    
    // 4. 更新缓存
    _cache[key] = data;
    await Hive.box('cache').put(key, data);
    
    return data;
  }
} 