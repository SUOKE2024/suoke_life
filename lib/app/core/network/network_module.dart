import 'package:get/get.dart';
import 'api_client.dart';
import 'doubao_client.dart';
import 'http2_config.dart';
import '../utils/token_manager.dart';
import '../config/env_config.dart';

class NetworkModule {
  static Future<void> init() async {
    // 根据环境配置 HTTP 客户端
    final httpClient = EnvConfig.enableHttp2
        ? await HTTP2Config.createHttpClient()
        : HttpClient();

    // 配置 HTTP 客户端
    httpClient.connectionTimeout = EnvConfig.timeout;
    httpClient.idleTimeout = const Duration(seconds: 30);
    if (EnvConfig.allowSelfSigned) {
      httpClient.badCertificateCallback = (cert, host, port) => true;
    }

    Get.put(httpClient, permanent: true);

    // 注入网络管理器
    Get.put(NetworkManager(), permanent: true);

    // 注入令牌管理器
    Get.put(TokenManager(Get.find()), permanent: true);

    // 注入 API 客户端
    Get.put(ApiClient(
      tokenManager: Get.find(),
      httpClient: Get.find(),
      baseUrl: EnvConfig.baseUrl,
      enableLogging: EnvConfig.enableNetworkLogging,
    ), permanent: true);

    // 注入豆包客户端
    Get.put(DoubaoClient(
      httpClient: Get.find(),
      baseUrl: EnvConfig.doubaoBaseUrl,
      enableLogging: EnvConfig.enableNetworkLogging,
    ), permanent: true);
  }

  static Future<void> dispose() async {
    final httpClient = Get.find<HttpClient>();
    httpClient.close(force: true);
  }
} 