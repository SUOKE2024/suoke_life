// dart format width=80
// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// InjectableConfigGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes

import '../../data/models/life_record.dart' as _i382;
import '../../data/models/service.dart' as _i866;
import '../../data/models/topic.dart' as _i667;
import '../../data/models/user.dart' as _i1063;
import '../../data/providers/database_provider.dart' as _i603;
import '../../data/providers/health_advice_provider.dart' as _i1016;
import '../../data/repositories/api_client.dart' as _i894;
import '../../data/repositories/chat_repository_impl.dart' as _i838;
import '../../data/services/ai_service_impl.dart' as _i692;
import '../../data/services/chat_service_impl.dart' as _i21;
import '../../data/services/health_service_impl.dart' as _i286;
import '../../data/services/life_service_impl.dart' as _i529;
import '../../data/services/suoke_service_impl.dart' as _i79;
import '../../di/register_module.dart' as _i624;
import '../../di/third_party_module.dart' as _i868;
import '../../domain/services/ai_service.dart' as _i885;
import '../../domain/services/chat_service.dart' as _i378;
import '../../domain/services/health_service.dart' as _i38;
import '../../domain/services/life_service.dart' as _i692;
import '../../domain/services/suoke_service.dart' as _i84;
import '../../domain/usecases/health/get_health_metrics_usecase.dart' as _i900;
import '../../features/ai/services/ai_service.dart' as _i448;
import '../../features/ai/services/ai_service_client.dart' as _i60;
import '../../features/life/services/life_service.dart' as _i494;
import '../../presentation/blocs/chat/voice_input_bloc.dart' as _i641;
import '../../presentation/blocs/navigation/navigation_bloc.dart' as _i261;
import '../../presentation/controllers/base/controller_template.dart' as _i506;
import '../../presentation/controllers/chat/chat_controller.dart' as _i261;
import '../../presentation/controllers/chat/chat_detail_bloc.dart' as _i400;
import '../../presentation/controllers/home/home_controller.dart' as _i236;
import '../../presentation/controllers/settings/settings_controller.dart'
    as _i161;
import '../../services/ai/doubao_service.dart' as _i560;
import '../../services/ai/embedding_service.dart' as _i611;
import '../../services/features/ai/ai_service.dart' as _i833;
import '../../services/features/ai/assistants/xiaoi_service.dart' as _i734;
import '../../services/features/analytics/aggregation_service.dart' as _i743;
import '../../services/features/analytics/analytics_service.dart' as _i793;
import '../../services/features/chat/chat_service.dart' as _i577;
import '../../services/features/config/config_service.dart' as _i298;
import '../../services/features/explore/explore_service.dart' as _i297;
import '../../services/features/health/health_service.dart' as _i1015;
import '../../services/features/knowledge/knowledge_service.dart' as _i939;
import '../../services/features/life/life_service.dart' as _i424;
import '../../services/features/user/user_service.dart' as _i772;
import '../agriculture/agriculture_service.dart' as _i281;
import '../agriculture/planting_plan_service.dart' as _i862;
import '../ai/ai_config.dart' as _i926;
import '../ai/ai_service.dart' as _i50;
import '../ai/graph_rag_service.dart' as _i249;
import '../analytics/analytics_processor.dart' as _i120;
import '../analytics/analytics_service.dart' as _i726;
import '../analytics/anonymizer_service.dart' as _i618;
import '../analytics/user_behavior_service.dart' as _i949;
import '../biometrics/biometric_service.dart' as _i800;
import '../cache/cache_manager.dart' as _i326;
import '../cache/cache_service.dart' as _i981;
import '../chat/chat_service.dart' as _i339;
import '../database/database_helper.dart' as _i64;
import '../database/database_service.dart' as _i711;
import '../database/repositories/user_repository.dart' as _i810;
import '../deeplink/deeplink_service.dart' as _i77;
import '../device/device_info_service.dart' as _i481;
import '../error/error_handler.dart' as _i308;
import '../error/parse_error_logger.dart' as _i764;
import '../file/file_service.dart' as _i34;
import '../health/health_service.dart' as _i680;
import '../health/tcm_service.dart' as _i34;
import '../health/vital_signs_service.dart' as _i427;
import '../image/image_service.dart' as _i17;
import '../lifecycle/app_lifecycle_service.dart' as _i973;
import '../localization/localization_service.dart' as _i970;
import '../logger/app_logger.dart' as _i293;
import '../logger/logger.dart' as _i512;
import '../network/api_client.dart' as _i557;
import '../network/connectivity_service.dart' as _i491;
import '../network/network_info.dart' as _i932;
import '../network/network_service.dart' as _i1025;
import '../notification/notification_service.dart' as _i85;
import '../permissions/permission_handler.dart' as _i159;
import '../security/anonymizer_service.dart' as _i20;
import '../security/encryption_service.dart' as _i320;
import '../security/key_rotation_service.dart' as _i910;
import '../security/security_config.dart' as _i275;
import '../security/security_service.dart' as _i383;
import '../services/file_service.dart' as _i367;
import '../services/permission_service.dart' as _i165;
import '../services/preferences_service.dart' as _i627;
import '../storage/data_cleanup_service.dart' as _i438;
import '../storage/local_storage.dart' as _i329;
import '../storage/local_storage_service.dart' as _i744;
import '../storage/secure_storage.dart' as _i619;
import '../storage/secure_storage_impl.dart' as _i891;
import '../storage/storage_service.dart' as _i865;
import '../sync/sync_service.dart' as _i520;
import '../theme/app_theme.dart' as _i1025;
import 'modules/core_module.dart' as _i134;
import 'modules/network_module.dart' as _i851;
import 'modules/storage_module.dart' as _i148;
import 'modules/third_party_module.dart' as _i691;
import 'network_module.dart' as _i567;

// initializes the registration of main-scope dependencies inside of GetIt
_i174.GetIt init(
  _i174.GetIt getIt, {
  String? environment,
  _i526.EnvironmentFilter? environmentFilter,
}) {
  final gh = _i526.GetItHelper(
    getIt,
    environment,
    environmentFilter,
  );
  final storageModule = _$StorageModule();
  final registerModule = _$RegisterModule();
  final coreModule = _$CoreModule();
  final networkModule = _$NetworkModule();
  final thirdPartyModule = _$ThirdPartyModule();
  final thirdPartyModule = _$ThirdPartyModule();
  final networkModule = _$NetworkModule();
  gh.factoryAsync<_i460.SharedPreferences>(() => storageModule.createPrefs());
  gh.factory<_i764.ParseErrorLogger>(() => _i764.ParseErrorLogger());
  gh.factory<_i165.PermissionService>(() => _i165.PermissionService());
  gh.factory<_i641.VoiceInputBloc>(() => _i641.VoiceInputBloc());
  gh.factory<_i261.NavigationBloc>(() => _i261.NavigationBloc());
  gh.factory<_i236.HomeController>(() => _i236.HomeController());
  gh.factory<_i506.ControllerTemplate>(() => _i506.ControllerTemplate());
  gh.singleton<_i558.FlutterSecureStorage>(() => registerModule.secureStorage);
  gh.singleton<_i64.DatabaseHelper>(() => _i64.DatabaseHelper());
  gh.singleton<_i800.BiometricService>(() => _i800.BiometricService());
  gh.singletonAsync<_i779.Database>(() => coreModule.database);
  gh.singleton<_i361.Dio>(() => networkModule.dio);
  gh.singleton<_i973.InternetConnectionChecker>(
      () => thirdPartyModule.connectionChecker);
  gh.singleton<_i152.LocalAuthentication>(() => thirdPartyModule.localAuth);
  gh.singleton<_i833.DeviceInfoPlugin>(() => thirdPartyModule.deviceInfo);
  gh.singleton<_i293.AppLogger>(() => _i293.AppLogger());
  gh.singleton<_i20.AnonymizerService>(() => _i20.AnonymizerService());
  gh.singleton<_i1025.NetworkService>(() => _i1025.NetworkService());
  gh.singleton<_i557.ApiClient>(() => _i557.ApiClient());
  gh.singleton<_i159.PermissionHandler>(() => _i159.PermissionHandler());
  gh.singleton<_i603.DatabaseProvider>(() => _i603.DatabaseProvider());
  gh.lazySingleton<_i895.Connectivity>(() => thirdPartyModule.connectivity);
  gh.lazySingleton<_i163.FlutterLocalNotificationsPlugin>(
      () => thirdPartyModule.notifications);
  gh.lazySingleton<_i892.FirebaseMessaging>(() => thirdPartyModule.messaging);
  gh.lazySingleton<_i618.AnonymizerService>(() => _i618.AnonymizerService());
  gh.lazySingleton<_i1016.HealthAdviceProvider>(
      () => _i1016.HealthAdviceProvider());
  gh.lazySingleton<_i894.ApiClient>(() => _i894.ApiClient());
  gh.lazySingleton<_i84.SuokeService>(() => const _i79.SuokeServiceImpl());
  gh.factory<_i382.LifeRecord>(() => _i382.LifeRecord(
        id: gh<String>(),
        title: gh<String>(),
        content: gh<String>(),
        type: gh<String>(),
        createdAt: gh<DateTime>(),
      ));
  gh.singletonAsync<_i329.LocalStorage>(() async =>
      _i329.LocalStorage(await gh.getAsync<_i460.SharedPreferences>()));
  gh.singletonAsync<_i627.PreferencesService>(() async =>
      _i627.PreferencesService(await gh.getAsync<_i460.SharedPreferences>()));
  gh.lazySingleton<_i744.LocalStorageService>(() => _i744.LocalStorageService(
        gh<InvalidType>(),
        gh<InvalidType>(),
      ));
  gh.lazySingleton<_i865.StorageService>(() => _i865.StorageServiceImpl());
  gh.factory<String>(
    () => networkModule.aiBaseUrl,
    instanceName: 'aiBaseUrl',
  );
  gh.singleton<_i54.ParseErrorLogger>(
    () => networkModule.errorLogger,
    instanceName: 'errorLogger',
  );
  gh.factory<_i866.Service>(() => _i866.Service(
        id: gh<String>(),
        title: gh<String>(),
        description: gh<String>(),
        imageUrl: gh<String>(),
        type: gh<String>(),
        metadata: gh<Map<String, dynamic>>(),
      ));
  gh.factory<_i361.Dio>(
    () => networkModule.aiDio,
    instanceName: 'aiDio',
  );
  gh.lazySingleton<_i326.CacheManager>(
      () => _i326.CacheManager(gh<_i865.StorageService>()));
  gh.lazySingleton<_i494.LifeService>(
      () => _i494.LifeService(gh<_i865.StorageService>()));
  gh.singleton<_i793.AnalyticsService>(() => _i793.AnalyticsService(
        gh<InvalidType>(),
        gh<InvalidType>(),
        gh<InvalidType>(),
      ));
  gh.lazySingleton<_i298.ConfigService>(() => _i298.ConfigService(
        gh<InvalidType>(),
        gh<InvalidType>(),
      ));
  gh.factory<_i838.ChatRepositoryImpl>(() => _i838.ChatRepositoryImpl(
        gh<InvalidType>(),
        gh<InvalidType>(),
      ));
  gh.singletonAsync<_i1015.HealthService>(() async => _i1015.HealthService(
        gh<_i1025.NetworkService>(),
        await gh.getAsync<_i329.LocalStorage>(),
        gh<_i293.AppLogger>(),
      ));
  gh.factory<_i885.AIService>(
      () => _i692.AIServiceImpl(gh<_i1025.NetworkService>()));
  gh.factory<_i378.ChatService>(
      () => _i21.ChatServiceImpl(gh<_i603.DatabaseProvider>()));
  gh.factory<_i692.LifeService>(() => _i529.LifeServiceImpl(
        gh<_i1025.NetworkService>(),
        gh<_i603.DatabaseProvider>(),
      ));
  gh.singleton<_i275.SecurityConfig>(() => _i275.SecurityConfig(
        keyRotationDays: gh<int>(),
        encryptionAlgorithm: gh<String>(),
        keyLength: gh<int>(),
        hashAlgorithm: gh<String>(),
      ));
  gh.factoryAsync<_i900.GetHealthMetricsUseCase>(() async =>
      _i900.GetHealthMetricsUseCase(await gh.getAsync<_i1015.HealthService>()));
  gh.singleton<_i320.EncryptionService>(
      () => _i320.EncryptionService(gh<_i558.FlutterSecureStorage>()));
  gh.factory<_i161.SettingsController>(
      () => _i161.SettingsController(gh<InvalidType>()));
  gh.factory<_i261.ChatController>(
      () => _i261.ChatController(gh<_i378.ChatService>()));
  gh.factory<_i60.AIServiceClient>(() => _i60.AIServiceClient(
        gh<_i361.Dio>(instanceName: 'aiDio'),
        baseUrl: gh<String>(instanceName: 'aiBaseUrl'),
        errorLogger: gh<dynamic>(),
      ));
  gh.factory<_i667.Topic>(() => _i667.Topic(
        id: gh<String>(),
        title: gh<String>(),
        description: gh<String>(),
        imageUrl: gh<String>(),
        tags: gh<List<String>>(),
      ));
  gh.singleton<_i932.NetworkInfoImpl>(
      () => _i932.NetworkInfoImpl(gh<_i973.InternetConnectionChecker>()));
  gh.singleton<_i926.AIConfig>(() => _i926.AIConfig(
        apiKey: gh<String>(),
        baseUrl: gh<String>(),
      ));
  gh.factory<_i560.DoubaoService>(
      () => _i560.DoubaoService(gh<_i1025.NetworkService>()));
  gh.factory<_i611.EmbeddingService>(
      () => _i611.EmbeddingService(gh<_i1025.NetworkService>()));
  gh.singletonAsync<_i981.CacheService>(() async => _i981.CacheService(
        await gh.getAsync<_i779.Database>(),
        gh<_i293.AppLogger>(),
      ));
  gh.factory<_i577.ChatService>(
      () => _i577.ChatService(gh<_i1025.NetworkService>()));
  gh.factory<_i297.ExploreService>(
      () => _i297.ExploreService(gh<_i1025.NetworkService>()));
  gh.factory<_i734.XiaoiService>(
      () => _i734.XiaoiService(gh<_i1025.NetworkService>()));
  gh.factory<_i833.AIService>(
      () => _i833.AIService(gh<_i1025.NetworkService>()));
  gh.lazySingleton<_i743.AggregationService>(
      () => _i743.AggregationService(gh<_i1025.NetworkService>()));
  gh.factory<_i1063.User>(() => _i1063.User(
        id: gh<String>(),
        name: gh<String>(),
        email: gh<String>(),
        avatarUrl: gh<String>(),
        createdAt: gh<DateTime>(),
      ));
  gh.lazySingleton<_i38.HealthService>(
      () => _i286.HealthServiceImpl(gh<_i603.DatabaseProvider>()));
  gh.singleton<_i711.DatabaseService>(
      () => _i711.DatabaseService(gh<_i293.AppLogger>()));
  gh.factory<_i367.FileService>(
      () => _i367.FileService(gh<_i320.EncryptionService>()));
  gh.singleton<_i481.DeviceInfoService>(
      () => _i481.DeviceInfoService(gh<_i833.DeviceInfoPlugin>()));
  gh.singletonAsync<_i1025.AppTheme>(
      () async => _i1025.AppTheme(await gh.getAsync<_i329.LocalStorage>()));
  gh.singletonAsync<_i970.LocalizationService>(() async =>
      _i970.LocalizationService(await gh.getAsync<_i329.LocalStorage>()));
  gh.lazySingleton<_i438.DataCleanupService>(
      () => _i438.DataCleanupService(gh<_i711.DatabaseService>()));
  gh.lazySingleton<_i619.SecureStorage>(
      () => _i891.SecureStorageImpl(gh<_i293.AppLogger>()));
  gh.factory<_i424.LifeService>(() => _i424.LifeService(
        gh<_i1025.NetworkService>(),
        gh<_i865.StorageService>(),
      ));
  gh.singleton<_i772.UserService>(() => _i772.UserService(
        gh<_i711.DatabaseService>(),
        gh<_i1025.NetworkService>(),
        gh<_i320.EncryptionService>(),
      ));
  gh.factoryAsync<_i939.KnowledgeService>(
      () async => _i939.KnowledgeServiceImpl(
            gh<_i1025.NetworkService>(),
            await gh.getAsync<_i981.CacheService>(),
          ));
  gh.factory<_i448.AIService>(
      () => _i448.AIService(gh<_i60.AIServiceClient>()));
  gh.singleton<_i726.AnalyticsService>(() => _i726.AnalyticsService(
        gh<_i711.DatabaseService>(),
        gh<_i20.AnonymizerService>(),
      ));
  gh.singleton<_i512.AppLogger>(
      () => _i512.AppLogger(gh<_i726.AnalyticsService>()));
  gh.singleton<_i810.UserRepository>(
      () => _i810.UserRepository(gh<_i711.DatabaseService>()));
  gh.singleton<_i910.KeyRotationService>(() => _i910.KeyRotationService(
        gh<_i619.SecureStorage>(),
        gh<_i275.SecurityConfig>(),
        gh<_i293.AppLogger>(),
      ));
  gh.factory<_i400.ChatDetailBloc>(
      () => _i400.ChatDetailBloc(gh<_i577.ChatService>()));
  gh.singletonAsync<_i85.NotificationService>(
      () async => _i85.NotificationService(
            gh<_i892.FirebaseMessaging>(),
            gh<_i163.FlutterLocalNotificationsPlugin>(),
            await gh.getAsync<_i329.LocalStorage>(),
            gh<_i512.AppLogger>(),
          ));
  gh.singletonAsync<_i34.TCMService>(() async => _i34.TCMService(
        gh<_i1025.NetworkService>(),
        await gh.getAsync<_i329.LocalStorage>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singletonAsync<_i680.HealthService>(() async => _i680.HealthService(
        gh<_i1025.NetworkService>(),
        await gh.getAsync<_i329.LocalStorage>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singletonAsync<_i427.VitalSignsService>(
      () async => _i427.VitalSignsService(
            gh<_i1025.NetworkService>(),
            await gh.getAsync<_i329.LocalStorage>(),
            gh<_i512.AppLogger>(),
          ));
  gh.singletonAsync<_i120.AnalyticsProcessor>(
      () async => _i120.AnalyticsProcessor(
            gh<_i726.AnalyticsService>(),
            await gh.getAsync<_i329.LocalStorage>(),
            gh<_i512.AppLogger>(),
          ));
  gh.singleton<_i383.SecurityService>(() => _i383.SecurityService(
        gh<_i619.SecureStorage>(),
        gh<_i293.AppLogger>(),
      ));
  gh.singleton<_i17.ImageService>(
      () => _i17.ImageService(gh<_i512.AppLogger>()));
  gh.singleton<_i77.DeeplinkService>(
      () => _i77.DeeplinkService(gh<_i512.AppLogger>()));
  gh.singletonAsync<_i949.UserBehaviorService>(
      () async => _i949.UserBehaviorService(
            await gh.getAsync<_i120.AnalyticsProcessor>(),
            await gh.getAsync<_i329.LocalStorage>(),
            gh<_i512.AppLogger>(),
          ));
  gh.singleton<_i973.AppLifecycleService>(() => _i973.AppLifecycleService(
        gh<_i512.AppLogger>(),
        gh<_i726.AnalyticsService>(),
      ));
  gh.singleton<_i308.ErrorHandler>(() => _i308.ErrorHandler(
        gh<_i512.AppLogger>(),
        gh<_i726.AnalyticsService>(),
      ));
  gh.singleton<_i34.FileService>(() => _i34.FileService(
        gh<_i320.EncryptionService>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singleton<_i862.PlantingPlanService>(() => _i862.PlantingPlanService(
        gh<_i1025.NetworkService>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singleton<_i281.AgricultureService>(() => _i281.AgricultureService(
        gh<_i1025.NetworkService>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singleton<_i249.GraphRAGService>(() => _i249.GraphRAGService(
        gh<_i1025.NetworkService>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singleton<_i50.AIService>(() => _i50.AIService(
        gh<_i1025.NetworkService>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singleton<_i491.ConnectivityService>(() => _i491.ConnectivityService(
        gh<_i895.Connectivity>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singleton<_i339.ChatService>(() => _i339.ChatService(
        gh<_i1025.NetworkService>(),
        gh<_i50.AIService>(),
        gh<_i249.GraphRAGService>(),
        gh<_i512.AppLogger>(),
      ));
  gh.singletonAsync<_i520.SyncService>(() async => _i520.SyncService(
        gh<_i1025.NetworkService>(),
        await gh.getAsync<_i329.LocalStorage>(),
        gh<_i491.ConnectivityService>(),
        gh<_i512.AppLogger>(),
      ));
  return getIt;
}

class _$StorageModule extends _i148.StorageModule {}

class _$RegisterModule extends _i624.RegisterModule {}

class _$CoreModule extends _i134.CoreModule {}

class _$NetworkModule extends _i851.NetworkModule {}

class _$ThirdPartyModule extends _i691.ThirdPartyModule {}

class _$ThirdPartyModule extends _i868.ThirdPartyModule {}

class _$NetworkModule extends _i567.NetworkModule {}
