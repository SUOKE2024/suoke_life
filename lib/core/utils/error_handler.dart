import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class ErrorHandler {
  static String handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
        return 'Connection timeout';
      case DioExceptionType.sendTimeout:
        return 'Send timeout';
      case DioExceptionType.receiveTimeout:
        return 'Receive timeout';
      case DioExceptionType.badResponse:
        return 'Bad response: ${error.response?.statusCode}';
      case DioExceptionType.cancel:
        return 'Request cancelled';
      case DioExceptionType.unknown:
        return 'Unknown error';
      default:
        return 'An unexpected error occurred';
    }
  }

  static void handleException(dynamic exception, StackTrace? stackTrace) {
    if (kDebugMode) {
      print('Exception: $exception');
      if (stackTrace != null) {
        print('Stack trace: $stackTrace');
      }
    }
    // 可以添加日志记录、错误上报等逻辑
  }
} 