/// 服务器异常
class ServerException implements Exception {
  /// 错误消息
  final String message;
  
  /// HTTP状态码
  final int? statusCode;
  
  /// 构造函数
  const ServerException({
    required this.message,
    required this.statusCode,
  });
  
  @override
  String toString() {
    return 'ServerException: $statusCode - $message';
  }
}

/// 缓存异常
class CacheException implements Exception {
  /// 错误消息
  final String message;
  
  /// 构造函数
  const CacheException({required this.message});
  
  @override
  String toString() {
    return 'CacheException: $message';
  }
}

/// 网络异常
class NetworkException implements Exception {
  /// 错误消息
  final String message;
  
  /// 构造函数
  const NetworkException({required this.message});
  
  @override
  String toString() {
    return 'NetworkException: $message';
  }
}

/// 认证异常
class AuthException implements Exception {
  /// 错误消息
  final String message;
  
  /// 错误代码
  final int code;
  
  /// 构造函数
  const AuthException({
    required this.message, 
    required this.code,
  });
  
  @override
  String toString() {
    return 'AuthException: $code - $message';
  }
} 