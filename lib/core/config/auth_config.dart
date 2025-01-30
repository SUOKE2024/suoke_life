class AuthConfig {
  // 第三方登录配置
  static const Map<String, Map<String, String>> socialConfig = {
    'wechat': {
      'appId': 'your_wechat_app_id',
      'appSecret': 'your_wechat_app_secret',
    },
    'google': {
      'clientId': 'your_google_client_id',
      'clientSecret': 'your_google_client_secret',
    },
    'apple': {
      'serviceId': 'your_apple_service_id',
      'teamId': 'your_apple_team_id',
    },
  };

  // 生物识别配置
  static const biometricConfig = {
    'enabled': true,
    'localizedReason': '请验证指纹以登录',
    'allowDeviceCredentials': true,
  };

  // 登录配置
  static const loginConfig = {
    'maxAttempts': 5,
    'lockoutDuration': Duration(minutes: 30),
    'rememberMeDuration': Duration(days: 30),
  };
} 