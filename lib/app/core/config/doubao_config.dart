class DoubaoConfig {
  // Doubao API 配置
  static const String baseUrl = 'https://api.doubao.com';
  static const String apiVersion = 'v1';
  static const String apiKey = 'your_api_key_here';
  
  // 模型配置
  static const Map<String, String> models = {
    'chat': 'doubao-pro-32k',      // 聊天模型
    'embedding': 'doubao-embedding', // 向量模型
    'knowledge': 'doubao-pro-128k', // 知识库模型
  };

  // 助手配置
  static const Map<String, Map<String, String>> assistants = {
    'xiaoi': {
      'name': '小艾',
      'role': 'life_assistant',
      'model': 'doubao-pro-32k',
      'temperature': '0.7',
      'mode': 'agentic',
    },
    'laoke': {
      'name': '老克',
      'role': 'knowledge_advisor',
      'model': 'doubao-pro-128k',
      'temperature': '0.3',
      'mode': 'agentic',
    },
    'xiaoke': {
      'name': '小克',
      'role': 'business_assistant',
      'model': 'doubao-pro-32k',
      'temperature': '0.5',
      'mode': 'agentic',
    },
  };

  // API 请求配置
  static const Map<String, String> defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-API-Key': apiKey,
    'X-Agent-Mode': 'enabled',
    'X-HTTP2-Enabled': 'true',
  };

  // 请求配置
  static const Duration timeout = Duration(seconds: 60);
  static const int maxRetries = 3;
  static const Duration retryInterval = Duration(seconds: 2);

  // HTTP/2 配置
  static const bool enableHttp2 = true;
  static const Map<String, String> http2Settings = {
    'enablePush': 'true',
    'initialWindowSize': '65535',
    'maxConcurrentStreams': '250',
    'maxFrameSize': '16384',
  };

  // TLS 配置
  static const Map<String, String> tlsSettings = {
    'certPath': 'assets/certs/cert.pem',
    'keyPath': 'assets/certs/key.pem',
    'protocols': 'h2,http/1.1',
  };
} 