class ApiClient {
  final Dio _dio;
  final AuthService _authService;

  ApiClient({
    required String baseUrl,
    required AuthService authService,
  }) : _dio = Dio(BaseOptions(baseUrl: baseUrl)),
       _authService = authService {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.addAll([
      AuthInterceptor(_authService),
      LoggingInterceptor(),
      RetryInterceptor(),
    ]);
  }

  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      return _handleResponse(response, fromJson);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<T> post<T>(
    String path, {
    dynamic data,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final response = await _dio.post(path, data: data);
      return _handleResponse(response, fromJson);
    } catch (e) {
      throw _handleError(e);
    }
  }

  T _handleResponse<T>(
    Response response,
    T Function(Map<String, dynamic>)? fromJson,
  ) {
    if (response.statusCode != 200) {
      throw ApiException(
        code: response.statusCode ?? 500,
        message: 'Request failed',
      );
    }

    if (fromJson == null) {
      return response.data as T;
    }

    return fromJson(response.data);
  }

  Exception _handleError(dynamic error) {
    if (error is DioException) {
      return ApiException(
        code: error.response?.statusCode ?? 500,
        message: error.message ?? 'Unknown error',
      );
    }
    return error;
  }
} 