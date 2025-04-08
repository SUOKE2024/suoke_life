/// API常量
///
/// 定义API相关的常量，如基础URL、端点和超时设置
class ApiConstants {
  ApiConstants._();

  // 环境配置
  static String environment = 'prod'; // 默认为生产环境，可通过配置更改

  // 获取基于环境的服务基础URL
  static String get apiBaseUrl => _getBaseUrl();
  static String get baseUrl => apiBaseUrl; // 兼容性
  static String get authServiceUrl => _getAuthServiceUrl();
  static String get userServiceUrl => _getUserServiceUrl();
  
  /// 连接测试URL
  static String get connectionTestUrl => '$apiBaseUrl/health';
  
  // 不同环境的地址配置
  static final Map<String, String> _apiBaseUrls = {
    'dev': 'http://localhost:8080/api',
    'test': 'http://test.suoke.life/api',
    'prod': 'http://118.31.223.213/api',
  };
  
  static final Map<String, String> _authServiceUrls = {
    'dev': 'http://localhost:8081/auth',
    'test': 'http://test.suoke.life/auth',
    'prod': 'http://118.31.223.213/auth',
  };
  
  static final Map<String, String> _userServiceUrls = {
    'dev': 'http://localhost:8082/api/users',
    'test': 'http://test.suoke.life/api/users',
    'prod': 'http://118.31.223.213/api/users',
  };
  
  // 私有方法获取当前环境的URL
  static String _getBaseUrl() {
    return _apiBaseUrls[environment] ?? _apiBaseUrls['prod']!;
  }
  
  static String _getAuthServiceUrl() {
    return _authServiceUrls[environment] ?? _authServiceUrls['prod']!;
  }
  
  static String _getUserServiceUrl() {
    return _userServiceUrls[environment] ?? _userServiceUrls['prod']!;
  }
  
  // 设置环境
  static void setEnvironment(String env) {
    if (_apiBaseUrls.containsKey(env)) {
      environment = env;
    }
  }

  /// 用户端点
  static const String userEndpoint = '/users';
  
  /// 健康数据路径
  static const String healthDataPath = '/health-data';
  
  /// AI端点
  static const String aiEndpoint = '/ai';
  
  /// 认证端点
  static const String authEndpoint = '/auth';
  
  /// 登录路径
  static const String loginPath = '/auth/login';
  
  /// 注册路径
  static const String registerPath = '/auth/register';
  
  /// 刷新令牌路径
  static const String refreshTokenPath = '/auth/refresh-token';
  
  /// 登出路径
  static const String logoutPath = '/auth/logout';
  
  /// 生物识别注册路径
  static const String registerBiometricPath = '/auth/register-biometric';
  
  /// 生物识别验证路径
  static const String verifyBiometricPath = '/auth/verify-biometric';
  
  /// 会话路径
  static const String sessionsPath = '/auth/sessions';

  /// 老克服务基础URL 
  static String get laokeServiceBaseUrl => '$apiBaseUrl/laoke';

  /// 用户API路径
  static const String users = '/users';
  
  /// 用户个人资料路径
  static const String profilePath = '/users/profile';
  
  /// 用户健康档案路径
  static const String healthProfilePath = '/users/health-profile';
  
  /// 用户知识偏好路径
  static const String knowledgePreferencesPath = '/users/knowledge-preferences';
  
  /// 用户社交分享路径
  static const String socialSharesPath = '/social-shares';
  
  /// 用户匹配路径
  static const String userMatchesPath = '/user-matches';

  /// RAG服务API路径
  static const String rag = '/rag';

  /// 健康API路径
  static const String health = '/health';

  /// 生活方式API路径
  static const String life = '/life';

  /// 搜索API路径
  static const String search = '/search';

  /// 偏好设置API路径
  static const String preferences = '/preferences';

  /// 消息API路径
  static const String messages = '/messages';

  /// 探索API路径
  static const String explore = '/explore';

  /// 知识图谱API路径
  static const String knowledge = '/knowledge';

  /// 商品API路径
  static const String products = '/products';

  /// 订单API路径
  static const String orders = '/orders';

  /// 活动API路径
  static const String activities = '/activities';

  /// 通知API路径
  static const String notifications = '/notifications';

  /// 文件上传API路径
  static const String upload = '/upload';

  /// 诊断API路径
  static const String diagnosis = '/diagnosis';

  /// 体质评估API路径
  static const String constitution = '/constitution';

  /// 食疗API路径
  static const String dietTherapy = '/diet-therapy';

  /// 农产品API路径
  static const String agriculture = '/agriculture';

  /// 认证API路径
  static const String auth = '/auth';

  // 请求超时配置
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 15);
  static const Duration sendTimeout = Duration(seconds: 15);
  
  // 重试配置
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 1);
}
