import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service_impl.dart';
import 'package:suoke_life/core/network/health_service_client.dart';
import 'package:suoke_life/core/network/life_service_client.dart';
import 'package:suoke_life/core/network/llm_service_client.dart';
import 'package:suoke_life/core/network/multimodal_service_client.dart';
import 'package:suoke_life/core/network/user_service_client.dart';
import 'package:suoke_life/core/services/network_service.dart';
import 'package:suoke_life/core/services/network_service_impl.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/network/knowledge_graph_client.dart';

void registerNetworkModule(GetIt getIt) {
  getIt.registerLazySingleton<Dio>(() => Dio());
  getIt.registerLazySingleton<NetworkService>(() => NetworkServiceImpl(getIt<Dio>()));
  getIt.registerLazySingleton<RedisService>(() => RedisServiceImpl());
  getIt.registerLazySingleton(() => LLMServiceClient(getIt<NetworkService>()));
  getIt.registerLazySingleton(() => HealthServiceClient(getIt<NetworkService>()));
  getIt.registerLazySingleton(() => UserServiceClient(getIt<NetworkService>()));
  getIt.registerLazySingleton(() => LifeServiceClient(getIt<NetworkService>()));
  getIt.registerLazySingleton(() => MultimodalServiceClient(getIt<NetworkService>()));
  getIt.registerLazySingleton<KnowledgeGraphClient>(() => KnowledgeGraphClient(getIt<AppConfig>()));
} 