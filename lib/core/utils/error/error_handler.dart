import 'package:injectable/injectable.dart';
import '../logger/logger.dart';
import '../analytics/analytics_service.dart';
import 'package:dio/dio.dart';

@singleton
class ErrorHandler {
  final AppLogger _logger;
  final AnalyticsService _analytics;

  ErrorHandler(this._logger, this._analytics);

  Future<void> handleError(dynamic error, [StackTrace? stackTrace]) async {
    if (error is DioException) {
      await _handleDioError(error);
    } else {
      await _handleGenericError(error, stackTrace);
    }
  }

  Future<void> _handleDioError(DioException error) async {
    final message = _getDioErrorMessage(error);
    _logger.error('Network Error: $message', error, error.stackTrace);
    
    await _analytics.trackEvent('network_error', {
      'type': error.type.toString(),
      'message': message,
      'url': error.requestOptions.path,
      'method': error.requestOptions.method,
    });
  }

  String _getDioErrorMessage(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
        return '连接超时';
      case DioExceptionType.sendTimeout:
        return '发送超时';
      case DioExceptionType.receiveTimeout:
        return '接收超时';
      case DioExceptionType.badResponse:
        return '服务器错误 ${error.response?.statusCode}';
      case DioExceptionType.cancel:
        return '请求取消';
      default:
        return '网络错误';
    }
  }

  Future<void> _handleGenericError(dynamic error, [StackTrace? stackTrace]) async {
    _logger.error('Application Error', error, stackTrace);
    
    await _analytics.trackEvent('app_error', {
      'error': error.toString(),
      'stackTrace': stackTrace?.toString(),
    });
  }

  Future<T> wrap<T>(Future<T> Function() action) async {
    try {
      return await action();
    } catch (e, stack) {
      await handleError(e, stack);
      rethrow;
    }
  }
} 