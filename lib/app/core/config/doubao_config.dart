class DouBaoConfig {
  static const String baseUrl = 'https://api.doubao.com';
  static const String defaultModel = 'xiaoai';
  
  static const Map<String, String> modelEndpoints = {
    'xiaoai': '/v1/chat/xiaoai',
    'laoke': '/v1/chat/laoke',
    'xiaoke': '/v1/chat/xiaoke',
  };
} 