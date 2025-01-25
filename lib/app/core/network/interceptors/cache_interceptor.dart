/// 缓存拦截器
class CacheInterceptor implements Interceptor {
  final _storage = ServiceRegistry.instance.get<StorageService>();
  
  @override
  Future<RequestOptions> onRequest(RequestOptions options) async {
    // 只缓存 GET 请求
    if (options.method != 'GET') return options;
    
    // 检查是否有缓存
    final cacheKey = _getCacheKey(options);
    final cacheData = await _storage.get<Map<String, dynamic>>(cacheKey);
    
    if (cacheData != null) {
      final expireTime = DateTime.parse(cacheData['expireTime'] as String);
      if (expireTime.isAfter(DateTime.now())) {
        // 返回缓存数据
        throw CacheResponse(cacheData['data']);
      }
    }
    
    return options;
  }

  @override
  Future<Response> onResponse(Response response) async {
    // 只缓存成功的 GET 请求
    if (response.statusCode == 200 && 
        response.requestOptions.method == 'GET') {
      final cacheKey = _getCacheKey(response.requestOptions);
      await _storage.set(cacheKey, {
        'data': response.data,
        'expireTime': DateTime.now()
            .add(const Duration(minutes: 5))
            .toIso8601String(),
      });
    }
    return response;
  }

  @override
  Future<dynamic> onError(NetworkException error) async {
    return error;
  }

  /// 生成缓存键
  String _getCacheKey(RequestOptions options) {
    return 'cache_${options.method}_${options.path}_${options.params.toString()}';
  }
}

/// 缓存响应
class CacheResponse implements Exception {
  final dynamic data;
  CacheResponse(this.data);
} 