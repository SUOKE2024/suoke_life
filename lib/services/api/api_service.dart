import 'package:dio/dio.dart' hide Response;
import 'package:dio/dio.dart' as dio show Response;
import 'package:get/get.dart';
import '../auth/auth_service.dart';

class ApiService extends GetxService {
  late final Dio _dio;
  
  Future<void> init() async {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.suoke.life/v1',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    ));

    // 添加拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: _handleRequest,
      onResponse: _handleResponse,
      onError: _handleError,
    ));

    return Future.value();
  }

  void _handleRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // 添加认证token
    final token = Get.find<AuthService>().token;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  void _handleResponse(dio.Response response, ResponseInterceptorHandler handler) {
    // 处理响应数据
    handler.next(response);
  }

  void _handleError(DioException error, ErrorInterceptorHandler handler) {
    // 统一错误处理
    handler.next(error);
  }

  // API 方法
  Future<dio.Response> get(String path, {Map<String, dynamic>? params}) {
    return _dio.get(path, queryParameters: params);
  }

  Future<dio.Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }

  Future<dio.Response> put(String path, {dynamic data}) {
    return _dio.put(path, data: data);
  }

  Future<dio.Response> delete(String path) {
    return _dio.delete(path);
  }
} 