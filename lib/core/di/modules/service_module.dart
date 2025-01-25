import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/repositories/health_data_repository.dart';
import 'package:suoke_life/core/repositories/health_data_repository_impl.dart';
import 'package:suoke_life/core/repositories/life_activity_data_repository.dart';
import 'package:suoke_life/core/repositories/life_activity_data_repository_impl.dart';
import 'package:suoke_life/core/repositories/user_repository.dart';
import 'package:suoke_life/core/repositories/user_repository_impl.dart';
import 'package:suoke_life/core/services/ai_service.dart';
import 'package:suoke_life/core/services/ai_service_impl.dart';
import 'package:suoke_life/core/services/chat_service.dart';
import 'package:suoke_life/core/services/chat_service_impl.dart';
import 'package:suoke_life/core/services/data_sync_service.dart';
import 'package:suoke_life/core/services/data_sync_service_impl.dart';
import 'package:suoke_life/core/services/expert_service.dart';
import 'package:suoke_life/core/services/expert_service_impl.dart';
import 'package:suoke_life/core/services/health_service.dart';
import 'package:suoke_life/core/services/health_service_impl.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';
import 'package:suoke_life/core/services/infrastructure/database_service_impl.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service_impl.dart';
import 'package:suoke_life/core/services/notification_service.dart';
import 'package:suoke_life/core/services/notification_service_impl.dart';
import 'package:suoke_life/core/services/payment_service.dart';
import 'package:suoke_life/core/services/payment_service_impl.dart';
import 'package:suoke_life/core/services/privacy_service.dart';
import 'package:suoke_life/core/services/privacy_service_impl.dart';
import 'package:suoke_life/core/services/analytics_service.dart';
import 'package:suoke_life/core/services/analytics_service_impl.dart';
import 'package:suoke_life/core/services/network_service.dart';
import 'package:suoke_life/core/services/health_profile_service.dart';
import 'package:suoke_life/core/services/health_profile_service_impl.dart';
// import 'package:suoke_life/core/services/my_service.dart'; // 示例
// import 'package:suoke_life/core/services/my_service_impl.dart'; // 示例

void registerServiceModule(GetIt getIt) {
  getIt.registerLazySingleton<LocalStorageService>(() => LocalStorageServiceImpl());
  getIt.registerLazySingleton<DatabaseService>(() => DatabaseServiceImpl());
  getIt.registerLazySingleton<PrivacyService>(() => PrivacyServiceImpl(getIt<LocalStorageService>()));
  getIt.registerLazySingleton<AiService>(() => AiServiceImpl(getIt<NetworkService>()));
  getIt.registerLazySingleton<ChatService>(() => ChatServiceImpl(getIt<LocalStorageService>()));
  getIt.registerLazySingleton<ExpertService>(() => ExpertServiceImpl());
  getIt.registerLazySingleton<HealthService>(() => HealthServiceImpl());
  getIt.registerLazySingleton<PaymentService>(() => PaymentServiceImpl());
  getIt.registerLazySingleton<NotificationService>(() => NotificationServiceImpl());
  getIt.registerLazySingleton<AnalyticsService>(() => AnalyticsServiceImpl());
  getIt.registerLazySingleton<DataSyncService>(() => DataSyncServiceImpl(
    getIt<UserRepository>(),
    getIt<HealthDataRepository>(),
    getIt<LifeActivityDataRepository>(),
    getIt<NetworkService>(),
    getIt<PrivacyService>(),
  ));
  getIt.registerLazySingleton<UserRepository>(() => UserRepositoryImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<HealthDataRepository>(() => HealthDataRepositoryImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<LifeActivityDataRepository>(() => LifeActivityDataRepositoryImpl(getIt<DatabaseService>()));
  getIt.registerLazySingleton<HealthProfileService>(() => HealthProfileServiceImpl(getIt<DatabaseService>()));
  // getIt.registerLazySingleton<MyService>(() => MyServiceImpl()); // 示例
  // 注册其他服务
} 