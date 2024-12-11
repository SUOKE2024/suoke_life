/// Service that handles network operations.
/// 
/// Features:
/// - HTTP requests
/// - Request interceptors
/// - Response handling
/// - Error handling
/// - Retry logic
class NetworkService extends BaseService {
  static final instance = NetworkService._();
  NetworkService._();

  late final Dio _dio;
  late final String _baseUrl;
  late final Duration _timeout;
  bool _initialized = false;

  @override
  List<Type> get dependencies => [
    StorageService,
  ];

  @override
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Load configuration
      final config = await _loadConfig();
      _baseUrl = config.baseUrl;
      _timeout = Duration(milliseconds: config.timeoutMs);

      // Initialize Dio
      _dio = Dio(BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: _timeout,
        receiveTimeout: _timeout,
        sendTimeout: _timeout,
        validateStatus: (status) => status != null && status < 500,
      ));

      // Add interceptors
      _dio.interceptors.addAll([
        _getAuthInterceptor(),
        _getLogInterceptor(),
        _getRetryInterceptor(),
      ]);

      _initialized = true;
      LoggerService.info('Network service initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize network service', error: e);
      rethrow;
    }
  }

  /// Make a GET request
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    void Function(int, int)? onReceiveProgress,
  }) async {
    try {
      return await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Make a POST request
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    void Function(int, int)? onSendProgress,
    void Function(int, int)? onReceiveProgress,
  }) async {
    try {
      return await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Make a PUT request
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    void Function(int, int)? onSendProgress,
    void Function(int, int)? onReceiveProgress,
  }) async {
    try {
      return await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Make a DELETE request
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Upload file
  Future<Response<T>> uploadFile<T>(
    String path,
    File file, {
    String? fileName,
    Map<String, dynamic>? data,
    Options? options,
    CancelToken? cancelToken,
    void Function(int, int)? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: fileName ?? basename(file.path),
        ),
        if (data != null) ...data,
      });

      return await _dio.post<T>(
        path,
        data: formData,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Get auth interceptor
  Interceptor _getAuthInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final storage = DependencyManager.instance.get<StorageService>();
        final token = await storage.get<String>('auth_token');
        
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Handle token refresh
          try {
            await _refreshToken();
            // Retry original request
            return handler.resolve(await _retry(error.requestOptions));
          } catch (e) {
            // Handle refresh failure
            return handler.reject(error);
          }
        }
        return handler.next(error);
      },
    );
  }

  /// Get log interceptor
  Interceptor _getLogInterceptor() {
    return LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (log) {
        LoggerService.debug(log.toString(), context: 'Network');
      },
    );
  }

  /// Get retry interceptor
  Interceptor _getRetryInterceptor() {
    return RetryInterceptor(
      dio: _dio,
      logPrint: (message) {
        LoggerService.warning(message, context: 'Network Retry');
      },
      retries: 3,
      retryDelays: const [
        Duration(seconds: 1),
        Duration(seconds: 2),
        Duration(seconds: 3),
      ],
    );
  }

  /// Handle network errors
  Exception _handleError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return NetworkTimeoutException(error.message);
        case DioExceptionType.badResponse:
          return NetworkResponseException(
            error.response?.statusCode ?? 500,
            error.response?.data,
          );
        case DioExceptionType.cancel:
          return NetworkCancelException();
        default:
          return NetworkException(error.message);
      }
    }
    return NetworkException('Unknown error occurred');
  }

  /// Refresh auth token
  Future<void> _refreshToken() async {
    final storage = DependencyManager.instance.get<StorageService>();
    final refreshToken = await storage.get<String>('refresh_token');
    
    if (refreshToken == null) {
      throw NetworkAuthException('No refresh token available');
    }

    try {
      final response = await _dio.post<Map<String, dynamic>>(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final newToken = response.data?['access_token'] as String?;
      if (newToken == null) {
        throw NetworkAuthException('Invalid refresh token response');
      }

      await storage.set('auth_token', newToken);
    } catch (e) {
      throw NetworkAuthException('Token refresh failed');
    }
  }

  /// Retry failed request
  Future<Response<dynamic>> _retry(RequestOptions requestOptions) {
    final options = Options(
      method: requestOptions.method,
      headers: requestOptions.headers,
    );

    return _dio.request<dynamic>(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
    );
  }

  /// Load network configuration
  Future<NetworkConfig> _loadConfig() async {
    final storage = DependencyManager.instance.get<StorageService>();
    return storage.get<NetworkConfig>(
      'network_config',
      defaultValue: const NetworkConfig(
        baseUrl: 'https://api.suoke.com',
        timeoutMs: 30000,
      ),
    );
  }

  @override
  Future<void> dispose() async {
    _initialized = false;
    _dio.close();
  }
}

/// Network configuration
class NetworkConfig {
  final String baseUrl;
  final int timeoutMs;

  const NetworkConfig({
    required this.baseUrl,
    required this.timeoutMs,
  });

  factory NetworkConfig.fromJson(Map<String, dynamic> json) => NetworkConfig(
    baseUrl: json['base_url'] as String,
    timeoutMs: json['timeout_ms'] as int,
  );

  Map<String, dynamic> toJson() => {
    'base_url': baseUrl,
    'timeout_ms': timeoutMs,
  };
}

/// Network exceptions
class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
  @override
  String toString() => 'NetworkException: $message';
}

class NetworkTimeoutException extends NetworkException {
  NetworkTimeoutException([String? message]) : super(message ?? 'Request timed out');
}

class NetworkResponseException extends NetworkException {
  final int statusCode;
  final dynamic data;
  NetworkResponseException(this.statusCode, this.data)
      : super('Server responded with status $statusCode');
}

class NetworkCancelException extends NetworkException {
  NetworkCancelException() : super('Request was cancelled');
}

class NetworkAuthException extends NetworkException {
  NetworkAuthException(String message) : super(message);
} 