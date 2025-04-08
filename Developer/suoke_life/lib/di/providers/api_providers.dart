import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/core/storage/secure_storage.dart';
import 'package:internet_connection_checker/internet_connection_checker.dart';

/// API客户端提供者
final apiClientProvider = Provider<ApiClient>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  
  // 开发环境URL
  const baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://118.31.223.213/api',
  );
  
  return ApiClient(
    baseUrl: baseUrl,
    secureStorage: secureStorage,
  );
});

/// 网络信息提供者
final networkInfoProvider = Provider<NetworkInfo>((ref) {
  return NetworkInfoImpl(InternetConnectionChecker());
});

/// 安全存储提供者
final secureStorageProvider = Provider<SecureStorage>((ref) {
  return SecureStorage();
}); 