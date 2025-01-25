// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// InjectableConfigGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:connectivity_plus/connectivity_plus.dart' as _i3;
import 'package:dio/dio.dart' as _i4;
import 'package:get_it/get_it.dart' as _i1;
import 'package:injectable/injectable.dart' as _i2;
import 'package:shared_preferences/shared_preferences.dart' as _i10;
import 'package:sqflite/sqflite.dart' as _i11;

import '../../data/datasources/cache_manager.dart' as _i13;
import '../../data/repositories/base_repository_impl.dart' as _i14;
import '../../core/di/modules/database_module.dart' as _i15;
import '../../core/di/modules/network_module.dart' as _i16;
import '../../core/di/modules/storage_module.dart' as _i17;
import '../../core/services/infrastructure/local_storage_service.dart' as _i6;
import '../../core/services/infrastructure/redis_service.dart' as _i8;
import '../../core/utils/network_info.dart' as _i7;
import '../../data/datasources/local_data_source.dart' as _i5;
import '../../data/datasources/remote_data_source.dart' as _i9;

// initializes the registration of main-scope dependencies inside of GetIt
Future<_i1.GetIt> $initGetIt(
  _i1.GetIt getIt, {
  String? environment,
  _i2.EnvironmentFilter? environmentFilter,
}) async {
  final gh = _i2.GetItHelper(
    getIt,
    environment,
    environmentFilter,
  );
  gh.singleton<_i3.Connectivity>(() => _i3.Connectivity());
  gh.singleton<_i4.Dio>(() => _i16.NetworkModule().dio);
  gh.factory<_i5.LocalDataSource>(() => _i5.LocalDataSource());
  gh.factory<_i9.RemoteDataSource>(() => _i9.RemoteDataSource());
  gh.singletonAsync<_i10.SharedPreferences>(
      () => _i17.StorageModule().prefs);
  gh.singleton<_i7.NetworkInfo>(() => _i7.NetworkInfo(gh<_i3.Connectivity>()));
  gh.singleton<_i8.RedisService>(() => _i8.RedisService());
  gh.singletonAsync<_i11.Database>(() => _i15.DatabaseModule().database);
  gh.singleton<_i13.CacheManager>(() => _i13.CacheManager(gh<_i8.RedisService>()));
  await gh.singletonAsync<_i6.LocalStorageService>(
      () async => _i6.LocalStorageService(await gh.getAsync<_i11.Database>()));
  gh.singleton<_i14.BaseRepositoryImpl>(() => _i14.BaseRepositoryImpl(
        gh<_i9.RemoteDataSource>(),
        gh<_i5.LocalDataSource>(),
        gh<_i7.NetworkInfo>(),
        gh<_i6.LocalStorageService>(),
        gh<_i8.RedisService>(),
        gh<_i13.CacheManager>(),
      ));
  return getIt;
} 