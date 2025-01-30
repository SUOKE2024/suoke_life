import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import '../env/env_config.dart';

@module
abstract class NetworkModule {
  @Named('aiDio')
  @injectable
  Dio get aiDio {
    final dio = Dio(BaseOptions(
      baseUrl: EnvConfig.aiServiceUrl,
      headers: {
        'Authorization': 'Bearer ${EnvConfig.aiApiKey}',
        'Content-Type': 'application/json',
      },
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));
    
    // 添加拦截器
    dio.interceptors.addAll([
      LogInterceptor(
        requestBody: true,
        responseBody: true,
      ),
    ]);
    
    return dio;
  }
  
  @Named('aiBaseUrl')
  @injectable
  String get aiBaseUrl => EnvConfig.aiServiceUrl;
} 