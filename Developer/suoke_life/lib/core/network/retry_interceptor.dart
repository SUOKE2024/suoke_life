import 'dart:async';
import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../utils/logger.dart';

/// 重试拦截器
/// 
/// 在请求失败时自动重试，提高应用的网络弹性
class RetryInterceptor extends Interceptor {
  final Dio dio;
  final int maxRetries;
  final Duration retryDelay;
  final List<int> retryStatusCodes;
  final bool retryIdempotentRequests;
  
  /// 构造函数
  /// 
  /// [dio] Dio实例
  /// [maxRetries] 最大重试次数
  /// [retryDelay] 重试间隔
  /// [retryStatusCodes] 需要重试的HTTP状态码
  /// [retryIdempotentRequests] 是否重试幂等请求（GET、HEAD、OPTIONS）
  RetryInterceptor({
    required this.dio,
    this.maxRetries = ApiConstants.maxRetries,
    this.retryDelay = ApiConstants.retryDelay,
    this.retryStatusCodes = const [408, 429, 500, 502, 503, 504],
    this.retryIdempotentRequests = true,
  });
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // 获取当前请求的重试次数
    var retryCount = err.requestOptions.extra['retryCount'] as int? ?? 0;
    
    // 检查是否符合重试条件
    if (_shouldRetry(err, retryCount)) {
      retryCount++;
      logger.info('重试请求 (${retryCount}/${maxRetries}): ${err.requestOptions.uri}');
      
      // 延时后重试
      await Future.delayed(retryDelay * retryCount);
      
      try {
        // 创建一个新的Options对象
        final options = Options(
          method: err.requestOptions.method,
          headers: err.requestOptions.headers,
          contentType: err.requestOptions.contentType,
          responseType: err.requestOptions.responseType,
          listFormat: err.requestOptions.listFormat,
        );
        
        // 将重试次数存储在extra中
        err.requestOptions.extra['retryCount'] = retryCount;
        
        // 重试请求
        final response = await dio.request<dynamic>(
          err.requestOptions.path,
          data: err.requestOptions.data,
          queryParameters: err.requestOptions.queryParameters,
          cancelToken: err.requestOptions.cancelToken,
          options: options,
          onSendProgress: err.requestOptions.onSendProgress,
          onReceiveProgress: err.requestOptions.onReceiveProgress,
        );
        
        // 如果重试成功，处理响应
        return handler.resolve(response);
      } catch (e) {
        // 如果重试失败，继续抛出错误
        return handler.next(err);
      }
    }
    
    // 不符合重试条件，继续抛出错误
    return handler.next(err);
  }
  
  /// 检查是否应该重试
  bool _shouldRetry(DioException err, int retryCount) {
    // 已达到最大重试次数
    if (retryCount >= maxRetries) {
      return false;
    }
    
    // 如果请求被取消，不重试
    if (err.type == DioExceptionType.cancel) {
      return false;
    }
    
    // 检查HTTP方法是否为幂等方法
    final method = err.requestOptions.method.toUpperCase();
    final isIdempotent = method == 'GET' || method == 'HEAD' || method == 'OPTIONS';
    
    // 如果是非幂等方法，且配置不允许重试非幂等方法，则不重试
    if (!isIdempotent && !retryIdempotentRequests) {
      return false;
    }
    
    // 根据错误类型决定是否重试
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return true;
      case DioExceptionType.badResponse:
        // 根据状态码决定是否重试
        final statusCode = err.response?.statusCode;
        if (statusCode != null && retryStatusCodes.contains(statusCode)) {
          return true;
        }
        return false;
      case DioExceptionType.unknown:
        // 未知错误，可能是网络连接中断
        return true;
      default:
        return false;
    }
  }
} 