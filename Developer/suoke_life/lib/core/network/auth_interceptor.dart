import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 授权拦截器，用于向请求中添加身份验证信息
class AuthInterceptor extends Interceptor {
  static const String _tokenKey = 'auth_token';
  
  @override
  Future<void> onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    
    // 尝试从本地存储获取Token
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_tokenKey);
    
    // 如果Token存在，则添加到请求头
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    
    // 继续请求
    return handler.next(options);
  }
  
  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    // 如果是401错误（未授权），可以在这里处理token刷新逻辑
    if (err.response?.statusCode == 401) {
      // TODO: 实现Token刷新逻辑
    }
    
    // 继续向上传递错误
    return handler.next(err);
  }
}