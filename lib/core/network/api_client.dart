import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';
import '../config/env_config.dart';
import 'token_manager.dart';

class ApiClient {
  final Dio _dio;
  final TokenManager _tokenManager;
  final String baseUrl;
  final bool enableLogging;

  ApiClient({
    required HttpClient httpClient,
    required TokenManager tokenManager,
    required this.baseUrl,
    required this.enableLogging,
  }) : _tokenManager = tokenManager {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: getIt<EnvConfig>().timeout,
      receiveTimeout: getIt<EnvConfig>().timeout,
    ));

    if (enableLogging) {
      _dio.interceptors.add(LogInterceptor(
