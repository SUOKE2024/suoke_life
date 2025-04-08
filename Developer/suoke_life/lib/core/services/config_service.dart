// 配置服务类
// 用于管理应用配置和API密钥

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logging/logging.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 环境配置枚举
enum Environment {
  /// 开发环境
  development,
  
  /// 测试环境
  testing,
  
  /// 生产环境
  production,
}

/// 配置服务类
class ConfigService {
  static final Logger _logger = Logger('ConfigService');
  
  /// 共享偏好实例
  final SharedPreferences _prefs;
  
  /// 安全存储实例
  final FlutterSecureStorage _secureStorage;
  
  /// 当前环境
  Environment _environment;
  
  /// 应用版本
  String _appVersion = '1.0.0';
  
  /// 应用构建号
  String _buildNumber = '1';
  
  static const String _envKey = 'api_environment';
  static const String _modelProviderKey = 'model_provider';
  
  /// 构造函数
  ConfigService(this._prefs, this._secureStorage, {Environment? environment})
      : _environment = environment ?? Environment.development {
    _initializeAppInfo();
  }
  
  /// 初始化应用信息
  Future<void> _initializeAppInfo() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      _appVersion = packageInfo.version;
      _buildNumber = packageInfo.buildNumber;
      _logger.info('应用版本: $_appVersion, 构建号: $_buildNumber');
    } catch (e) {
      _logger.warning('获取应用信息失败: $e');
    }
  }
  
  /// 获取当前环境
  Environment get environment => _environment;
  
  /// 设置当前环境
  Future<void> setEnvironment(Environment env) async {
    _environment = env;
    await _prefs.setString(_envKey, env.toString().split('.').last);
    _logger.info('已设置环境为: $env');
  }
  
  /// 获取API基础URL
  String getApiBaseUrl() {
    switch (_environment) {
      case Environment.development:
        return 'http://dev-api.suoke.life';
      case Environment.testing:
        return 'http://test-api.suoke.life';
      case Environment.production:
        return 'https://api.suoke.life';
    }
  }
  
  /// 获取百度API密钥
  String? getBaiduApiKey() {
    return _getSecureValue('baidu_api_key');
  }
  
  /// 获取百度API密钥
  String? getBaiduSecretKey() {
    return _getSecureValue('baidu_secret_key');
  }
  
  /// 获取阿里API密钥
  String? getAlibabaApiKey() {
    return _getSecureValue('alibaba_api_key');
  }
  
  /// 获取讯飞API密钥
  String? getIFlytekApiKey() {
    return _getSecureValue('iflytek_api_key');
  }
  
  /// 获取大模型首选提供商
  String getPreferredModelProvider() {
    return _prefs.getString(_modelProviderKey) ?? 'baidu';
  }
  
  /// 设置大模型首选提供商
  Future<bool> setPreferredModelProvider(String provider) async {
    return _prefs.setString(_modelProviderKey, provider);
  }
  
  /// 获取是否使用流式响应
  bool getUseStreamingResponse() {
    return _prefs.getBool('use_streaming') ?? true;
  }
  
  /// 设置是否使用流式响应
  Future<void> setUseStreamingResponse(bool useStreaming) async {
    await _prefs.setBool('use_streaming', useStreaming);
  }
  
  /// 获取大模型温度参数
  double getModelTemperature() {
    return _prefs.getDouble('model_temperature') ?? 0.7;
  }
  
  /// 设置大模型温度参数
  Future<void> setModelTemperature(double temperature) async {
    await _prefs.setDouble('model_temperature', temperature);
  }
  
  /// 获取网络搜索API密钥
  String? getWebSearchApiKey() {
    return _getSecureValue('web_search_api_key');
  }
  
  /// 设置网络搜索API密钥
  Future<void> setWebSearchApiKey(String apiKey) async {
    await _setSecureValue('web_search_api_key', apiKey);
  }
  
  /// 获取智能体配置
  Future<Map<String, Map<String, dynamic>>?> getAgentConfigs() async {
    final configsJson = _prefs.getString('agent_configs');
    if (configsJson == null) {
      return null;
    }
    
    try {
      final Map<String, dynamic> decoded = json.decode(configsJson);
      final result = <String, Map<String, dynamic>>{};
      
      decoded.forEach((key, value) {
        if (value is Map) {
          result[key] = Map<String, dynamic>.from(value);
        }
      });
      
      return result;
    } catch (e) {
      _logger.warning('解析智能体配置失败: $e');
      return null;
    }
  }
  
  /// 保存智能体配置
  Future<void> saveAgentConfig(String agentId, Map<String, dynamic> config) async {
    // 获取现有配置
    final configs = await getAgentConfigs() ?? {};
    
    // 更新配置
    configs[agentId] = config;
    
    // 保存到SharedPreferences
    await _prefs.setString('agent_configs', json.encode(configs));
  }
  
  /// 获取文件搜索配置
  Map<String, dynamic> getFileSearchConfig() {
    final configJson = _prefs.getString('file_search_config');
    if (configJson == null) {
      return {
        'search_paths': ['assets/knowledge_base'],
        'max_results': 10,
        'use_semantic_search': true,
      };
    }
    
    try {
      return json.decode(configJson);
    } catch (e) {
      _logger.warning('解析文件搜索配置失败: $e');
      return {
        'search_paths': ['assets/knowledge_base'],
        'max_results': 10,
        'use_semantic_search': true,
      };
    }
  }
  
  /// 设置文件搜索配置
  Future<void> setFileSearchConfig(Map<String, dynamic> config) async {
    await _prefs.setString('file_search_config', json.encode(config));
  }
  
  /// 获取应用版本
  String getAppVersion() => _appVersion;
  
  /// 获取构建号
  String getBuildNumber() => _buildNumber;
  
  /// 获取应用完整版本
  String getFullVersion() => '$_appVersion+$_buildNumber';
  
  /// 从安全存储获取值
  Future<String?> _getSecureValue(String key) async {
    try {
      return await _secureStorage.read(key: key);
    } catch (e) {
      _logger.warning('从安全存储读取失败: $key, 错误: $e');
      return null;
    }
  }
  
  /// 向安全存储写入值
  Future<void> _setSecureValue(String key, String value) async {
    try {
      await _secureStorage.write(key: key, value: value);
    } catch (e) {
      _logger.warning('写入安全存储失败: $key, 错误: $e');
    }
  }
  
  /// 清除所有配置
  Future<void> clearAllConfigurations() async {
    try {
      await _prefs.clear();
      await _secureStorage.deleteAll();
      _logger.info('已清除所有配置');
    } catch (e) {
      _logger.severe('清除配置失败: $e');
      rethrow;
    }
  }
  
  /// 获取API访问令牌
  Future<String?> getApiToken() async {
    return _getSecureValue('api_token');
  }
  
  /// 设置API访问令牌
  Future<void> setApiToken(String token) async {
    await _setSecureValue('api_token', token);
  }
  
  /// 获取API密钥
  Future<String?> getApiKey(String provider) async {
    return _getSecureValue('${provider}_api_key');
  }
  
  /// 设置API密钥
  Future<void> setApiKey(String provider, String apiKey) async {
    await _setSecureValue('${provider}_api_key', apiKey);
  }
  
  /// 获取模型配置
  Map<String, dynamic> getModelConfig() {
    final configJson = _prefs.getString('model_config');
    if (configJson != null) {
      // 在实际应用中，这里应该解析JSON
      return {'temperature': 0.7, 'maxTokens': 2048};
    }
    return {'temperature': 0.7, 'maxTokens': 2048};
  }
  
  /// 设置模型配置
  Future<bool> setModelConfig(Map<String, dynamic> config) async {
    // 在实际应用中，这里应该序列化为JSON
    return _prefs.setString('model_config', config.toString());
  }
  
  /// 获取RAG配置
  Map<String, dynamic> getRAGConfig() {
    return {
      'enableRAG': _prefs.getBool('enable_rag') ?? true,
      'maxChunks': _prefs.getInt('max_chunks') ?? 5,
      'similarityThreshold': _prefs.getDouble('similarity_threshold') ?? 0.75,
    };
  }
  
  /// 设置是否启用RAG
  Future<bool> setEnableRAG(bool enable) async {
    return _prefs.setBool('enable_rag', enable);
  }
  
  /// 设置最大块数
  Future<bool> setMaxChunks(int maxChunks) async {
    return _prefs.setInt('max_chunks', maxChunks);
  }
  
  /// 设置相似度阈值
  Future<bool> setSimilarityThreshold(double threshold) async {
    return _prefs.setDouble('similarity_threshold', threshold);
  }
} 