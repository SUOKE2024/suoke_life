/// 基于 Dio 的网络服务实现
class DioNetworkService implements NetworkService {
  late final Dio _dio;
  final _interceptors = <Interceptor>[];
  final _config = ServiceRegistry.instance.get<NetworkConfig>('network');
  
  @override
  Future<void> onInit() async {
    _dio = Dio(BaseOptions(
      baseUrl: _config.baseUrl,
      connectTimeout: Duration(milliseconds: _config.timeout),
      receiveTimeout: Duration(milliseconds: _config.timeout),
      sendTimeout: Duration(milliseconds: _config.timeout),
    ));

    // 添加基础拦截器
    _dio.interceptors.add(_createDioInterceptor());
  }

  @override
  Future<Response> get(
    String path, {
    Map<String, dynamic>? params,
    Map<String, String>? headers,
    Duration? timeout,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: params,
        options: Options(
          headers: headers,
          sendTimeout: timeout,
        ),
      );
      return _convertResponse(response);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, String>? headers,
    Duration? timeout,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        options: Options(
          headers: headers,
          sendTimeout: timeout,
        ),
      );
      return _convertResponse(response);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<Response> upload(
    String path,
    List<MultipartFile> files, {
    Map<String, dynamic>? data,
    Map<String, String>? headers,
    ProgressCallback? onProgress,
  }) async {
    try {
      final formData = FormData();
      
      // 添加文件
      for (final file in files) {
        formData.files.add(MapEntry(
          'files',
          await _convertMultipartFile(file),
        ));
      }

      // 添加其他数据
      if (data != null) {
        formData.fields.addAll(
          data.entries.map((e) => MapEntry(e.key, e.value.toString())),
        );
      }

      final response = await _dio.post(
        path,
        data: formData,
        options: Options(headers: headers),
        onSendProgress: onProgress,
      );
      
      return _convertResponse(response);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<Response> download(
    String path,
    String savePath, {
    Map<String, dynamic>? params,
    Map<String, String>? headers,
    ProgressCallback? onProgress,
  }) async {
    try {
      final response = await _dio.download(
        path,
        savePath,
        queryParameters: params,
        options: Options(headers: headers),
        onReceiveProgress: onProgress,
      );
      return _convertResponse(response);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  void addInterceptor(Interceptor interceptor) {
    _interceptors.add(interceptor);
  }

  @override
  void removeInterceptor(Interceptor interceptor) {
    _interceptors.remove(interceptor);
  }

  @override
  void cancelRequest([String? tag]) {
    if (tag != null) {
      _dio.close(tag);
    } else {
      _dio.close();
    }
  }

  /// 创建 Dio 拦截器
  Interceptor _createDioInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final requestOptions = RequestOptions(
          path: options.path,
          method: options.method,
          data: options.data,
          params: options.queryParameters,
          headers: options.headers.cast<String, String>(),
          timeout: options.sendTimeout,
          tag: options.extra['tag'] as String?,
        );

        // 执行自定义拦截器
        for (final interceptor in _interceptors) {
          try {
            final newOptions = await interceptor.onRequest(requestOptions);
            options.path = newOptions.path;
            options.method = newOptions.method;
            options.data = newOptions.data;
            options.queryParameters = newOptions.params ?? {};
            options.headers = newOptions.headers ?? {};
            options.sendTimeout = newOptions.timeout;
          } catch (e) {
            handler.reject(
              DioException(
                requestOptions: options,
                error: e,
              ),
            );
            return;
          }
        }

        handler.next(options);
      },
      onResponse: (response, handler) async {
        final customResponse = _convertResponse(response);

        // 执行自定义拦截器
        for (final interceptor in _interceptors) {
          try {
            final newResponse = await interceptor.onResponse(customResponse);
            response.data = newResponse.data;
            response.statusCode = newResponse.statusCode;
            response.statusMessage = newResponse.statusMessage;
          } catch (e) {
            handler.reject(
              DioException(
                requestOptions: response.requestOptions,
                error: e,
              ),
            );
            return;
          }
        }

        handler.next(response);
      },
      onError: (error, handler) async {
        final customError = _handleDioError(error);

        // 执行自定义拦截器
        for (final interceptor in _interceptors) {
          try {
            final result = await interceptor.onError(customError);
            if (result is Response) {
              handler.resolve(
                Response(
                  requestOptions: error.requestOptions,
                  data: result.data,
                  statusCode: result.statusCode,
                  statusMessage: result.statusMessage,
                ),
              );
              return;
            }
          } catch (e) {
            handler.reject(error);
            return;
          }
        }

        handler.reject(error);
      },
    );
  }

  /// 转换响应
  Response _convertResponse(Response<dynamic> response) {
    return Response(
      data: response.data,
      statusCode: response.statusCode,
      statusMessage: response.statusMessage,
      headers: response.headers.map,
      isRedirect: response.isRedirect,
      redirectUrl: response.realUri.toString(),
    );
  }

  /// 转换多部分文���
  Future<dio.MultipartFile> _convertMultipartFile(MultipartFile file) async {
    return dio.MultipartFile(
      file.stream,
      file.length,
      filename: file.filename,
      contentType: file.contentType != null 
        ? MediaType.parse(file.contentType!)
        : null,
    );
  }

  /// 处理 Dio 错误
  NetworkException _handleDioError(DioException error) {
    return NetworkException(
      message: error.message ?? 'Network error',
      code: error.response?.statusCode,
      data: error.response?.data,
    );
  }

  @override
  Future<void> onDispose() async {
    _dio.close();
    _interceptors.clear();
  }
} 