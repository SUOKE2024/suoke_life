// 用户服务提供者文件
// 定义用户相关的Provider

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:suoke_life/di/providers/core_providers.dart';
import 'package:suoke_life/domain/repositories/user_repository.dart';

/// 用户服务提供者
/// 暂时仅提供空实现，将在后续开发中完善
final userServiceProvider = Provider<UserService>((ref) {
  final dio = ref.watch(dioProvider);
  return UserService(dio: dio);
});

/// 用户API服务提供者
final userApiServiceProvider = Provider<UserApiService>((ref) {
  final dio = ref.watch(dioProvider);
  return UserApiService(dio: dio);
});

/// 临时用户API服务类
class UserApiService {
  final Dio dio;
  
  UserApiService({required this.dio});
  
  // 未来将实现的方法
  Future<Map<String, dynamic>> getUserProfile(String userId) async {
    // 获取用户资料的API调用
    return {'userId': userId, 'name': '用户', 'email': 'user@example.com'};
  }
}

/// 临时用户服务类
/// 后续将实现完整的用户服务功能
class UserService {
  final Dio dio;
  
  UserService({required this.dio});
  
  // 未来将实现的方法
  Future<void> getUserProfile() async {
    // 获取用户资料
  }
  
  Future<void> updateUserProfile(Map<String, dynamic> data) async {
    // 更新用户资料
  }
  
  Future<void> getUserPreferences() async {
    // 获取用户偏好
  }
}

/// 用户远程数据源提供者
final userRemoteDataSourceProvider = Provider<UserRemoteDataSource>((ref) {
  final dio = ref.watch(dioProvider);
  final apiService = ref.watch(userApiServiceProvider);
  return UserRemoteDataSourceImpl(dio: dio, apiService: apiService);
});

/// 临时用户远程数据源接口
abstract class UserRemoteDataSource {
  Future<Map<String, dynamic>> getUserProfile(String userId);
}

/// 临时用户远程数据源实现
class UserRemoteDataSourceImpl implements UserRemoteDataSource {
  final Dio dio;
  final UserApiService apiService;
  
  UserRemoteDataSourceImpl({required this.dio, required this.apiService});
  
  @override
  Future<Map<String, dynamic>> getUserProfile(String userId) async {
    return apiService.getUserProfile(userId);
  }
}

/// 用户本地数据源提供者
final userLocalDataSourceProvider = Provider<UserLocalDataSource>((ref) {
  return UserLocalDataSourceImpl();
});

/// 临时用户本地数据源接口
abstract class UserLocalDataSource {
  Future<Map<String, dynamic>?> getCachedUserProfile();
  Future<void> cacheUserProfile(Map<String, dynamic> userProfile);
}

/// 临时用户本地数据源实现
class UserLocalDataSourceImpl implements UserLocalDataSource {
  @override
  Future<Map<String, dynamic>?> getCachedUserProfile() async {
    return null;
  }
  
  @override
  Future<void> cacheUserProfile(Map<String, dynamic> userProfile) async {
    // 缓存用户资料
  }
}

/// 用户存储库提供者
final userRepositoryProvider = Provider<UserRepository>((ref) {
  final remoteDataSource = ref.watch(userRemoteDataSourceProvider);
  final localDataSource = ref.watch(userLocalDataSourceProvider);
  return UserRepositoryImpl(
    remoteDataSource: remoteDataSource,
    localDataSource: localDataSource,
  );
});

/// 临时用户存储库实现类
class UserRepositoryImpl implements UserRepository {
  final UserRemoteDataSource remoteDataSource;
  final UserLocalDataSource localDataSource;
  
  UserRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
  });
  
  @override
  Future<bool> isLoggedIn() async {
    return false;
  }
} 