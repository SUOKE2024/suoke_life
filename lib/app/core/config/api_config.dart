class ApiConfig {
  static const String baseUrl = 'https://api.suoke.com/v1';
  
  static const Duration connectTimeout = Duration(seconds: 5);
  static const Duration receiveTimeout = Duration(seconds: 3);
  static const Duration sendTimeout = Duration(seconds: 3);
  
  static const Map<String, String> defaultHeaders = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
  };

  // HTTP/2 配置
  static const bool enableHttp2 = true;
  static const int maxConcurrentRequests = 10;
  static const int idleTimeout = 30; // 秒
  
  // 证书配置
  static const String certificatePath = 'assets/certificates/certificate.pem';
  static const bool allowSelfSigned = true; // 开发环境可以设置为 true
  
  // 重试配置
  static const int maxRetries = 3;
  static const Duration retryInterval = Duration(seconds: 1);
} 