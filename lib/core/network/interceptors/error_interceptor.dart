import 'dart:io';
import 'package:dio/dio.dart';
import '../../error/exceptions.dart';
import '../../utils/logger.dart';

/// 错误处理拦截器
/// 负责将Dio异常转换为应用程序的自定义异常
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // 创建AppException实例
    AppException exception = _handleError(err);
    
    // 记录错误信息
    logger.e(
      '网络错误: ${exception.message}',
      error: err,
      stackTrace: err.stackTrace,
    );
    
    // 用自定义异常替换原始Dio异常
    err = err.copyWith(error: exception);
    
    // 继续处理错误
    handler.next(err);
  }
  
  /// 处理网络错误并转换为应用程序的自定义异常
  AppException _handleError(DioException err) {
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
        return NetworkException(
          '连接超时，请检查网络',
          code: 'CONNECTION_TIMEOUT',
        );
        
      case DioExceptionType.sendTimeout:
        return NetworkException(
          '发送请求超时，请稍后重试',
          code: 'SEND_TIMEOUT',
        );
        
      case DioExceptionType.receiveTimeout:
        return NetworkException(
          '接收响应超时，请稍后重试',
          code: 'RECEIVE_TIMEOUT',
        );
        
      case DioExceptionType.badResponse:
        return _handleResponseError(err);
        
      case DioExceptionType.cancel:
        return NetworkException(
          '请求已取消',
          code: 'REQUEST_CANCELLED',
        );
        
      case DioExceptionType.unknown:
        if (err.error is SocketException) {
          return NetworkException(
            '网络连接失败，请检查网络设置',
            code: 'NO_INTERNET_CONNECTION',
          );
        } else {
          return NetworkException(
            '发生未知错误: ${err.message}',
            code: 'UNKNOWN',
          );
        }
        
      default:
        return NetworkException(
          '发生未知错误: ${err.message}',
          code: 'UNKNOWN',
        );
    }
  }
  
  /// 处理基于HTTP状态码的响应错误
  AppException _handleResponseError(DioException err) {
    int statusCode = err.response?.statusCode ?? 0;
    dynamic data = err.response?.data;
    String serverMessage = '';
    
    // 尝试从响应中提取错误消息
    if (data != null && data is Map<String, dynamic>) {
      serverMessage = data['message'] as String? ?? 
                     data['error'] as String? ?? 
                     '';
    }
    
    switch (statusCode) {
      case 400:
        return BadRequestException(
          serverMessage.isNotEmpty ? serverMessage : '无效的请求',
          code: 'BAD_REQUEST',
        );
        
      case 401:
        return UnauthorizedException(
          serverMessage.isNotEmpty ? serverMessage : '未授权，请登录',
          code: 'UNAUTHORIZED',
        );
        
      case 403:
        return ForbiddenException(
          serverMessage.isNotEmpty ? serverMessage : '禁止访问此资源',
          code: 'FORBIDDEN',
        );
        
      case 404:
        return NotFoundException(
          serverMessage.isNotEmpty ? serverMessage : '请求的资源不存在',
          code: 'NOT_FOUND',
        );
        
      case 409:
        return ConflictException(
          serverMessage.isNotEmpty ? serverMessage : '资源冲突',
          code: 'CONFLICT',
        );
        
      case 422:
        return ValidationException(
          serverMessage.isNotEmpty ? serverMessage : '请求数据验证失败',
          code: 'VALIDATION_ERROR',
          validationErrors: data is Map<String, dynamic> && data.containsKey('errors') 
              ? data['errors'] as Map<String, dynamic>?
              : null,
        );
        
      case 429:
        return TooManyRequestsException(
          serverMessage.isNotEmpty ? serverMessage : '请求频率过高，请稍后再试',
          code: 'TOO_MANY_REQUESTS',
        );
        
      case 500:
      case 501:
      case 502:
      case 503:
      case 504:
        return ServerException(
          serverMessage.isNotEmpty ? serverMessage : '服务器错误，请稍后重试',
          code: 'SERVER_ERROR',
          statusCode: statusCode,
        );
        
      default:
        return ServerException(
          serverMessage.isNotEmpty ? serverMessage : '未知的服务器错误',
          code: 'UNKNOWN_SERVER_ERROR',
          statusCode: statusCode,
        );
    }
  }
}
