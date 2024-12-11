/// 服务注册表
class ServiceRegistry {
  static final instance = ServiceRegistry._();
  ServiceRegistry._();

  final Map<Type, ServiceProvider> _providers = {};
  final Map<Type, dynamic> _singletons = {};
  bool _initialized = false;

  /// 注册单例服务
  void registerSingleton<T>(T instance) {
    if (_singletons.containsKey(T)) {
      throw Exception('Service ${T.toString()} already registered');
    }
    _singletons[T] = instance;
  }

  /// 注册服务提供者
  void register<T>(ServiceProvider<T> provider) {
    if (_providers.containsKey(T)) {
      throw Exception('Provider for ${T.toString()} already registered');
    }
    _providers[T] = provider;
  }

  /// 获取服务实例
  T get<T>() {
    // 优先返回单例
    final singleton = _singletons[T];
    if (singleton != null) {
      return singleton as T;
    }

    // 通过提供者创建实例
    final provider = _providers[T];
    if (provider == null) {
      throw Exception('No provider registered for ${T.toString()}');
    }

    return provider.create() as T;
  }

  /// 异步获取服务实例
  Future<T> getAsync<T>() async {
    // 优先返回单例
    final singleton = _singletons[T];
    if (singleton != null) {
      return singleton as T;
    }

    // 通过提供者创建实例
    final provider = _providers[T];
    if (provider == null) {
      throw Exception('No provider registered for ${T.toString()}');
    }

    if (provider is AsyncServiceProvider) {
      return await provider.createAsync() as T;
    }

    return provider.create() as T;
  }

  /// 初始化所有服务
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // 初始化所有单例服务
      for (final instance in _singletons.values) {
        if (instance is BaseService) {
          await instance.initialize();
        }
      }

      _initialized = true;
      LoggerService.info('Service registry initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize service registry', error: e);
      rethrow;
    }
  }

  /// 释放所有服务资源
  Future<void> dispose() async {
    if (!_initialized) return;

    try {
      // 释放所有单例服务
      for (final instance in _singletons.values) {
        if (instance is BaseService) {
          await instance.dispose();
        }
      }

      _providers.clear();
      _singletons.clear();
      _initialized = false;
      LoggerService.info('Service registry disposed');
    } catch (e) {
      LoggerService.error('Failed to dispose service registry', error: e);
      rethrow;
    }
  }
}

/// 服务提供者接口
abstract class ServiceProvider<T> {
  T create();
}

/// 异步服务提供者接口
abstract class AsyncServiceProvider<T> implements ServiceProvider<T> {
  Future<T> createAsync();

  @override
  T create() {
    throw UnsupportedError('Use createAsync() for async service creation');
  }
} 