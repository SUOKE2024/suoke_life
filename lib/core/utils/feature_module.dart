/// 功能模块基类，提供模块生命周期和依赖管理
abstract class FeatureModule extends BaseModule {
  /// 模块配置
  ModuleConfig? get config => null;

  /// 模块路由
  List<GetPage> get routes => const [];

  /// 模块中间件
  List<GetMiddleware> get middleware => const [];

  /// 模块绑定
  List<Bindings> get bindings => const [];

  /// 模块服务
  @override
  Map<Type, BaseService> services() => const {};

  /// 模块初始化
  @override
  Future<void> onInitialize() async {
    try {
      // 注册路由
      _registerRoutes();

      // 注册中间件
      _registerMiddleware();

      // 注册绑定
      _registerBindings();

      // 初始化配置
      await _initializeConfig();

      // 初始化服务
      await _initializeServices();

      LoggerService.info('Feature module initialized: $name');
    } catch (e) {
      LoggerService.error(
        'Failed to initialize feature module: $name',
        error: e,
      );
      rethrow;
    }
  }

  /// 注册路由
  void _registerRoutes() {
    for (final route in routes) {
      Get.addPage(route);
    }
  }

  /// 注册中间件
  void _registerMiddleware() {
    for (final mw in middleware) {
      Get.addMiddleware(mw);
    }
  }

  /// 注册绑定
  void _registerBindings() {
    for (final binding in bindings) {
      binding.dependencies();
    }
  }

  /// 初始化配置
  Future<void> _initializeConfig() async {
    if (config != null) {
      final configManager = DependencyManager.instance.get<AppConfigManager>();
      await configManager.setConfig(name, config!);
    }
  }

  /// 初始化服务
  Future<void> _initializeServices() async {
    final serviceMap = services();
    for (final entry in serviceMap.entries) {
      await ServiceLifecycleManager.instance.registerService(entry.value);
    }
  }

  @override
  Future<void> onDispose() async {
    try {
      // 移除路由
      for (final route in routes) {
        Get.removeRoute(route.name);
      }

      // 移除中间件
      for (final mw in middleware) {
        Get.removeMiddleware(mw);
      }

      // 销毁服务
      final serviceMap = services();
      for (final entry in serviceMap.entries) {
        await ServiceLifecycleManager.instance.disposeService(entry.key);
      }

      LoggerService.info('Feature module disposed: $name');
    } catch (e) {
      LoggerService.error(
        'Failed to dispose feature module: $name',
        error: e,
      );
      rethrow;
    }
  }

  /// 获取模块配置
  Future<T?> getConfig<T>() async {
    final configManager = DependencyManager.instance.get<AppConfigManager>();
    return configManager.getConfig<T>(name);
  }

  /// 设置模块配置
  Future<void> setConfig<T>(T config) async {
    final configManager = DependencyManager.instance.get<AppConfigManager>();
    await configManager.setConfig(name, config);
  }
} 