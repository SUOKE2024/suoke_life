/// 重试拦截器
class RetryInterceptor implements Interceptor {
  final _config = ServiceRegistry.instance.get<NetworkConfig>('network');
  
  @override
  Future<RequestOptions> onRequest(RequestOptions options) async {
    // 设置重试次数
    options.extra['retryCount'] = 0;
    return options;
  }

  @override
  Future<Response> onResponse(Response response) async {
    return response;
  }

  @override
  Future<dynamic> onError(NetworkException error) async {
    final options = error.data as RequestOptions?;
    if (options == null) return error;

    final retryCount = options.extra['retryCount'] as int? ?? 0;
    if (retryCount >= _config.retryCount) {
      return error;
    }

    // 增加重试次数
    options.extra['retryCount'] = retryCount + 1;

    // 延迟重试
    await Future.delayed(Duration(seconds: math.pow(2, retryCount).toInt()));

    // 重新发起请求
    try {
      final response = await Get.find<NetworkService>().request(options);
      return response;
    } catch (e) {
      return error;
    }
  }
} 