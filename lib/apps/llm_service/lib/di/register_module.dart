import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/services/agent_memory_service.dart'; // 导入 AgentMemoryService
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart'; // 确保导入 LocalStorageService
import 'package:suoke_life/apps/llm_service/lib/services/llm_service.dart'; // 导入 LLMService
import 'package:suoke_life/core/config/app_config.dart'; // 导入 AppConfig
import 'package:suoke_life/core/network/knowledge_graph_client.dart'; // 导入 KnowledgeGraphClient
import 'package:suoke_life/core/services/health_profile_service.dart'; // 导入 HealthProfileService
import 'package:suoke_life/core/services/rag/context_compression_strategy.dart'; // 导入 ContextCompressionStrategy
import 'package:suoke_life/core/services/rag/keyword_extraction_compression_strategy.dart'; // 导入 KeywordExtractionCompressionStrategy
import 'package:suoke_life/core/services/rag/no_compression_strategy.dart'; // 导入 NoCompressionStrategy
import 'package:suoke_life/core/services/rag/summary_compression_strategy.dart'; // 导入 SummaryCompressionStrategy

final getIt = GetIt.instance;

void registerLLMServiceModule() {
  // 注册 LLMService
  final appConfig = getIt<AppConfig>();
  final agentMemoryService = getIt<AgentMemoryService>();
  final knowledgeGraphClient =
      getIt<KnowledgeGraphClient>(); // 获取 KnowledgeGraphClient 实例
  final healthProfileService = getIt<HealthProfileService>();

  //  注册 ContextCompressionStrategy
  getIt.registerLazySingleton<NoCompressionStrategy>(
      () => NoCompressionStrategy());
  getIt.registerLazySingleton<SummaryCompressionStrategy>(
      () => SummaryCompressionStrategy());
  getIt.registerLazySingleton<KeywordExtractionCompressionStrategy>(
      () => KeywordExtractionCompressionStrategy());

  //  根据配置选择 ContextCompressionStrategy
  ContextCompressionStrategy contextCompressionStrategy;
  const compressionType =
      ContextCompressionType.keyword_extraction; //  TODO:  从配置中读取
  switch (compressionType) {
    case ContextCompressionType.summary:
      contextCompressionStrategy = getIt<SummaryCompressionStrategy>();
      break;
    case ContextCompressionType.keyword_extraction:
      contextCompressionStrategy =
          getIt<KeywordExtractionCompressionStrategy>();
      break;
    default:
      contextCompressionStrategy = getIt<NoCompressionStrategy>();
      break;
  }

  getIt.registerLazySingleton<LLMService>(() => LLMService(
        appConfig: appConfig,
        agentMemoryService: agentMemoryService,
        queryExpansionStrategy: QueryExpansionStrategy.synonym_replacement,
        contextCompressionStrategy: contextCompressionStrategy,
        reRankingStrategy: ReRankingStrategy.semantic_similarity,
        promptStrategy: PromptStrategy.standard_rag,
      ));

  // ... 其他 LLM Service 相关的注册 ...
}
