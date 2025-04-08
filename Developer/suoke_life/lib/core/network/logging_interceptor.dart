import 'package:dio/dio.dart';

/// 日志拦截器，用于记录请求和响应的详细信息
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final requestPath = '${options.baseUrl}${options.path}';
    print('┌─────────────────────────────────────────────────────');
    print('│ 🚀 REQUEST[${options.method}] => PATH: $requestPath');
    
    if (options.queryParameters.isNotEmpty) {
      print('│ 🔍 QUERY PARAMS: ${options.queryParameters}');
    }
    
    if (options.headers.isNotEmpty) {
      print('│ 📋 HEADERS: ${_redactSensitiveHeaders(options.headers)}');
    }
    
    if (options.data != null) {
      print('│ 📦 DATA: ${_truncateIfNeeded(options.data.toString())}');
    }
    
    print('└─────────────────────────────────────────────────────');
    
    super.onRequest(options, handler);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final requestPath = '${response.requestOptions.baseUrl}${response.requestOptions.path}';
    print('┌─────────────────────────────────────────────────────');
    print('│ ✅ RESPONSE[${response.statusCode}] => PATH: $requestPath');
    
    if (response.headers.map.isNotEmpty) {
      print('│ 📋 HEADERS: ${_redactSensitiveHeaders(response.headers.map)}');
    }
    
    if (response.data != null) {
      final dataStr = _truncateIfNeeded(response.data.toString());
      print('│ 📦 DATA: $dataStr');
    }
    
    final duration = response.requestOptions.extra['duration'] as Duration?;
    if (duration != null) {
      print('│ ⏱️ DURATION: ${duration.inMilliseconds}ms');
    }
    
    print('└─────────────────────────────────────────────────────');
    
    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final requestPath = '${err.requestOptions.baseUrl}${err.requestOptions.path}';
    print('┌─────────────────────────────────────────────────────');
    print('│ ❌ ERROR[${err.response?.statusCode ?? 'UNKNOWN'}] => PATH: $requestPath');
    print('│ 📄 TYPE: ${err.type}');
    
    if (err.response != null) {
      print('│ 🔍 RESPONSE: ${_truncateIfNeeded(err.response.toString())}');
    }
    
    print('│ ❗ MESSAGE: ${err.message}');
    print('└─────────────────────────────────────────────────────');
    
    super.onError(err, handler);
  }
  
  /// 截断过长的字符串
  String _truncateIfNeeded(String text, {int maxLength = 1000}) {
    if (text.length <= maxLength) {
      return text;
    }
    return '${text.substring(0, maxLength)}... (${text.length - maxLength} more characters)';
  }
  
  /// 编辑敏感的请求头信息
  Map<String, dynamic> _redactSensitiveHeaders(Map<String, dynamic> headers) {
    final result = Map<String, dynamic>.from(headers);
    final sensitiveHeaders = ['authorization', 'cookie', 'set-cookie'];
    
    for (final key in sensitiveHeaders) {
      if (result.containsKey(key)) {
        result[key] = '******';
      }
    }
    
    return result;
  }
}