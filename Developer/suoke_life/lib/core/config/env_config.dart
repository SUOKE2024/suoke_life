import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// 环境类型
enum EnvironmentType {
  development,
  staging,
  production,
}

/// 环境配置
class EnvConfig {
  /// 单例实例
  static final EnvConfig _instance = EnvConfig._internal();

  /// 工厂构造函数
  factory EnvConfig() => _instance;

  /// 内部构造函数
  EnvConfig._internal();

  /// 当前环境
  late EnvironmentType _currentEnv;

  /// API 基础URL
  late String _apiBaseUrl;

  /// DeepSeek API 密钥
  late String _deepseekApiKey;

  /// DeepSeek API 地址
  late String _deepseekApiUrl;

  /// 是否已初始化
  bool _isInitialized = false;

  /// 初始化环境配置
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // 加载.env文件
      await dotenv.load();

      // 设置当前环境
      final envString = dotenv.get('ENV', fallback: 'development');
      _currentEnv = _parseEnvType(envString);

      // 设置API基础URL
      _apiBaseUrl =
          dotenv.get('API_BASE_URL', fallback: 'http://localhost:8000');

      // 设置DeepSeek配置
      _deepseekApiKey = dotenv.get('DEEPSEEK_API_KEY',
          fallback: 'sk-7861d4a25a4b4d5facb51d696b49e321');
      _deepseekApiUrl = dotenv.get('DEEPSEEK_API_URL',
          fallback: 'https://api.deepseek.com/v1');

      _isInitialized = true;
      debugPrint('环境配置已初始化: $_currentEnv');
    } catch (e) {
      debugPrint('环境配置初始化失败: $e');
      // 使用默认值
      _currentEnv = EnvironmentType.development;
      _apiBaseUrl = 'http://localhost:8000';
      _deepseekApiKey = 'sk-7861d4a25a4b4d5facb51d696b49e321';
      _deepseekApiUrl = 'https://api.deepseek.com/v1';
      _isInitialized = true;
    }
  }

  /// 解析环境类型
  EnvironmentType _parseEnvType(String envString) {
    switch (envString.toLowerCase()) {
      case 'production':
        return EnvironmentType.production;
      case 'staging':
        return EnvironmentType.staging;
      case 'development':
      default:
        return EnvironmentType.development;
    }
  }

  /// 获取当前环境
  EnvironmentType get currentEnv => _currentEnv;

  /// 获取API基础URL
  String get apiBaseUrl => _apiBaseUrl;

  /// 获取DeepSeek API密钥
  String get deepseekApiKey => _deepseekApiKey;

  /// 获取DeepSeek API地址
  String get deepseekApiUrl => _deepseekApiUrl;

  /// 是否为开发环境
  bool get isDevelopment => _currentEnv == EnvironmentType.development;

  /// 是否为测试环境
  bool get isStaging => _currentEnv == EnvironmentType.staging;

  /// 是否为生产环境
  bool get isProduction => _currentEnv == EnvironmentType.production;
}
