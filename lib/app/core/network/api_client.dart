import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'dart:io';
import '../config/api_config.dart';
import '../utils/token_manager.dart';

class ApiClient {
  late final Dio _dio;
  final TokenManager _tokenManager;

  ApiClient({required TokenManager tokenManager}) : _tokenManager = tokenManager {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      sendTimeout: ApiConfig.sendTimeout,
      headers: ApiConfig.defaultHeaders,
    ));

    // 配置 HTTP/2
    (_dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();
      client.idleTimeout = const Duration(seconds: ApiConfig.idleTimeout);
      client.connectionTimeout = ApiConfig.connectTimeout;
      
      // 强制启用 HTTP/2
      client.badCertificateCallback = (cert, host, port) => true;
      
      // 配置 HTTP/2 选项
      final context = SecurityContext.defaultContext;
      try {
        context.setTrustedCertificates('path/to/your/certificate.pem');
      } catch (e) {
        print('Warning: ${e.toString()}');
      }
      
      return client;
    };

    _dio.interceptors.addAll([
      InterceptorsWrapper(
        onRequest: _onRequest,
        onResponse: _onResponse,
        onError: _onError,
      ),
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: true,
      ),
    ]);
  }

  Future<void> _onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // 添加认证token
    final token = await _tokenManager.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  Future<void> _onResponse(Response response, ResponseInterceptorHandler handler) async {
    // 处理响应
    if (response.statusCode == 200) {
      handler.next(response);
    } else {
      handler.reject(
        DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
        ),
      );
    }
  }

  Future<void> _onError(DioException error, ErrorInterceptorHandler handler) async {
    // 处理错误
    if (error.response?.statusCode == 401) {
      // token过期，刷新token
      await _tokenManager.refreshToken();
      // 重试请求
      final token = await _tokenManager.getToken();
      error.requestOptions.headers['Authorization'] = 'Bearer $token';
      final response = await _dio.fetch(error.requestOptions);
      handler.resolve(response);
    } else {
      handler.next(error);
    }
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<dynamic> post(String path, {dynamic data}) async {
    try {
      final response = await _dio.post(path, data: data);
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<dynamic> put(String path, {dynamic data}) async {
    try {
      final response = await _dio.put(path, data: data);
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<dynamic> delete(String path) async {
    try {
      final response = await _dio.delete(path);
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<dynamic> download(String url, String savePath, {
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      await _dio.download(
        url,
        savePath,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      rethrow;
    }
  }

  // 上传语音文件
  Future<Map<String, dynamic>> uploadVoice(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
      });
      
      final response = await _dio.post(
        '/voice/upload',
        data: formData,
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  // 获取语音识别结果
  Future<Map<String, dynamic>> getVoiceRecognitionResult(String taskId) async {
    try {
      final response = await _dio.get('/voice/result/$taskId');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
} 