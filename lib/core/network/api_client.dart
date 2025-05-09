import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:suoke_life/core/constants/app_constants.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// API请求异常
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException({
    required this.message,
    this.statusCode,
    this.data,
  });

  @override
  String toString() => 'ApiException: $message (Status: $statusCode)';
}

/// API客户端
///
/// 封装Dio实现HTTP请求的客户端类，处理认证、错误和重试逻辑
class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  late final Dio _dio;
  final AppLogger _logger = AppLogger();

  /// 单例访问器
  factory ApiClient() => _instance;

  ApiClient._internal() {
    final baseUrl = dotenv.env[AppConstants.apiBaseUrlKey] ?? '';

    final options = BaseOptions(
      baseUrl: baseUrl,
      connectTimeout:
          Duration(seconds: AppConstants.defaultConnectTimeoutSeconds),
      receiveTimeout: Duration(seconds: AppConstants.defaultApiTimeoutSeconds),
      contentType: 'application/json',
    );

    _dio = Dio(options);
    _setupInterceptors();

    _logger.i('ApiClient 初始化完成: baseUrl=$baseUrl');
  }

  /// 配置拦截器
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          _logger.d('API请求: ${options.method} ${options.path}');
          return handler.next(options);
        },
        onResponse: (response, handler) {
          _logger.d(
              'API响应: ${response.statusCode} ${response.requestOptions.path}');
          return handler.next(response);
        },
        onError: (DioException error, handler) {
          _logger.e(
            'API错误: ${error.requestOptions.path}',
            error,
            error.stackTrace,
          );

          final exception = _handleError(error);
          return handler.reject(
            DioException(
              requestOptions: error.requestOptions,
              error: exception,
              message: exception.message,
              response: error.response,
              type: error.type,
              stackTrace: error.stackTrace,
            ),
          );
        },
      ),
    );
  }

  /// 设置访问令牌
  void setToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  /// 清除访问令牌
  void clearToken() {
    _dio.options.headers.remove('Authorization');
  }

  /// 标准GET请求
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    } catch (e, stack) {
      _logger.e('GET请求未知错误: $path', e, stack);
      throw ApiException(message: e.toString());
    }
  }

  /// 标准POST请求
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    } catch (e, stack) {
      _logger.e('POST请求未知错误: $path', e, stack);
      throw ApiException(message: e.toString());
    }
  }

  /// 标准PUT请求
  Future<T> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    } catch (e, stack) {
      _logger.e('PUT请求未知错误: $path', e, stack);
      throw ApiException(message: e.toString());
    }
  }

  /// 标准DELETE请求
  Future<T> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    } catch (e, stack) {
      _logger.e('DELETE请求未知错误: $path', e, stack);
      throw ApiException(message: e.toString());
    }
  }

  /// 处理Dio异常
  ApiException _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: AppConstants.timeoutErrorMessage,
          statusCode: e.response?.statusCode,
          data: e.response?.data,
        );
      case DioExceptionType.badResponse:
        return ApiException(
          message: _getErrorMessage(e.response?.statusCode),
          statusCode: e.response?.statusCode,
          data: e.response?.data,
        );
      case DioExceptionType.cancel:
        return ApiException(
          message: '请求已取消',
          statusCode: e.response?.statusCode,
          data: e.response?.data,
        );
      default:
        if (e.error is SocketException) {
          return ApiException(
            message: AppConstants.networkErrorMessage,
            statusCode: e.response?.statusCode,
            data: e.response?.data,
          );
        }
        return ApiException(
          message: e.message ?? AppConstants.unknownErrorMessage,
          statusCode: e.response?.statusCode,
          data: e.response?.data,
        );
    }
  }

  /// 根据状态码获取错误消息
  String _getErrorMessage(int? statusCode) {
    switch (statusCode) {
      case 400:
        return '请求参数错误';
      case 401:
        return '未授权，请重新登录';
      case 403:
        return '拒绝访问';
      case 404:
        return '请求资源不存在';
      case 500:
        return AppConstants.serverErrorMessage;
      default:
        return AppConstants.unknownErrorMessage;
    }
  }
}
