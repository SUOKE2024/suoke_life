import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/network/auth_interceptor.dart';
import 'package:suoke_life/core/network/logging_interceptor.dart';

/// 提供基础Dio客户端
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio();
  
  // 设置基础配置
  dio.options.connectTimeout = const Duration(seconds: 15);
  dio.options.receiveTimeout = const Duration(seconds: 15);
  dio.options.headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // 添加拦截器
  dio.interceptors.add(AuthInterceptor());
  
  // 在开发环境中添加日志拦截器
  const bool isDevelopment = true; // 在实际环境中，这应该根据环境变量设置
  if (isDevelopment) {
    dio.interceptors.add(LoggingInterceptor());
  }
  
  return dio;
});

/// 提供API客户端
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return ApiClient(dio: dio);
});