import 'package:get_it/get_it.dart';
import 'package:dio/dio.dart';
import '../../repositories/health_data_repository.dart';
import '../../repositories/health_data_repository_impl.dart';
import '../../repositories/life_activity_data_repository.dart';
import '../../repositories/life_activity_data_repository_impl.dart';
import '../../repositories/user_repository.dart';
import '../../repositories/user_repository_impl.dart';
import '../../services/ai_service.dart';
import '../../services/ai_service_impl.dart';
import '../../services/chat_service.dart';
import '../../services/chat_service_impl.dart';
import '../../services/data_sync_service.dart';
import '../../services/data_sync_service_impl.dart';
import '../../services/expert_service.dart';
import '../../services/expert_service_impl.dart';
import '../../services/health_profile_service.dart';
import '../../services/health_profile_service_impl.dart';
import '../../services/health/health_service.dart';
import '../../services/health/health_service_impl.dart';
import '../../services/life/life_service.dart';
import '../../services/life/life_service_impl.dart';
import '../../services/multimodal_service.dart';
import '../../services/multimodal_service_impl.dart';
import '../../services/network_service.dart';
import '../../services/network_service_impl.dart';
import '../../services/notification_service.dart';
import '../../services/notification_service_impl.dart';
import '../../services/privacy_service.dart';
import '../../services/privacy_service_impl.dart';
import '../../services/redis_service.dart';
import '../../services/redis_service_impl.dart';
import '../../services/analytics_service.dart';
import '../../services/analytics_service_impl.dart';
import '../../services/infrastructure/database_service.dart';
import '../../services/infrastructure/database_service_impl.dart';
import '../../services/infrastructure/local_storage_service.dart';
import '../../services/infrastructure/local_storage_service_impl.dart';
import '../../services/user/user_service.dart';
import '../../services/user/user_service_impl.dart';
// import 'package:suoke_life/core/services/my_service.dart'; // 示例
// import 'package:suoke_life/core/services/my_service_impl.dart'; // 示例

void registerServiceModule(GetIt getIt) {
  getIt.registerLazySingleton<DatabaseService>(() => DatabaseServiceImpl());
  getIt.registerLazySingleton<LocalStorageService>(
      () => LocalStorageServiceImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<NetworkService>(
      () => NetworkServiceImpl(getIt<LocalStorageService>()));
  getIt.registerLazySingleton<NotificationService>(
      () => NotificationServiceImpl());
  getIt.registerLazySingleton<PrivacyService>(() => PrivacyServiceImpl(
        getIt<LocalStorageService>(),
      ));
  getIt.registerLazySingleton<RedisService>(() => RedisServiceImpl());
  getIt.registerLazySingleton<UserService>(() => UserServiceImpl(
        getIt<UserRepository>(),
        getIt<LocalStorageService>(),
      ));
  getIt.registerLazySingleton<AiService>(
      () => AiServiceImpl(getIt<NetworkService>()));
  getIt.registerLazySingleton<ChatService>(() => ChatServiceImpl(
        chatService: getIt<NetworkService>(),
        storage: getIt<LocalStorageService>(),
        redis: getIt<RedisService>(),
      ));
  getIt.registerLazySingleton<DataSyncService>(() => DataSyncServiceImpl());
  getIt.registerLazySingleton<ExpertService>(() => ExpertServiceImpl());
  getIt.registerLazySingleton<HealthService>(() => HealthServiceImpl());
  getIt.registerLazySingleton<LifeService>(() => LifeServiceImpl());
  getIt.registerLazySingleton<MultimodalService>(() => MultimodalServiceImpl());
  getIt.registerLazySingleton<AnalyticsService>(() => AnalyticsServiceImpl());
  getIt.registerLazySingleton<UserRepository>(
      () => UserRepositoryImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<HealthDataRepository>(
      () => HealthDataRepositoryImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<LifeActivityDataRepository>(
      () => LifeActivityDataRepositoryImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<HealthProfileService>(
      () => HealthProfileServiceImpl(getIt<DatabaseService>()));
  // getIt.registerLazySingleton<MyService>(() => MyServiceImpl()); // 示例
  // 注册其他服务
}
