import 'dart:io' if (dart.library.html) 'dart:html';
import 'package:flutter_dotenv/flutter_dotenv.dart';

abstract class EnvConfigBase {
  // API 配置
  String get apiUrl;
  String get apiKey;
  
  // AI 服务配置
  String get aiServiceUrl;
  String get aiApiKey;
  
  // 数据库配置
  String get dbName;
  int get dbVersion;
  
  // 环境配置
  String get env;
  bool get isDevelopment => env == 'development';
  bool get isProduction => env == 'production';
  bool get isTest => env == 'test';
  
  // 缓存配置
  Duration get defaultCacheDuration => const Duration(hours: 1);
  int get maxCacheSize => 100;
  
  // 安全配置
  String get encryptionKey;
  Duration get tokenExpiration => const Duration(days: 7);
}

class EnvConfigBase {
  static late EnvConfigBase _instance;
  late String aiApiKey;

  EnvConfigBase._();

  static Future<void> init() async {
    _instance = EnvConfigBase._();
    await _instance._load();
  }

  static EnvConfigBase get instance => _instance;

  Future<void> _load() async {
    try {
      // Flutter 环境
      await dotenv.load(fileName: '.env');
      aiApiKey = dotenv.env['AI_API_KEY'] ?? '';
    } catch (e) {
      if (identical(0, 0.0)) {
        // Web 平台
        // TODO: 实现 Web 平台的配置加载
        throw UnimplementedError('Web platform not supported yet');
      } else {
        // Native 平台
        final file = File('.env');
        if (!await file.exists()) {
          throw Exception('Environment file .env not found');
        }

        final lines = await file.readAsLines();
        final env = Map.fromEntries(
          lines
              .where((line) => line.isNotEmpty && !line.startsWith('#'))
              .map((line) => line.split('='))
              .where((parts) => parts.length == 2)
              .map((parts) => MapEntry(parts[0].trim(), parts[1].trim())),
        );

        aiApiKey = env['AI_API_KEY'] ?? '';
      }
    }

    if (aiApiKey.isEmpty) {
      throw Exception('AI_API_KEY not found in environment file');
    }
  }
} 