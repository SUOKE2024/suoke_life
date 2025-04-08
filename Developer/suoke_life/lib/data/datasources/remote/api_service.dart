import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/api_constants.dart';

/// API服务接口
/// 
/// 提供基本的HTTP请求方法，包括GET、POST、PUT、DELETE等
class ApiService {
  final Dio _dio;
  
  /// 构造函数
  ApiService({required Dio dio}) : _dio = dio;
  
  /// 发起GET请求
  /// 
  /// [endpoint] 请求终端点
  /// [queryParameters] 查询参数
  /// [requiresAuth] 是否需要认证
  /// [headers] 自定义请求头
  Future<dynamic> get(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    bool requiresAuth = false,
    Map<String, dynamic>? headers,
  }) async {
    try {
      final response = await _dio.get(
        endpoint,
        queryParameters: queryParameters,
        options: _getOptions(requiresAuth, headers),
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
  
  /// 发起POST请求
  /// 
  /// [endpoint] 请求终端点
  /// [body] 请求体
  /// [queryParameters] 查询参数
  /// [requiresAuth] 是否需要认证
  /// [headers] 自定义请求头
  Future<dynamic> post(
    String endpoint, {
    dynamic body,
    Map<String, dynamic>? queryParameters,
    bool requiresAuth = false,
    Map<String, dynamic>? headers,
  }) async {
    try {
      final response = await _dio.post(
        endpoint,
        data: body,
        queryParameters: queryParameters,
        options: _getOptions(requiresAuth, headers),
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
  
  /// 发起PUT请求
  /// 
  /// [endpoint] 请求终端点
  /// [body] 请求体
  /// [queryParameters] 查询参数
  /// [requiresAuth] 是否需要认证
  /// [headers] 自定义请求头
  Future<dynamic> put(
    String endpoint, {
    dynamic body,
    Map<String, dynamic>? queryParameters,
    bool requiresAuth = false,
    Map<String, dynamic>? headers,
  }) async {
    try {
      final response = await _dio.put(
        endpoint,
        data: body,
        queryParameters: queryParameters,
        options: _getOptions(requiresAuth, headers),
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
  
  /// 发起DELETE请求
  /// 
  /// [endpoint] 请求终端点
  /// [queryParameters] 查询参数
  /// [requiresAuth] 是否需要认证
  /// [headers] 自定义请求头
  Future<dynamic> delete(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    bool requiresAuth = false,
    Map<String, dynamic>? headers,
  }) async {
    try {
      final response = await _dio.delete(
        endpoint,
        queryParameters: queryParameters,
        options: _getOptions(requiresAuth, headers),
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
  
  /// 发起PATCH请求
  /// 
  /// [endpoint] 请求终端点
  /// [body] 请求体
  /// [queryParameters] 查询参数
  /// [requiresAuth] 是否需要认证
  /// [headers] 自定义请求头
  Future<dynamic> patch(
    String endpoint, {
    dynamic body,
    Map<String, dynamic>? queryParameters,
    bool requiresAuth = false,
    Map<String, dynamic>? headers,
  }) async {
    try {
      final response = await _dio.patch(
        endpoint,
        data: body,
        queryParameters: queryParameters,
        options: _getOptions(requiresAuth, headers),
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
  
  /// 获取请求选项
  /// 
  /// [requiresAuth] 是否需要认证
  /// [customHeaders] 自定义请求头
  Options _getOptions(bool requiresAuth, Map<String, dynamic>? customHeaders) {
    final headers = <String, dynamic>{};
    
    // 如果需要认证，添加Authorization头
    if (requiresAuth) {
      // 这里需要从安全存储中获取token
      // 注意：这个应该由Dio拦截器处理，这里只是示例
      // final token = await secureStorage.read(StorageKeys.userToken);
      // headers['Authorization'] = 'Bearer $token';
    }
    
    // 添加自定义请求头
    if (customHeaders != null) {
      headers.addAll(customHeaders);
    }
    
    return Options(headers: headers);
  }
}

/// API服务Provider
final apiServiceProvider = Provider<ApiService>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: ApiConstants.baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    contentType: 'application/json',
    responseType: ResponseType.json,
  ));
  
  // 可以在这里添加拦截器
  dio.interceptors.add(LogInterceptor(
    request: true,
    requestHeader: true,
    requestBody: true,
    responseHeader: true,
    responseBody: true,
    error: true,
  ));
  
  // 添加错误拦截器
  dio.interceptors.add(InterceptorsWrapper(
    onError: (error, handler) {
      // 处理错误，例如刷新令牌
      return handler.next(error);
    },
  ));
  
  return ApiService(dio: dio);
});
