import 'package:dio/dio.dart';
import '../security/encryption_service.dart';
import '../cache/cache_service.dart';

class NetworkService {
  late final Dio _dio;
  final EncryptionService _encryption;
  final CacheService _cache;

  NetworkService(this._encryption, this._cache) {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.suoke.com/v1',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
    ));

    _dio.interceptors.addAll([
      _AuthInterceptor(),
      _CacheInterceptor(_cache),
      _EncryptionInterceptor(_encryption),
      _RetryInterceptor(),
    ]);
  }

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? params,
    bool useCache = true,
    Duration? cacheDuration,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: params,
        options: Options(
          extra: {
            'use_cache': useCache,
            'cache_duration': cacheDuration,
          },
        ),
      );
      return response;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response<T>> post<T>(
    String path,
    dynamic data, {
    bool encrypt = false,
  }) async {
    try {
      return await _dio.post<T>(
        path,
        data: data,
        options: Options(
          extra: {
            'encrypt': encrypt,
          },
        ),
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return NetworkTimeoutException();
        case DioExceptionType.badResponse:
          return ApiException(
            error.response?.statusCode ?? 500,
            error.response?.data?['message'] ?? '未知错误',
          );
        default:
          return NetworkException(error.message);
      }
    }
    return Exception('网络请求失败');
  }
}

class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // 添加认证信息
    final token = GetIt.I<StorageService>().get('auth_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}

class _CacheInterceptor extends Interceptor {
  final CacheService _cache;

  _CacheInterceptor(this._cache);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (options.method == 'GET' && options.extra['use_cache'] == true) {
      final cached = await _cache.get<String>(options.uri.toString());
      if (cached != null) {
        return handler.resolve(
          Response(
            requestOptions: options,
            data: cached,
            statusCode: 200,
          ),
        );
      }
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) async {
    if (response.requestOptions.method == 'GET' &&
        response.requestOptions.extra['use_cache'] == true) {
      await _cache.set(
        response.requestOptions.uri.toString(),
        response.data,
        ttl: response.requestOptions.extra['cache_duration'],
      );
    }
    handler.next(response);
  }
}

class _EncryptionInterceptor extends Interceptor {
  final EncryptionService _encryption;

  _EncryptionInterceptor(this._encryption);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (options.extra['encrypt'] == true && options.data != null) {
      options.data = await _encryption.encrypt(options.data);
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) async {
    if (response.requestOptions.extra['encrypt'] == true) {
      response.data = await _encryption.decrypt(response.data);
    }
    handler.next(response);
  }
}

class _RetryInterceptor extends Interceptor {
  int _retryCount = 0;
  static const _maxRetries = 3;

  @override
  Future onError(DioException err, ErrorInterceptorHandler handler) async {
    if (_shouldRetry(err) && _retryCount < _maxRetries) {
      _retryCount++;
      return _retry(err.requestOptions);
    }
    return handler.next(err);
  }

  bool _shouldRetry(DioException err) {
    return err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout;
  }

  Future<void> _retry(RequestOptions requestOptions) async {
    final options = Options(
      method: requestOptions.method,
      headers: requestOptions.headers,
    );

    return Dio().request<dynamic>(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
    );
  }
}

class NetworkTimeoutException implements Exception {
  final String message = '网络连接超时';
}

class ApiException implements Exception {
  final int code;
  final String message;

  ApiException(this.code, this.message);
}

class NetworkException implements Exception {
  final String message;

  NetworkException(this.message);
} 