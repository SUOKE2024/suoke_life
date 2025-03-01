/// 应用常量

/// API 常量
class ApiConstants {
  /// API 基础URL
  static const String baseUrl = 'http://118.31.223.213/api';
  
  /// API 版本
  static const String apiVersion = 'v1';
  
  /// 完整 API URL
  static const String apiUrl = '$baseUrl/$apiVersion';
  
  /// 连接超时时间（毫秒）
  static const int connectionTimeout = 30000;
  
  /// 接收超时时间（毫秒）
  static const int receiveTimeout = 30000;
  
  /// 健康数据API路径
  static const String healthDataPath = '/health';
  
  /// 用户API路径
  static const String userPath = '/users';
  
  /// 认证API路径
  static const String authPath = '/auth';
  
  /// 知识图谱API路径
  static const String knowledgePath = '/knowledge';
  
  /// 文件上传API路径
  static const String uploadPath = '/upload';
  
  /// 禁止直接实例化
  ApiConstants._();
}

/// 本地存储键常量
class PreferenceKeys {
  /// 用户认证令牌
  static const String authToken = 'auth_token';
  
  /// 用户信息
  static const String userInfo = 'user_info';
  
  /// 主题模式
  static const String themeMode = 'theme_mode';
  
  /// 是否首次启动
  static const String isFirstLaunch = 'is_first_launch';
  
  /// 用户语言选择
  static const String userLanguage = 'user_language';
  
  /// 上次同步时间
  static const String lastSyncTime = 'last_sync_time';
  
  /// 离线数据库版本
  static const String databaseVersion = 'database_version';
  
  /// 禁止直接实例化
  PreferenceKeys._();
}

/// 数据库常量
class DatabaseConstants {
  /// 数据库名称
  static const String databaseName = 'suoke_life.db';
  
  /// 数据库版本
  static const int databaseVersion = 1;
  
  /// 用户表
  static const String userTable = 'users';
  
  /// 健康数据表
  static const String healthDataTable = 'health_data';
  
  /// 知识图谱表
  static const String knowledgeNodeTable = 'knowledge_nodes';
  
  /// 知识关系表
  static const String knowledgeRelationTable = 'knowledge_relations';
  
  /// 中医处方表
  static const String tcmPrescriptionTable = 'tcm_prescriptions';
  
  /// 药材表
  static const String medicinalTable = 'medicinals';
  
  /// 禁止直接实例化
  DatabaseConstants._();
}

/// 路由常量
class RouteConstants {
  /// 启动页
  static const String splash = '/';
  
  /// 主页
  static const String home = '/home';
  
  /// 登录页
  static const String login = '/login';
  
  /// 注册页
  static const String register = '/register';
  
  /// 聊天页
  static const String chat = '/chat';
  
  /// 服务页
  static const String services = '/services';
  
  /// 探索页
  static const String explore = '/explore';
  
  /// 生活页
  static const String life = '/life';
  
  /// 我的页
  static const String profile = '/profile';
  
  /// 知识图谱可视化
  static const String knowledgeGraph = '/knowledge-graph';
  
  /// 健康数据
  static const String healthData = '/health-data';
  
  /// 禁止直接实例化
  RouteConstants._();
}

/// 资源常量
class AssetConstants {
  /// 图片路径
  static const String imagesPath = 'assets/images/';
  
  /// 图标路径
  static const String iconsPath = 'assets/icons/';
  
  /// 动画路径
  static const String animationsPath = 'assets/animations/';
  
  /// 应用图标
  static const String appIcon = '${imagesPath}app_icon.jpg';
  
  /// Logo
  static const String logo = '${imagesPath}logo.png';
  
  /// 默认头像
  static const String defaultAvatar = '${imagesPath}default_avatar.png';
  
  /// 老克头像
  static const String laokeAvatar = '${imagesPath}laoke_avatar.png';
  
  /// 小艾头像
  static const String xiaoaiAvatar = '${imagesPath}xiaoai_avatar.png';
  
  /// 小克头像
  static const String xiaokeAvatar = '${imagesPath}xiaoke_avatar.png';
  
  /// 禁止直接实例化
  AssetConstants._();
}

/// 错误消息常量
class ErrorMessages {
  /// 网络错误
  static const String networkError = '网络连接错误，请检查您的网络连接';
  
  /// 服务器错误
  static const String serverError = '服务器错误，请稍后再试';
  
  /// 未授权错误
  static const String unauthorizedError = '未授权，请重新登录';
  
  /// 请求超时
  static const String timeoutError = '请求超时，请稍后再试';
  
  /// 未知错误
  static const String unknownError = '发生未知错误，请稍后再试';
  
  /// 解析错误
  static const String parseError = '数据解析错误，请联系客服';
  
  /// 禁止直接实例化
  ErrorMessages._();
}

/// 应用常量
class AppConstants {
  /// 应用名称
  static const String appName = '索克生活';
  
  /// 应用版本
  static const String appVersion = '1.0.0';
  
  /// 构建号
  static const String buildNumber = '1';
  
  /// 缓存过期时间（秒）
  static const int cacheExpirationSeconds = 3600 * 24; // 1天
  
  /// 页面大小
  static const int defaultPageSize = 20;
  
  /// 最大重试次数
  static const int maxRetryCount = 3;
  
  /// 禁止直接实例化
  AppConstants._();
} 