class AliHealthConfig {
  // API 配置
  static const String baseUrl = 'https://api.health.aliyun.com';
  static const String apiVersion = 'v1';
  static const String appKey = 'your_app_key';
  static const String appSecret = 'your_app_secret';

  // 服务类型
  static const Map<String, Map<String, dynamic>> services = {
    'health_check': {
      'path': '/health/check',
      'method': 'POST',
      'version': '2023-12-21',
    },
    'vital_signs': {
      'path': '/vital/signs',
      'method': 'POST',
      'version': '2023-12-21',
    },
    'medical_advice': {
      'path': '/medical/advice',
      'method': 'POST',
      'version': '2023-12-21',
    },
  };

  // 请求配置
  static const Duration timeout = Duration(seconds: 30);
  static const Map<String, String> defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // 签名配置
  static const String signMethod = 'HMAC-SHA256';
  static const String signVersion = '1.0';
  static const String format = 'JSON';
} 