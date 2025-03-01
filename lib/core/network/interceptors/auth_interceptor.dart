import 'package:dio/dio.dart';
import '../../storage/secure_storage.dart';
import '../../utils/logger.dart';

/// 认证拦截器
/// 负责处理请求和响应中的认证相关操作
class AuthInterceptor extends Interceptor {
  /// 安全存储实例
  final SecureStorage _secureStorage;
  
  /// 访问令牌的存储键
  static const String _accessTokenKey = 'access_token';
  
  /// 刷新令牌的存储键
  static const String _refreshTokenKey = 'refresh_token';
  
  /// 构造函数
  AuthInterceptor(this._secureStorage);
  
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // 如果请求已经包含Authorization头，则不做修改
    if (options.headers.containsKey('Authorization')) {
      return handler.next(options);
    }
    
    // 对认证相关的路径不加Authorization头
    if (options.path.contains('/auth/login') || options.path.contains('/auth/register')) {
      return handler.next(options);
    }
    
    try {
      // 从安全存储中获取访问令牌
      final accessToken = await _secureStorage.read(_accessTokenKey);
      
      if (accessToken != null && accessToken.isNotEmpty) {
        // 添加Authorization头
        options.headers['Authorization'] = 'Bearer $accessToken';
      }
      
      handler.next(options);
    } catch (e, stackTrace) {
      logger.e('获取访问令牌失败', error: e, stackTrace: stackTrace);
      handler.next(options);
    }
  }
  
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // 检查响应中是否包含新的令牌
    if (response.data is Map && response.data.containsKey('token')) {
      final newToken = response.data['token'] as String?;
      if (newToken != null && newToken.isNotEmpty) {
        _updateAccessToken(newToken);
      }
    }
    
    handler.next(response);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // 处理401未授权错误（令牌过期）
    if (err.response?.statusCode == 401) {
      try {
        // 尝试使用刷新令牌获取新的访问令牌
        final refreshToken = await _secureStorage.read(_refreshTokenKey);
        
        if (refreshToken != null && refreshToken.isNotEmpty) {
          // 刷新令牌请求
          final dio = Dio();
          final refreshResponse = await dio.post<Map<String, dynamic>>(
            '${err.requestOptions.baseUrl}/auth/refresh',
            data: {'refresh_token': refreshToken},
          );
          
          if (refreshResponse.statusCode == 200 && refreshResponse.data != null) {
            final newAccessToken = refreshResponse.data!['access_token'] as String?;
            final newRefreshToken = refreshResponse.data!['refresh_token'] as String?;
            
            if (newAccessToken != null && newAccessToken.isNotEmpty) {
              // 更新令牌
              await _updateAccessToken(newAccessToken);
              if (newRefreshToken != null && newRefreshToken.isNotEmpty) {
                await _updateRefreshToken(newRefreshToken);
              }
              
              // 重试原请求
              final options = err.requestOptions;
              options.headers['Authorization'] = 'Bearer $newAccessToken';
              
              final response = await dio.fetch(options);
              return handler.resolve(response);
            }
          }
        }
      } catch (e, stackTrace) {
        logger.e('令牌刷新失败', error: e, stackTrace: stackTrace);
      }
      
      // 刷新失败，需要重新登录
      await _clearTokens();
    }
    
    // 继续处理错误
    handler.next(err);
  }
  
  /// 更新访问令牌
  Future<void> _updateAccessToken(String token) async {
    try {
      await _secureStorage.write(_accessTokenKey, token);
    } catch (e, stackTrace) {
      logger.e('更新访问令牌失败', error: e, stackTrace: stackTrace);
    }
  }
  
  /// 更新刷新令牌
  Future<void> _updateRefreshToken(String token) async {
    try {
      await _secureStorage.write(_refreshTokenKey, token);
    } catch (e, stackTrace) {
      logger.e('更新刷新令牌失败', error: e, stackTrace: stackTrace);
    }
  }
  
  /// 清除所有令牌
  Future<void> _clearTokens() async {
    try {
      await _secureStorage.delete(_accessTokenKey);
      await _secureStorage.delete(_refreshTokenKey);
    } catch (e, stackTrace) {
      logger.e('清除令牌失败', error: e, stackTrace: stackTrace);
    }
  }
} 