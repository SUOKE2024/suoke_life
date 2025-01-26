import 'package:get/get.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvConfig extends GetxService {
  static EnvConfig get to => Get.find();

  late final String apiKey;
  late final String baseUrl;
  late final String environment;

  Future<EnvConfig> init() async {
    // 加载环境变量
    await dotenv.load(fileName: '.env');

    // 初始化配置
    environment = dotenv.env['ENV'] ?? 'development';
    apiKey = dotenv.env['DOUBAO_API_KEY'] ?? '';
    baseUrl = dotenv.env['DOUBAO_API_URL'] ??
        'https://ark.cn-beijing.volces.com/api/v3';

    print('EnvConfig initialized: $environment');
    return this;
  }

  // API 相关配置
  String get doubaoApiKey => dotenv.env['DOUBAO_API_KEY'] ?? '';
  String get doubaoApiUrl => dotenv.env['DOUBAO_API_URL'] ?? '';

  // 模型配置
  String get doubaoPro32kEp => dotenv.env['DOUBAO_PRO_32K_EP'] ?? '';
  String get doubaoPro128kEp => dotenv.env['DOUBAO_PRO_128K_EP'] ?? '';
  String get doubaoEmbeddingEp => dotenv.env['DOUBAO_EMBEDDING_EP'] ?? '';
}
