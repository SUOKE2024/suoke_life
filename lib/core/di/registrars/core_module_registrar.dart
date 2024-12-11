import 'package:get_it/get_it.dart';
import '../module_registrar.dart';
import '../../error/error_handler_service.dart';
import '../../auth/services/auth_service.dart';
import '../../routes/route_analytics.dart';
import '../../routes/route_error_handler.dart';

/// 核心模块注册器
class CoreModuleRegistrar implements ModuleRegistrar {
  @override
  String get moduleName => '核心模块';
  
  @override
  List<Type> get dependencies => [];  // 核心模块没有外部依赖

  @override
  Future<void> register(GetIt getIt) async {
    // 错误处理服务
    getIt.registerLazySingleton(() => ErrorHandlerService());
    getIt.registerLazySingleton(() => RouteErrorHandler());
    
    // 路由分析服务
    getIt.registerLazySingleton(() => RouteAnalytics());
  }

  @override
  Future<void> registerAsync(GetIt getIt) async {
    // 认证服务需要异步初始化
    await getIt.registerSingletonAsync(
      () => AuthService().init(),
      signalsReady: true,
    );
    
    // 路由分析服务需要异步初始化
    await getIt.registerSingletonAsync(
      () => RouteAnalytics().init(),
      signalsReady: true,
    );
  }

  @override
  Future<void> onModuleReady(GetIt getIt) async {
    // 确保认证服务已经准备就绪
    await getIt.isReady<AuthService>();
    
    // 初始化错误处理
    final errorHandler = getIt<ErrorHandlerService>();
    errorHandler.initialize();
  }

  @override
  Future<void> onModuleDispose(GetIt getIt) async {
    // 清理认证服务
    final authService = getIt<AuthService>();
    await authService.dispose();
  }
} 