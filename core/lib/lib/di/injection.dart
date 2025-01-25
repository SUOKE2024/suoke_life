import 'package:core/core.dart';
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

final getIt = GetIt.instance;

@InjectableInit()
void configureDependencies() {
  // 基础服务注册
  getIt.registerLazySingleton<LLMServiceClient>(() => LLMServiceClientImpl());
  getIt.registerLazySingleton<MultimodalServiceClient>(() => MultimodalServiceClientImpl());
  
  // AI代理相关服务
  getIt.registerLazySingleton<AgentSelector>(() => AgentSelector());
  getIt.registerLazySingleton<HealthAnalysisService>(
    () => HealthAnalysisServiceImpl(
      getIt<LLMServiceClient>(),
      getIt<MultimodalServiceClient>(),
      getIt<AgentSelector>(),
    ),
  );

  getIt.registerFactoryParam<AnalysisContext, TCMPatterns, void>(
    (tcmPatterns, _) => AnalysisContext(
      userData: getIt<UserProfile>(),
      tcmPatterns: tcmPatterns,
    ),
  );

  // 其他现有服务注册...
}
