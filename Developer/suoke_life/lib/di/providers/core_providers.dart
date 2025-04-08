// 核心服务提供者文件
// 用于注册配置服务、模型服务和RAG服务

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/ai_agents/tools/file_search_tool.dart';
import 'package:suoke_life/core/services/config_service.dart';
import 'package:suoke_life/core/services/model_service.dart';
import 'package:suoke_life/core/services/rag_service.dart';
import 'package:dio/dio.dart';
import '../../core/network/api_interceptor.dart';
import '../../core/utils/logger.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/retry_interceptor.dart';
import 'package:internet_connection_checker/internet_connection_checker.dart';
import '../../core/network/network_info.dart';
import 'package:suoke_life/core/network/dio_interceptors.dart';
import 'package:suoke_life/core/storage/preferences_manager.dart';

/// Dio HTTP客户端提供者
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio();
  
  // 配置基础URL和超时时间
  dio.options.baseUrl = ApiConstants.baseUrl;
  dio.options.connectTimeout = ApiConstants.connectTimeout;
  dio.options.receiveTimeout = ApiConstants.receiveTimeout;
  dio.options.sendTimeout = ApiConstants.sendTimeout;
  
  // 添加拦截器处理认证令牌、刷新令牌等
  dio.interceptors.add(AuthInterceptor(ref));
  
  // 添加重试拦截器
  dio.interceptors.add(RetryInterceptor(dio: dio));
  
  // 添加日志拦截器
  dio.interceptors.add(LogInterceptor(
    request: true,
    requestHeader: true,
    requestBody: true,
    responseHeader: true,
    responseBody: true,
    error: true,
  ));
  
  return dio;
});

/// FlutterSecureStorage提供者
final flutterSecureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

/// SharedPreferences提供者
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('需要在main.dart中覆盖此provider');
});

/// 首选项管理器提供者
final preferencesManagerProvider = Provider<PreferencesManager>((ref) {
  final sharedPreferences = ref.watch(sharedPreferencesProvider);
  final secureStorage = ref.watch(flutterSecureStorageProvider);
  return PreferencesManager(sharedPreferences, secureStorage);
});

/// 配置服务提供者
final configServiceProvider = Provider<ConfigService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  final secureStorage = ref.watch(flutterSecureStorageProvider);
  return ConfigService(prefs, secureStorage);
});

/// 模型服务提供者
final modelServiceProvider = Provider<ModelService>((ref) {
  final configService = ref.watch(configServiceProvider);
  final provider = configService.getPreferredModelProvider();
  return ModelServiceFactory.createModelService(provider, configService);
});

/// 文件搜索工具提供者
final fileSearchToolProvider = Provider<FileSearchTool>((ref) {
  final configService = ref.watch(configServiceProvider);
  final modelService = ref.watch(modelServiceProvider);
  return FileSearchTool(
    configService: configService,
    modelService: modelService,
  );
});

/// RAG服务提供者
final ragServiceProvider = Provider<RAGService>((ref) {
  final configService = ref.watch(configServiceProvider);
  final modelService = ref.watch(modelServiceProvider);
  final fileSearchTool = ref.watch(fileSearchToolProvider);
  
  return BasicRagService(
    configService: configService,
    modelService: modelService,
    fileSearchTool: fileSearchTool,
  );
});

/// 网络检查Provider
final internetConnectionCheckerProvider = Provider<InternetConnectionChecker>((ref) {
  return InternetConnectionChecker();
});

/// 网络信息Provider
final networkInfoProvider = Provider<NetworkInfo>((ref) {
  return NetworkInfoImpl(ref.watch(internetConnectionCheckerProvider));
});

/// 初始化核心提供者
Future<void> initializeCoreProviders(ProviderContainer container) async {
  // 初始化SharedPreferences
  final prefs = await SharedPreferences.getInstance();
  container.updateOverrides([
    sharedPreferencesProvider.overrideWithValue(prefs),
  ]);
  
  // 尝试从存储获取API环境配置
  final apiEnv = prefs.getString('api_environment');
  if (apiEnv != null) {
    ApiConstants.setEnvironment(apiEnv);
  }
} 