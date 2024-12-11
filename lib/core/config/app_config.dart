class AppConfig {
  static const String appName = '索克生活';
  static const String version = '1.0.0';
  
  // 环境配置
  static const bool isDevelopment = true;
  static const String baseUrl = isDevelopment
      ? 'https://dev-api.suoke.life'
      : 'https://api.suoke.life';
  
  // 缓存配置
  static const int cacheMaxAge = 7 * 24 * 60 * 60; // 7天
  static const int cacheMaxSize = 32 * 1024 * 1024; // 32MB
  
  // 主题配置
  static const bool enableDarkMode = true;
  
  // 功能开关
  static const bool enableLog = true;
  static const bool enableCrashReport = true;
  
  // API 配置
  static const int apiTimeout = 10000; // 10秒
  static const int apiRetryCount = 3;
  
  // 其他配置
  static const String privacyUrl = 'https://www.suoke.life/privacy';
  static const String termsUrl = 'https://www.suoke.life/terms';
  static const String aboutUrl = 'https://www.suoke.life/about';
} 