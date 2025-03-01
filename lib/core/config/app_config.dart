import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'environment.dart';

/// 应用配置类 - 单例模式
class AppConfig {
  // 单例实例
  static late AppConfig _instance;
  static AppConfig get instance => _instance;
  
  // 包信息
  late PackageInfo _packageInfo;
  
  // 应用信息
  late String _appName;
  late String _appVersion;
  late String _buildNumber;
  
  // 配置数据
  late Map<String, dynamic> _config;
  
  // 预设主题模式
  late ThemeMode _defaultThemeMode;
  
  // 预设语言
  late Locale _defaultLocale;
  
  /// 私有构造函数
  AppConfig._();
  
  /// 初始化应用配置
  static Future<void> initialize() async {
    final instance = AppConfig._();
    await instance._initialize();
    _instance = instance;
  }
  
  /// 内部初始化方法
  Future<void> _initialize() async {
    // 加载包信息
    _packageInfo = await PackageInfo.fromPlatform();
    _appName = _packageInfo.appName;
    _appVersion = _packageInfo.version;
    _buildNumber = _packageInfo.buildNumber;
    
    // 加载配置文件
    final configPath = 'assets/config/${Environment.current.name}_config.json';
    final configString = await rootBundle.loadString(configPath);
    _config = json.decode(configString) as Map<String, dynamic>;
    
    // 设置默认主题模式
    final themeModeName = _config['defaultThemeMode'] as String? ?? 'system';
    _defaultThemeMode = _parseThemeMode(themeModeName);
    
    // 设置默认语言
    final localeName = _config['defaultLocale'] as String? ?? 'zh_CN';
    final localeParts = localeName.split('_');
    _defaultLocale = Locale(localeParts[0], localeParts.length > 1 ? localeParts[1] : null);
  }
  
  /// 解析主题模式字符串
  ThemeMode _parseThemeMode(String mode) {
    switch (mode.toLowerCase()) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      case 'system':
      default:
        return ThemeMode.system;
    }
  }
  
  // 属性访问器
  
  /// 应用名称
  String get appName => _appName;
  
  /// 应用版本
  String get appVersion => _appVersion;
  
  /// 构建编号
  String get buildNumber => _buildNumber;
  
  /// 完整版本号 (x.y.z+build)
  String get fullVersion => '$_appVersion+$_buildNumber';
  
  /// 默认主题模式
  ThemeMode get defaultThemeMode => _defaultThemeMode;
  
  /// 默认语言
  Locale get defaultLocale => _defaultLocale;
  
  /// 获取配置值
  T? getValue<T>(String key) {
    if (!_config.containsKey(key)) {
      return null;
    }
    
    final value = _config[key];
    if (value is T) {
      return value;
    }
    
    return null;
  }
  
  /// 获取嵌套配置值
  T? getNestedValue<T>(List<String> keys) {
    dynamic current = _config;
    
    for (final key in keys) {
      if (current is! Map<String, dynamic> || !current.containsKey(key)) {
        return null;
      }
      current = current[key];
    }
    
    if (current is T) {
      return current;
    }
    
    return null;
  }
} 