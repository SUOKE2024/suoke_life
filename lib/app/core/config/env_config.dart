import 'package:get/get.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvConfig extends GetxService {
  static EnvConfig get to => Get.find();
  
  late final String apiKey;
  late final String baseUrl;
  late final String environment;

  Future<EnvConfig> init() async {
    // 加载环境变量
    await dotenv.load(fileName: ".env");
    
    // 初始化配置
    environment = dotenv.env['ENVIRONMENT'] ?? 'development';
    apiKey = dotenv.env['API_KEY'] ?? '';
    baseUrl = dotenv.env['BASE_URL'] ?? 'https://api.doubao.com';
    
    print('EnvConfig initialized: $environment');
    return this;
  }

  // 获取环境变量的方法
  String getString(String key) {
    return dotenv.env[key] ?? '';
  }

  int? getInt(String key) {
    final value = dotenv.env[key];
    return value != null ? int.tryParse(value) : null;
  }

  double? getDouble(String key) {
    final value = dotenv.env[key];
    return value != null ? double.tryParse(value) : null;
  }

  bool getBool(String key) {
    final value = dotenv.env[key];
    return value?.toLowerCase() == 'true';
  }

  // 环境判断
  bool get isDevelopment => environment == 'development';
  bool get isProduction => environment == 'production';
  bool get isStaging => environment == 'staging';

  // 常用配置获取
  String get doubaoApiKey => getString('DOUBAO_API_KEY');
  String get doubaoApiUrl => getString('DOUBAO_API_URL');
  String get doubaoPro32kEp => getString('DOUBAO_PRO_32K_EP');
  String get doubaoPro128kEp => getString('DOUBAO_PRO_128K_EP');
  String get doubaoEmbeddingKey => getString('DOUBAO_EMBEDDING_KEY');
  String get doubaoAccessToken => getString('DOUBAO_ACCESS_TOKEN');
} 