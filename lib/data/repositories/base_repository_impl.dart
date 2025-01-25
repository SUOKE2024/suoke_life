import 'package:suoke_life/data/datasources/cache_manager.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';
import 'package:injectable/injectable.dart';
import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/utils/network_info.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/data/datasources/local_data_source.dart';
import 'package:suoke_life/data/datasources/remote_data_source.dart';

@singleton
class BaseRepositoryImpl<T> implements BaseRepository<T> {
  final RemoteDataSource<T> remoteDataSource;
  final LocalDataSource<T> localDataSource;
  final NetworkInfo networkInfo;
  final LocalStorageService _localStorageService;
  final RedisService _redisService;
  final CacheManager _cacheManager;
  
  BaseRepositoryImpl(
    this.remoteDataSource,
    this.localDataSource,
    this.networkInfo,
    this._localStorageService,
    this._redisService,
    this._cacheManager,
  );

  Future<Either<Failure, T>> get(String id) async {
    if (await networkInfo.isConnected) {
      try {
        final remoteData = await remoteDataSource.get(id);
        await localDataSource.cache(remoteData);
        return Right(remoteData);
      } catch (e) {
        final localData = await localDataSource.get(id);
        return localData != null ? Right(localData) : Left(ServerFailure());
      }
    } else {
      final localData = await localDataSource.get(id);
      return localData != null ? Right(localData) : Left(NetworkFailure());
    }
  }

  Future<T?> getFromCache<T>(String key, T Function(Map<String, dynamic>) fromJson) async {
    final cachedData = await _cacheManager.get(key);
    if (cachedData != null) {
      return fromJson(cachedData);
    }
    return null;
  }

  Future<void> saveToCache<T>(String key, T data, Map<String, dynamic> Function(T) toJson) async {
    await _cacheManager.set(key, toJson(data));
  }

  Future<void> clearCache(String key) async {
    await _cacheManager.delete(key);
  }

  Future<void> saveToLocal<T>(String key, T data, Map<String, dynamic> Function(T) toJson) async {
    // Implement local storage logic
  }

  Future<T?> getFromLocal<T>(String key, T Function(Map<String, dynamic>) fromJson) async {
    // Implement local storage logic
    return null;
  }
} 