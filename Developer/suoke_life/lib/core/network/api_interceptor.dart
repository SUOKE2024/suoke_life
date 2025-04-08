import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../di/providers/auth_providers.dart';
import '../../core/exceptions/auth_exceptions.dart';
import '../../domain/usecases/auth_usecases.dart';
import '../utils/logger.dart';

/// API拦截器，处理认证和其他拦截需求
class ApiInterceptor extends Interceptor {
  final Ref ref;

  ApiInterceptor(this.ref);

  @override
  void onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    LogUtil.d('REQUEST[${options.method}] => PATH: ${options.path}');

    // 如果已经有认证头，就不需要再添加
    if (options.headers.containsKey('Authorization')) {
      return handler.next(options);
    }

    // 尝试获取认证令牌并添加到请求头
    try {
      // 这里需要小心处理，避免循环依赖
      // 通常只对非认证API添加令牌，认证API本身不需要令牌
      if (!options.path.contains('/auth/')) {
        final repository = ref.read(authRepositoryProvider);
        final details = await repository.getAuthStatusDetails();
        
        if (details.isAuthenticated && details.isTokenValid) {
          final token = await repository.getAccessToken();
          options.headers['Authorization'] = 'Bearer $token';
        }
      }
    } catch (e) {
      LogUtil.e('Failed to add auth token to request: $e');
    }

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    LogUtil.d(
        'RESPONSE[${response.statusCode}] <= PATH: ${response.requestOptions.path}');
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    LogUtil.e(
        'ERROR[${err.response?.statusCode}] => PATH: ${err.requestOptions.path}');

    // 处理401错误，尝试刷新令牌
    if (err.response?.statusCode == 401) {
      try {
        // 如果是刷新令牌请求失败，直接返回错误
        if (err.requestOptions.path.contains('/auth/refresh')) {
          throw const TokenExpiredException();
        }

        // 尝试刷新令牌
        final repository = ref.read(authRepositoryProvider);
        final refreshed = await repository.autoRefreshToken();
        
        if (refreshed) {
          // 获取新令牌
          final token = await repository.getAccessToken();
          
          // 使用新令牌重试原请求
          final options = err.requestOptions;
          options.headers['Authorization'] = 'Bearer $token';
          
          final retryResponse = await Dio().fetch(options);
          return handler.resolve(retryResponse);
        } else {
          throw const TokenExpiredException();
        }
      } catch (e) {
        LogUtil.e('Token refresh failed: $e');
        
        // 刷新失败，可能需要用户重新登录
        // 这里可以触发登出操作或发送事件
      }
    }

    handler.next(err);
  }
} 