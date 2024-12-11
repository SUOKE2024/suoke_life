import 'dart:io';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// AI配置管理
class AIConfig {
  static Future<void> load() async {
    final env = Platform.environment['SUOKE_ENV'] ?? 'development';
    
    // 加载AI配置
    await dotenv.load(fileName: 'config/$env/ai.env');
  }

  // 豆包API密钥
  static String get doubaoApiKey => dotenv.env['DOUBAO_API_KEY'] ?? '';
  
  // 模型ID配置
  static String get xiaoiModelId => dotenv.env['XIAOI_MODEL_ID'] ?? '';
  static String get laokeModelId => dotenv.env['LAOKE_MODEL_ID'] ?? '';
  static String get embeddingModelId => dotenv.env['EMBEDDING_MODEL_ID'] ?? '';
  
  // AI服务配置
  static String get aiServiceHost => dotenv.env['AI_SERVICE_HOST'] ?? 'localhost';
  static int get aiServicePort => int.tryParse(dotenv.env['AI_SERVICE_PORT'] ?? '') ?? 5000;
  
  // 模型参数配置
  static int get maxTokens => int.tryParse(dotenv.env['MAX_TOKENS'] ?? '') ?? 2048;
  static double get temperature => double.tryParse(dotenv.env['TEMPERATURE'] ?? '') ?? 0.7;
  static int get topK => int.tryParse(dotenv.env['TOP_K'] ?? '') ?? 50;
  static double get topP => double.tryParse(dotenv.env['TOP_P'] ?? '') ?? 0.9;
  
  // 资源限制配置
  static int get maxConcurrentRequests => int.tryParse(dotenv.env['MAX_CONCURRENT_REQUESTS'] ?? '') ?? 5;
  static int get requestTimeout => int.tryParse(dotenv.env['REQUEST_TIMEOUT'] ?? '') ?? 30000;
} 