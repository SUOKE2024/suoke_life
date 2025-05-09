/// 应用程序全局常量定义
class AppConstants {
  const AppConstants._();

  /// 应用基本信息
  static const String appName = '索克生活';
  static const String appVersion = '0.1.0';

  /// 屏幕适配基准尺寸
  static const double designWidth = 375.0;
  static const double designHeight = 812.0;

  /// API相关常量
  static const int defaultApiTimeoutSeconds = 30;
  static const int defaultConnectTimeoutSeconds = 10;
  static const String apiBaseUrlKey = 'API_BASE_URL';

  /// 本地存储键
  static const String tokenKey = 'auth_token';
  static const String userInfoKey = 'user_info';
  static const String settingsKey = 'app_settings';

  /// 体质类型常量
  static const List<String> constitutionTypes = [
    '平和质',
    '气虚质',
    '阳虚质',
    '阴虚质',
    '痰湿质',
    '湿热质',
    '血瘀质',
    '气郁质',
    '特禀质',
  ];

  /// 路由名称
  static const String homeRoute = '/home';
  static const String loginRoute = '/login';
  static const String registerRoute = '/register';
  static const String profileRoute = '/profile';
  static const String constitutionTestRoute = '/constitution_test';
  static const String constitutionResultRoute = '/constitution_result';

  /// 错误消息
  static const String networkErrorMessage = '网络连接失败，请检查您的网络设置';
  static const String serverErrorMessage = '服务器错误，请稍后重试';
  static const String timeoutErrorMessage = '请求超时，请稍后重试';
  static const String unknownErrorMessage = '发生未知错误，请稍后重试';
}
