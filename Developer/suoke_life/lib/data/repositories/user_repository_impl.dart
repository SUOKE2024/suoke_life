import 'package:dartz/dartz.dart';
import '../../domain/entities/user.dart';
import '../../domain/entities/user_preferences.dart';
import '../../domain/entities/health_data.dart';
import '../../domain/repositories/user_repository.dart';
import '../datasources/user_remote_data_source.dart';
import '../../core/error/failures.dart';
import '../../core/error/exceptions.dart';
import '../../core/network/network_info.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/remote/user_api_service.dart';
import 'package:suoke_life/data/datasources/local/user_local_data_source.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/user_preferences.dart';
import 'package:suoke_life/domain/entities/user_profile.dart';
import 'package:suoke_life/core/exceptions/user_exceptions.dart';

/// 用户仓库实现
class UserRepositoryImpl implements UserRepository {
  /// 远程数据源
  final UserApiService _remoteDataSource;
  
  /// 本地数据源
  final UserLocalDataSource _localDataSource;
  
  /// 网络信息
  final NetworkInfo _networkInfo;

  /// 构造函数
  UserRepositoryImpl({
    required UserApiService remoteDataSource,
    required UserLocalDataSource localDataSource,
    required NetworkInfo networkInfo,
  })  : _remoteDataSource = remoteDataSource,
        _localDataSource = localDataSource,
        _networkInfo = networkInfo;

  @override
  Future<Either<Failure, User>> getUserProfile(String userId) async {
    if (await _networkInfo.isConnected) {
      try {
        final accessToken = await _localDataSource.getAccessToken();
        final remoteUser = await _remoteDataSource.getUserProfile(userId, accessToken);
        await _localDataSource.cacheUser(remoteUser);
        return Right(remoteUser);
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } on UnauthorizedException catch (e) {
        return Left(UnauthorizedFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      try {
        final user = await _localDataSource.getUser(userId);
        return Right(user);
      } on CacheException catch (e) {
        return Left(CacheFailure(message: e.message));
      } catch (e) {
        return Left(CacheFailure(message: e.toString()));
      }
    }
  }

  @override
  Future<Either<Failure, User>> updateUserProfile(String userId, Map<String, dynamic> profileData) async {
    if (await _networkInfo.isConnected) {
      try {
        final accessToken = await _localDataSource.getAccessToken();
        final updatedUser = await _remoteDataSource.updateUserProfile(userId, profileData, accessToken);
        await _localDataSource.cacheUser(updatedUser);
        return Right(updatedUser);
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } on UnauthorizedException catch (e) {
        return Left(UnauthorizedFailure(message: e.message));
      } on InvalidInputException catch (e) {
        return Left(ValidationFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return const Left(NetworkFailure(message: '网络连接失败'));
    }
  }

  @override
  Future<Either<Failure, UserPreferences>> getUserPreferences(String userId) async {
    if (await _networkInfo.isConnected) {
      try {
        final accessToken = await _localDataSource.getAccessToken();
        final preferences = await _remoteDataSource.getUserPreferences(userId, accessToken);
        await _localDataSource.cacheUserPreferences(preferences);
        return Right(preferences);
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } on UnauthorizedException catch (e) {
        return Left(UnauthorizedFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      try {
        final preferences = await _localDataSource.getUserPreferences(userId);
        return Right(preferences);
      } on CacheException catch (e) {
        return Left(CacheFailure(message: e.message));
      } catch (e) {
        return Left(CacheFailure(message: e.toString()));
      }
    }
  }

  @override
  Future<Either<Failure, UserPreferences>> updateUserPreferences(String userId, Map<String, dynamic> preferences) async {
    if (await _networkInfo.isConnected) {
      try {
        final accessToken = await _localDataSource.getAccessToken();
        final updatedPreferences = await _remoteDataSource.updateUserPreferences(userId, preferences, accessToken);
        await _localDataSource.cacheUserPreferences(updatedPreferences);
        return Right(updatedPreferences);
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } on UnauthorizedException catch (e) {
        return Left(UnauthorizedFailure(message: e.message));
      } on InvalidInputException catch (e) {
        return Left(ValidationFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return const Left(NetworkFailure(message: '网络连接失败'));
    }
  }

  @override
  Future<Either<Failure, HealthData>> getUserHealthData(String userId, {String? period}) async {
    if (await _networkInfo.isConnected) {
      try {
        final accessToken = await _localDataSource.getAccessToken();
        final healthData = await _remoteDataSource.getUserHealthData(userId, period: period, accessToken: accessToken);
        return Right(healthData);
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } on UnauthorizedException catch (e) {
        return Left(UnauthorizedFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return const Left(NetworkFailure(message: '网络连接失败'));
    }
  }
} 