import 'package:get_it/get_it.dart';
import '../module_registrar.dart';
import '../../network/http_client.dart';
import '../../network/websocket_client.dart';
import '../../../services/connection_manager_service.dart';
import '../../../services/secure_data_transport_service.dart';
import '../../error/error_handler_service.dart';

/// 网络模块注册器
class NetworkModuleRegistrar implements ModuleRegistrar {
  @override
  String get moduleName => '网络模块';
  
  @override
  List<Type> get dependencies => [
    ErrorHandlerService,  // 依赖错误处理服务
  ];

  @override
  Future<void> register(GetIt getIt) async {
    // 验证依赖
    await validateDependencies(getIt);
    
    // 基础网络客户端
    getIt.registerLazySingleton(() => HttpClient());
    getIt.registerLazySingleton(() => WebSocketClient());

    // 连接管理服务
    getIt.registerLazySingleton(
      () => ConnectionManagerService(
        wsClient: getIt<WebSocketClient>(),
        errorHandler: getIt<ErrorHandlerService>(),
      ),
    );

    // 安全传输服务
    getIt.registerLazySingleton(
      () => SecureDataTransportService(
        wsClient: getIt<WebSocketClient>(),
        httpClient: getIt<HttpClient>(),
        encryptionKey: const String.fromEnvironment(
          'SECURE_TRANSPORT_KEY',
          defaultValue: 'your-default-key-here',
        ),
      ),
    );
  }

  @override
  Future<void> onModuleReady(GetIt getIt) async {
    // 初始化连接管理器
    final connectionManager = getIt<ConnectionManagerService>();
    await connectionManager.initialize();
    
    // 初始化安全传输服务
    final secureTransport = getIt<SecureDataTransportService>();
    await secureTransport.initialize();
  }

  @override
  Future<void> onModuleDispose(GetIt getIt) async {
    // 关闭网络连接
    final wsClient = getIt<WebSocketClient>();
    await wsClient.dispose();
    
    // 清理连接管理器
    final connectionManager = getIt<ConnectionManagerService>();
    await connectionManager.dispose();
  }
} 