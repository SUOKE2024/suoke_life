import 'package:dio/dio.dart';
import '../error/app_error.dart';
import '../logging/app_logger.dart';

class HttpClient {
  static final HttpClient _instance = HttpClient._internal();
  static HttpClient get instance => _instance;

  late final Dio _dio;
  final _logger = AppLogger.instance;

  HttpClient._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.suoke.life',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        _logger.debug('发起请求: ${options.uri}');
        // TODO: 添加认证token
        return handler.next(options);
      },
      onResponse: (response, handler) {
        _logger.debug('收到响应: ${response.statusCode}');
        return handler.next(response);
      },
      onError: (error, handler) {
        _logger.error(
          '请求错误: ${error.message}',
          error: error,
          stackTrace: error.stackTrace,
        );
        return handler.next(error);
      },
    ));
  }

  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  AppError _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return NetworkError('网络连接超时', code: 'TIMEOUT');
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode == 401) {
          return AuthError('未授权访问', code: 'UNAUTHORIZED');
        } else if (statusCode == 403) {
          return AuthError('访问被拒绝', code: 'FORBIDDEN');
        } else if (statusCode == 404) {
          return NetworkError('资源不存在', code: 'NOT_FOUND');
        } else if (statusCode == 500) {
          return NetworkError('服务器错误', code: 'SERVER_ERROR');
        }
        return NetworkError('请求失败: $statusCode');
      case DioExceptionType.cancel:
        return NetworkError('请求已取消', code: 'CANCELLED');
      default:
        return NetworkError('网络错误: ${error.message}');
    }
  }

  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  void clearAuthToken() {
    _dio.options.headers.remove('Authorization');
  }
} 