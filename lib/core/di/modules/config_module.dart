import 'package:get_it/get_it.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../../config/app_config.dart';

// 注册配置模块的依赖
//
// 在这里注册 AppConfig, DotEnv 等配置相关的依赖
void registerConfigModule(GetIt getIt) {
  // 加载 .env 文件
  dotenv.load();

  // 注册 AppConfig 为单例
  getIt.registerLazySingleton<AppConfig>(() => AppConfig(
      knowledgeGraphApiBaseUrl: 'YOUR_KNOWLEDGE_GRAPH_API_BASE_URL',
      llmApiBaseUrl: 'YOUR_LLM_API_BASE_URL',
      multimodalApiBaseUrl: 'YOUR_MULTIMODAL_API_BASE_URL'));
} 