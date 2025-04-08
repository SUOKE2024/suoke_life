/// 应用全局常量定义
///
/// 包含各种全局使用的常量值，如通知相关配置、传感器配置、缓存路径等

/// 应用基本常量
class AppConstants {
  // 应用基本信息
  static const String appName = "Suoke Life";
  static const String appVersion = "1.0.0";
  
  // 后台服务配置
  static const String backgroundServiceName = "com.suoke.life.background_service";
  static const String backgroundServiceDescription = "Suoke Life 后台服务";
  static const int backgroundServiceNotificationId = 1001;
  
  // 传感器配置
  static const String sensorConfigKey = "sensor_config";
  static const String sensorDataDirectoryName = "sensor_data";
  static const int sensorDataSyncInterval = 30; // 分钟
  static const int sensorDataRetentionDays = 30; // 天
  static const int sensorDataBatchSize = 100; // 条
  
  // 缓存配置
  static const int cacheSizeMax = 50 * 1024 * 1024; // 50MB
  static const int cacheExpirationDays = 7; // 天
  
  // 通知通道
  static const String defaultNotificationChannelId = "suoke_life_default_channel";
  static const String defaultNotificationChannelName = "一般通知";
  static const String backgroundServiceChannelId = "suoke_life_background_channel";
  static const String backgroundServiceChannelName = "后台服务";
  static const String healthAlertChannelId = "suoke_life_health_alert_channel";
  static const String healthAlertChannelName = "健康提醒";
  
  // 性能配置
  static const int connectionTimeout = 10000; // 毫秒
  static const int responseTimeout = 15000; // 毫秒
  
  // 工作管理器任务
  static const String syncSensorDataTask = "syncSensorData";
  static const String cleanupOldDataTask = "cleanupOldData";
  static const int taskRetryDelayMinutes = 15;
  
  // 首选项键名
  static const String prefsKeyFirstRun = "first_run";
  static const String prefsKeyUserId = "user_id";
  static const String prefsKeyIsLoggedIn = "is_logged_in";
  static const String prefsKeyToken = "auth_token";
  static const String prefsKeyTokenExpiry = "auth_token_expiry";
  static const String prefsKeyBackgroundSensingEnabled = "background_sensing_enabled";
  static const String prefsKeyDataCollectionFrequency = "sensor_data_collection_frequency";
  static const String prefsKeyShareSensorData = "share_sensor_data";
  
  // 安全配置
  static const String secureStorageKey = "suoke_life_secure_storage";
  static const int passwordMinLength = 8;
  
  // 本地化
  static const String defaultLocale = "zh-CN";
  
  // 主题
  static const String defaultThemeMode = "system";
  
  // 消息队列
  static const int messageQueueLimit = 100;
  
  // 健康相关常量
  static const int constitutionAssessmentQuestions = 18;
  static const int minimumScoreForType = 7;
  
  // 目录和文件名
  static const String logsDirectoryName = "logs";
  static const String cacheDirectoryName = "cache";
  static const String diagnosticDataFileName = "diagnostic_data.json";
  static const String userPreferencesFileName = "user_preferences.json";
  
  // 特殊值
  static const String placeholderUserId = "guest_user";
  static const String defaultDeviceId = "unknown_device";
  
  // 隐私设置
  static const bool defaultDataCollectionEnabled = false;
  static const bool defaultLocationEnabled = false;
  
  // 应用状态
  static const int appStateActive = 1;
  static const int appStateInactive = 2;
  static const int appStateBackground = 3;
  
  // 网络连接状态
  static const int networkStatusConnected = 1;
  static const int networkStatusOffline = 0;
  
  // 时间格式
  static const String defaultDateFormat = "yyyy-MM-dd";
  static const String defaultTimeFormat = "HH:mm:ss";
  static const String defaultDateTimeFormat = "yyyy-MM-dd HH:mm:ss";
} 