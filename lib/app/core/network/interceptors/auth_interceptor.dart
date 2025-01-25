/// 认证拦截器
class AuthInterceptor implements Interceptor {
  final _storage = ServiceRegistry.instance.get<StorageService>();
  
  @override
  Future<RequestOptions> onRequest(RequestOptions options) async {
    final token = await _storage.get<String>('auth_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return options;
  }

  @override
  Future<Response> onResponse(Response response) async {
    // 处理认证相关响应
    if (response.statusCode == 401) {
      // Token 过期，尝试刷新
      await _refreshToken();
    }
    return response;
  }

  @override
  Future<dynamic> onError(NetworkException error) async {
    if (error.code == 401) {
      // 认证失败，清除token
      await _storage.remove('auth_token');
      // 跳转登录页
      Get.offAllNamed(Routes.LOGIN);
    }
    return error;
  }

  /// 刷新Token
  Future<void> _refreshToken() async {
    try {
      final refreshToken = await _storage.get<String>('refresh_token');
      if (refreshToken == null) {
        throw NetworkException(message: 'No refresh token');
      }

      // 调用刷新接口
      final response = await Get.find<NetworkService>().post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.isSuccess) {
        // 保存新token
        await _storage.set('auth_token', response.data['access_token']);
        await _storage.set('refresh_token', response.data['refresh_token']);
      } else {
        throw NetworkException(message: 'Failed to refresh token');
      }
    } catch (e) {
      LoggerService.error('Failed to refresh token', error: e);
      // 刷新失败，清除token
      await _storage.remove('auth_token');
      await _storage.remove('refresh_token');
      // 跳转登录页
      Get.offAllNamed(Routes.LOGIN);
    }
  }
} 