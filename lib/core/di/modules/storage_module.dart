import 'package:get_it/get_it.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';
import 'package:suoke_life/core/services/infrastructure/database_service_impl.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service_impl.dart';
import 'package:suoke_life/core/config/database_config.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/services/agent_memory_service.dart';
import 'package:suoke_life/core/services/redis_service_impl.dart';

void registerStorageModule(GetIt getIt) {
  getIt.registerLazySingletonAsync(() async => await SharedPreferences.getInstance());
  getIt.registerLazySingleton<DatabaseConfig>(
      () => DatabaseConfig(databaseName: 'suoke_life_database.db'));
  getIt.registerLazySingleton<LocalStorageService>(
      () => LocalStorageServiceImpl());
  getIt.registerLazySingleton<DatabaseService>(() => DatabaseServiceImpl());
  getIt.registerLazySingleton<RedisService>(() => RedisServiceImpl());
  getIt.registerLazySingleton<AgentMemoryService>(
      () => AgentMemoryService(getIt<DatabaseConfig>(), getIt<AppConfig>()));
} 