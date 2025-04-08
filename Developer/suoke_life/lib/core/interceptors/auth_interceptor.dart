import 'package:dio/dio.dart';
import '../../data/repositories/auth_repository_impl.dart';

class AuthInterceptor extends Interceptor {
  final AuthRepository _authRepository;
  final Dio _dio;
  
  AuthInterceptor({
    required AuthRepository authRepository,
    required Dio dio,
  })  : _authRepository = authRepository,
        _dio = dio;
        
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // 如果不是需要认证的请求，直接放行
    if (!_shouldIntercept(options)) {
      return handler.next(options);
    }
    
    // 添加认证令牌
    final token = await _authRepository.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    
    return handler.next(options);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // 如果不是认证错误，直接放行
    if (err.response?.statusCode != 401 || !_shouldIntercept(err.requestOptions)) {
      return handler.next(err);
    }
    
    // 尝试刷新令牌
    final refreshed = await _authRepository.refreshTokens();
    if (!refreshed) {
      // 刷新失败，返回原始错误
      return handler.next(err);
    }
    
    // 刷新成功，重新发送请求
    final token = await _authRepository.getToken();
    if (token == null) {
      return handler.next(err);
    }
    
    // 克隆原始请求
    final options = err.requestOptions;
    options.headers['Authorization'] = 'Bearer $token';
    
    // 重新发送请求
    try {
      final response = await _dio.fetch(options);
      return handler.resolve(response);
    } on DioException catch (e) {
      return handler.next(e);
    }
  }
  
  bool _shouldIntercept(RequestOptions options) {
    // 检查请求是否需要添加认证令牌
    return !options.path.contains('/login') && 
           !options.path.contains('/register') &&
           !options.path.contains('/oauth') &&
           !options.path.contains('/refresh');
  }
}
