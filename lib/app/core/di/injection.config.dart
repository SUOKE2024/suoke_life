// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// InjectableConfigGenerator
// **************************************************************************

import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

import '../services/suoke_service.dart';
import '../services/suoke_service_impl.dart';
import '../security/encryption_service.dart';
import '../security/anonymizer_service.dart';
import '../database/database_service.dart';
import '../cache/cache_service.dart';
import '../sync/sync_service.dart';
import '../network/network_service.dart';
import '../services/features/user/user_service.dart';
import '../services/features/health/health_service.dart';
import '../services/features/ai/ai_service.dart';
import '../services/features/knowledge/knowledge_service.dart';
import '../services/features/analytics/analytics_service.dart';
import '../services/features/config/config_service.dart';
// ... 其他导入

@InjectableInit()
void $initGetIt(GetIt getIt, {String? environment}) {
  final gh = GetItHelper(getIt, environment);
  
  // 核心服务
  gh.singleton<EncryptionService>(EncryptionService());
  gh.singleton<NetworkService>(NetworkService(
    getIt<EncryptionService>(),
    getIt<CacheService>(),
  ));
  
  // 功能服务
  gh.singleton<UserService>(UserService(
    getIt<DatabaseService>(),
    getIt<NetworkService>(),
    getIt<EncryptionService>(),
  ));
  
  gh.singleton<HealthService>(HealthService(
    getIt<DatabaseService>(),
    getIt<NetworkService>(),
    getIt<SyncService>(),
  ));
  
  gh.singleton<AIService>(AIService(
    getIt<NetworkService>(),
    getIt<CacheService>(),
  ));
  
  gh.singleton<KnowledgeService>(KnowledgeService(
    getIt<NetworkService>(),
    getIt<CacheService>(),
  ));
  
  gh.singleton<AnalyticsService>(AnalyticsService(
    getIt<NetworkService>(),
    getIt<DatabaseService>(),
  ));
  
  gh.singleton<ConfigService>(ConfigService(
    getIt<StorageService>(),
    getIt<NetworkService>(),
  ));
}
