import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../data/datasources/remote/auth_api_service.dart';
import '../../data/repositories/auth_repository_impl.dart';
import '../../domain/repositories/auth_repository.dart';
import '../../domain/usecases/auth_usecases.dart';
import '../../presentation/auth/notifiers/auth_state_notifier.dart';
import '../../data/datasources/local/auth_local_data_source.dart';
import '../../data/datasources/remote/api_service.dart';
import '../providers/core_providers.dart'; // 导入核心提供者，包含secureStorageProvider
import 'package:suoke_life/data/datasources/remote/auth_remote_data_source.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';

/// API服务提供者
final apiServiceProvider = Provider<ApiService>((ref) {
  final dio = ref.watch(dioProvider);
  // 返回实际的ApiService实现
  return ApiService(dio: dio);
});

/// API服务提供者
final authApiServiceProvider = Provider<AuthApiService>((ref) {
  final dio = ref.watch(dioProvider);
  // 返回实际的AuthApiService实现
  return AuthApiService(dio: dio);
});

/// 本地数据源提供者
final authLocalDataSourceProvider = Provider<AuthLocalDataSource>((ref) {
  return AuthLocalDataSourceImpl();
});

/// 认证远程数据源Provider
final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return AuthRemoteDataSourceImpl(apiService: apiService);
});

/// 存储库提供者
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final remoteDataSource = ref.watch(authRemoteDataSourceProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  final apiService = ref.watch(apiServiceProvider);
  final authApiService = ref.watch(authApiServiceProvider);
  final secureStorage = ref.watch(secureStorageProvider);
  
  return AuthRepositoryImpl(
    remoteDataSource: remoteDataSource,
    networkInfo: networkInfo,
    apiService: apiService,
    authApiService: authApiService,
    secureStorage: secureStorage,
  );
});

/// 用例提供者
final authUseCasesProvider = Provider<AuthUseCases>((ref) {
  final repository = ref.watch(authRepositoryProvider);
  
  return AuthUseCases(repository: repository);
});

/// 认证状态提供者
final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  final useCases = ref.watch(authUseCasesProvider);
  
  return AuthStateNotifier(useCases: useCases);
});

/// 认证状态检查提供者
final authStatusProvider = FutureProvider<bool>((ref) async {
  final repository = ref.watch(authRepositoryProvider);
  return repository.checkAuthStatus();
});

/// 当前用户提供者
final currentUserProvider = FutureProvider((ref) async {
  final repository = ref.watch(authRepositoryProvider);
  return repository.getCurrentUser();
});

/// 安全存储Provider
final secureStorageProvider = Provider<SecureStorage>((ref) {
  final flutterSecureStorage = ref.watch(flutterSecureStorageProvider);
  return SecureStorage(storage: flutterSecureStorage);
});
