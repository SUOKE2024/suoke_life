import 'package:core/services/infrastructure/local_storage_service.dart';
import 'package:core/services/infrastructure/redis_service.dart';
import 'package:injectable/injectable.dart';

@module
abstract class StorageModule {
  @preResolve
  @singleton
  Future<LocalStorageService> get localStorageService async {
    final service = LocalStorageServiceImpl();
    await service.init();
    return service;
  }
  @singleton
  RedisService get redisService => RedisServiceImpl();
} 