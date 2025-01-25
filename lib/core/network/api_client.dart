class ApiClient {
  final Dio dio;
  final CacheManager cacheManager;
  
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? params,
    Duration? cacheDuration,
  }) async {
    if (cacheDuration != null) {
      final cached = await cacheManager.get<T>(path);
      if (cached != null) return cached;
    }
    
    final response = await dio.get(path, queryParameters: params);
    if (cacheDuration != null) {
      await cacheManager.set(path, response.data, maxAge: cacheDuration);
    }
    return response.data;
  }
} 