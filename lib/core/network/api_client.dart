import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/environment.dart';
import '../utils/logger.dart';
import 'interceptors/auth_interceptor.dart';
import 'interceptors/error_interceptor.dart';
import 'interceptors/logging_interceptor.dart';

/// API请求方法
enum ApiMethod {
  /// GET请求
  get,

  /// POST请求
  post,

  /// PUT请求
  put,

  /// DELETE请求
  delete,

  /// PATCH请求
  patch,

  /// HEAD请求
  head,
}

/// API配置
class ApiConfig {
  static const String baseUrl = 'http://118.31.223.213/api';
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);
  static const String contentType = 'application/json; charset=utf-8';
  
  // API端点
  static const String endpoint = {
    'auth': '/auth',
    'users': '/users',
    'healthData': '/health-data',
    'knowledge': '/knowledge',
    'chat': '/chat',
    'sync': '/sync',
  };
}

/// API客户端类
class ApiClient {
  /// Dio HTTP客户端
  final Dio _dio;

  /// 构造函数
  ApiClient(this._dio) {
    _dio.options.baseUrl = Environment.apiUrl;
    _dio.options.connectTimeout = Duration(milliseconds: Environment.timeout);
    _dio.options.receiveTimeout = Duration(milliseconds: Environment.timeout);
    _dio.options.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  /// 设置认证令牌
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }
  
  /// 清除认证令牌
  void clearAuthToken() {
    _dio.options.headers.remove('Authorization');
  }

  /// 执行API请求
  Future<Response<T>> request<T>({
    required String endpoint,
    required ApiMethod method,
    Map<String, dynamic>? queryParameters,
    dynamic data,
    Map<String, dynamic>? headers,
    ResponseType responseType = ResponseType.json,
    String? contentType,
    bool validateStatus = true,
  }) async {
    try {
      // 构建请求选项
      final options = Options(
        headers: headers,
        responseType: responseType,
        contentType: contentType,
        validateStatus: validateStatus ? null : (_) => true,
      );

      // 根据方法选择对应的请求函数
      Response<T> response;
      switch (method) {
        case ApiMethod.get:
          response = await _dio.get<T>(
            endpoint,
            queryParameters: queryParameters,
            options: options,
          );
          break;
        case ApiMethod.post:
          response = await _dio.post<T>(
            endpoint,
            data: data,
            queryParameters: queryParameters,
            options: options,
          );
          break;
        case ApiMethod.put:
          response = await _dio.put<T>(
            endpoint,
            data: data,
            queryParameters: queryParameters,
            options: options,
          );
          break;
        case ApiMethod.delete:
          response = await _dio.delete<T>(
            endpoint,
            data: data,
            queryParameters: queryParameters,
            options: options,
          );
          break;
        case ApiMethod.patch:
          response = await _dio.patch<T>(
            endpoint,
            data: data,
            queryParameters: queryParameters,
            options: options,
          );
          break;
        case ApiMethod.head:
          response = await _dio.head<T>(
            endpoint,
            data: data,
            queryParameters: queryParameters,
            options: options,
          );
          break;
      }

      return response;
    } on DioException catch (e) {
      logger.e(
        'API请求失败: ${e.message}',
        error: e,
        stackTrace: e.stackTrace,
      );
      
      if (e.response != null) {
        logger.e('响应状态: ${e.response?.statusCode}');
        logger.e('响应数据: ${jsonEncode(e.response?.data)}');
      }
      
      rethrow;
    } catch (e, stackTrace) {
      logger.e('API请求未知错误', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// GET请求
  Future<Response<T>> get<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    Map<String, dynamic>? headers,
    ResponseType responseType = ResponseType.json,
  }) {
    return request<T>(
      endpoint: endpoint,
      method: ApiMethod.get,
      queryParameters: queryParameters,
      headers: headers,
      responseType: responseType,
    );
  }

  /// POST请求
  Future<Response<T>> post<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, dynamic>? headers,
    ResponseType responseType = ResponseType.json,
  }) {
    return request<T>(
      endpoint: endpoint,
      method: ApiMethod.post,
      data: data,
      queryParameters: queryParameters,
      headers: headers,
      responseType: responseType,
    );
  }

  /// PUT请求
  Future<Response<T>> put<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, dynamic>? headers,
    ResponseType responseType = ResponseType.json,
  }) {
    return request<T>(
      endpoint: endpoint,
      method: ApiMethod.put,
      data: data,
      queryParameters: queryParameters,
      headers: headers,
      responseType: responseType,
    );
  }

  /// DELETE请求
  Future<Response<T>> delete<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, dynamic>? headers,
    ResponseType responseType = ResponseType.json,
  }) {
    return request<T>(
      endpoint: endpoint,
      method: ApiMethod.delete,
      data: data,
      queryParameters: queryParameters,
      headers: headers,
      responseType: responseType,
    );
  }

  /// PATCH请求
  Future<Response<T>> patch<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Map<String, dynamic>? headers,
    ResponseType responseType = ResponseType.json,
  }) {
    return request<T>(
      endpoint: endpoint,
      method: ApiMethod.patch,
      data: data,
      queryParameters: queryParameters,
      headers: headers,
      responseType: responseType,
    );
  }

  /// 上传文件
  Future<Response> uploadFile(
    String path,
    String filePath, {
    String fileKey = 'file',
    Map<String, dynamic>? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    void Function(int, int)? onSendProgress,
  }) async {
    final formData = FormData.fromMap({
      ...?data,
      fileKey: await MultipartFile.fromFile(filePath),
    });
    
    return _dio.post(
      path,
      data: formData,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
    );
  }
}

/// 创建API客户端提供者
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: ApiConfig.baseUrl,
    connectTimeout: ApiConfig.connectTimeout,
    receiveTimeout: ApiConfig.receiveTimeout,
    sendTimeout: ApiConfig.sendTimeout,
    contentType: ApiConfig.contentType,
  ));
  
  // 添加拦截器
  dio.interceptors.add(LoggingInterceptor());
  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(ErrorInterceptor());
  
  return ApiClient(dio);
}); 