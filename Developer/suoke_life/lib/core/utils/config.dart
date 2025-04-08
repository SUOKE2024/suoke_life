// 应用配置文件
// 包含各类配置信息，如API密钥、环境变量等

import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// 应用环境
enum AppEnvironment {
  /// 开发环境
  development,
  
  /// 测试环境
  test,
  
  /// 生产环境
  production,
}

/// 应用配置类
class AppConfig {
  /// 当前环境
  static AppEnvironment _environment = AppEnvironment.development;
  
  /// 获取当前环境
  static AppEnvironment get environment => _environment;
  
  /// 设置当前环境
  static void setEnvironment(AppEnvironment env) {
    _environment = env;
  }
  
  /// 是否为开发环境
  static bool get isDevelopment => _environment == AppEnvironment.development;
  
  /// 是否为测试环境
  static bool get isTest => _environment == AppEnvironment.test;
  
  /// 是否为生产环境
  static bool get isProduction => _environment == AppEnvironment.production;
  
  /// API基础URL
  static String get apiBaseUrl {
    switch (_environment) {
      case AppEnvironment.development:
        return 'https://dev-api.suoke.life';
      case AppEnvironment.test:
        return 'https://test-api.suoke.life';
      case AppEnvironment.production:
        return 'https://api.suoke.life';
    }
  }
  
  /// 是否启用调试模式
  static bool get enableDebug => !isProduction;
  
  /// 是否启用模拟数据
  static bool get useMockData => isDevelopment && _getBool('USE_MOCK_DATA');
  
  /// 百度文心一言API密钥
  static String get baiduApiKey => _getString('BAIDU_API_KEY');
  
  /// 百度文心一言密钥
  static String get baiduSecretKey => _getString('BAIDU_SECRET_KEY');
  
  /// 阿里通义千问API密钥
  static String get aliApiKey => _getString('ALI_API_KEY');
  
  /// 阿里通义千问密钥
  static String get aliSecretKey => _getString('ALI_SECRET_KEY');
  
  /// 讯飞星火API密钥
  static String get xunfeiApiKey => _getString('XUNFEI_API_KEY');
  
  /// 讯飞星火密钥
  static String get xunfeiSecretKey => _getString('XUNFEI_SECRET_KEY');
  
  /// 智谱ChatGLM API密钥
  static String get zhipuApiKey => _getString('ZHIPU_API_KEY');
  
  /// 智谱ChatGLM密钥
  static String get zhipuSecretKey => _getString('ZHIPU_SECRET_KEY');
  
  /// DeepSeek API密钥
  static String get deepseekApiKey => _getString('DEEPSEEK_API_KEY');
  
  /// OpenAI API密钥
  static String get openaiApiKey => _getString('OPENAI_API_KEY');
  
  /// 是否启用OpenAI
  static bool get enableOpenAI => _getBool('ENABLE_OPENAI');
  
  /// Google搜索API密钥
  static String get webSearchApiKey => _getString('WEB_SEARCH_API_KEY');
  
  /// Google搜索引擎ID
  static String get webSearchEngineId => _getString('WEB_SEARCH_ENGINE_ID');
  
  /// Bing搜索API密钥
  static String get bingSearchApiKey => _getString('BING_SEARCH_API_KEY');
  
  /// 初始化配置
  static Future<void> init() async {
    try {
      // 加载.env文件
      await dotenv.load();
      
      // 根据环境变量设置当前环境
      final envStr = _getString('APP_ENV').toLowerCase();
      if (envStr == 'production') {
        _environment = AppEnvironment.production;
      } else if (envStr == 'test') {
        _environment = AppEnvironment.test;
      } else {
        _environment = AppEnvironment.development;
      }
      
      if (kDebugMode) {
        print('应用环境: $_environment');
      }
    } catch (e) {
      if (kDebugMode) {
        print('初始化配置失败: $e');
      }
    }
  }
  
  /// 获取字符串配置
  static String _getString(String key, [String defaultValue = '']) {
    try {
      return dotenv.env[key] ?? defaultValue;
    } catch (e) {
      if (kDebugMode) {
        print('获取配置[$key]失败: $e');
      }
      return defaultValue;
    }
  }
  
  /// 获取布尔配置
  static bool _getBool(String key, [bool defaultValue = false]) {
    try {
      final value = dotenv.env[key]?.toLowerCase();
      if (value == null) return defaultValue;
      return value == 'true' || value == '1' || value == 'yes';
    } catch (e) {
      if (kDebugMode) {
        print('获取配置[$key]失败: $e');
      }
      return defaultValue;
    }
  }
  
  /// 获取整数配置
  static int _getInt(String key, [int defaultValue = 0]) {
    try {
      final value = dotenv.env[key];
      if (value == null) return defaultValue;
      return int.tryParse(value) ?? defaultValue;
    } catch (e) {
      if (kDebugMode) {
        print('获取配置[$key]失败: $e');
      }
      return defaultValue;
    }
  }
  
  /// 获取双精度浮点数配置
  static double _getDouble(String key, [double defaultValue = 0.0]) {
    try {
      final value = dotenv.env[key];
      if (value == null) return defaultValue;
      return double.tryParse(value) ?? defaultValue;
    } catch (e) {
      if (kDebugMode) {
        print('获取配置[$key]失败: $e');
      }
      return defaultValue;
    }
  }
} 