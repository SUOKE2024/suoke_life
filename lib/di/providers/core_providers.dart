import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../../core/config/environment.dart';
import '../../core/database/database_helper.dart';
import '../../core/network/api_client.dart';
import '../../core/network/interceptors/auth_interceptor.dart';
import '../../core/network/interceptors/error_interceptor.dart';
import '../../core/network/interceptors/logging_interceptor.dart';
import '../../core/network/network_info.dart';
import '../../core/storage/secure_storage.dart';

/// 日志提供者
final loggerProvider = Provider<Logger>((ref) {
  return Logger();
});

/// 安全存储提供者
final secureStorageProvider = Provider<SecureStorage>((ref) {
  return SecureStorage();
});

/// 网络信息提供者
final networkInfoProvider = Provider<NetworkInfo>((ref) {
  return NetworkInfoImpl(Connectivity());
});

/// 数据库辅助类提供者
final databaseHelperProvider = Provider<DatabaseHelper>((ref) {
  final logger = ref.watch(loggerProvider);
  return DatabaseHelper(logger: logger);
});

/// API客户端提供者
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: Environment.apiUrl,
    connectTimeout: Duration(milliseconds: Environment.timeout),
    receiveTimeout: Duration(milliseconds: Environment.timeout),
    sendTimeout: Duration(milliseconds: Environment.timeout),
    contentType: 'application/json; charset=utf-8',
  ));
  
  // 添加拦截器
  dio.interceptors.add(LoggingInterceptor());
  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(ErrorInterceptor());
  
  return ApiClient(dio);
});