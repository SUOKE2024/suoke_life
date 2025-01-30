import 'dart:io';
import 'package:get_it/get_it.dart';
import 'api_client.dart';
import 'doubao_client.dart';
import 'http2_config.dart';
import '../utils/token_manager.dart';
import '../config/env_config.dart';
import 'network_manager.dart';

class NetworkModule {
  final GetIt getIt;

  NetworkModule(this.getIt);

  Future<void> init() async {
    // 根据环境配置 HTTP 客户端
    final httpClient = getIt<EnvConfig>().enableHttp2
        ? HTTP2Config.createHttpClient()
        : HttpClient();

    // 配置 HTTP 客户端
    httpClient.connectionTimeout = getIt<EnvConfig>().timeout;
    httpClient.idleTimeout = const Duration(seconds: 30);
    if (getIt<EnvConfig>().allowSelfSigned) {
      httpClient.badCertificateCallback = (cert, host, port) => true;
    }

    getIt.registerLazySingleton<HttpClient>(() => httpClient);

    // 注入网络管理器
    getIt.registerLazySingleton<NetworkManager>(() => NetworkManager());

    // 注入令牌管理器
    getIt.registerLazySingleton<TokenManager>(
        () => TokenManager(getIt<HttpClient>()));

    // 注入 API 客户端
    getIt.registerLazySingleton<ApiClient>(
      () => ApiClient(
        tokenManager: getIt<TokenManager>(),
        httpClient: getIt<HttpClient>(),
        baseUrl: getIt<EnvConfig>().baseUrl,
        enableLogging: getIt<EnvConfig>().enableNetworkLogging,
      ),
    );

    // 注入豆包客户端
    getIt.registerLazySingleton<DoubaoClient>(
      () => DoubaoClient(
        httpClient: getIt<HttpClient>(),
        baseUrl: getIt<EnvConfig>().doubaoBaseUrl,
        enableLogging: getIt<EnvConfig>().enableNetworkLogging,
      ),
    );
  }

  Future<void> dispose() async {
    final httpClient = getIt<HttpClient>();
    httpClient.close(force: true);
  }
}
