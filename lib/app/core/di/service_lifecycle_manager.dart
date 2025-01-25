/// 服务生命周期管理器
class ServiceLifecycleManager {
  static final instance = ServiceLifecycleManager._();
  ServiceLifecycleManager._();

  final Map<Type, BaseService> _services = {};
  final Map<Type, List<Type>> _dependencies = {};
  final Set<Type> _initializing = {};
  bool _initialized = false;
  bool _isDisposing = false;

  /// 注册服务
  void registerService<T extends BaseService>(T service) {
    if (_services.containsKey(T)) {
      throw ServiceException('Service already registered: $T');
    }
    _services[T] = service;
    _dependencies[T] = service.dependencies;
  }

  /// 获取服务实例
  T getService<T extends BaseService>() {
    final service = _services[T];
    if (service == null) {
      throw ServiceException('Service not found: $T');
    }
    return service as T;
  }

  /// 初始化所有服务
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // 检查循环依赖
      _checkCircularDependencies();

      // 按依赖顺序初始化服务
      final sortedServices = _sortServicesByDependencies();
      for (final serviceType in sortedServices) {
        if (_initializing.contains(serviceType)) {
          throw ServiceException('Circular dependency detected: $serviceType');
        }

        try {
          _initializing.add(serviceType);
          final service = _services[serviceType]!;
          await service.initialize();
          _initializing.remove(serviceType);
        } catch (e) {
          _initializing.remove(serviceType);
          LoggerService.error('Failed to initialize service: $serviceType', error: e);
          rethrow;
        }
      }

      _initialized = true;
      LoggerService.info('All services initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize services', error: e);
      rethrow;
    }
  }

  /// 检查是否存在循环依赖
  void _checkCircularDependencies() {
    final visited = <Type>{};
    final recursionStack = <Type>{};

    void dfs(Type serviceType) {
      visited.add(serviceType);
      recursionStack.add(serviceType);

      for (final dependency in _dependencies[serviceType] ?? []) {
        if (!visited.contains(dependency)) {
          dfs(dependency);
        } else if (recursionStack.contains(dependency)) {
          throw ServiceException('Circular dependency detected: $serviceType -> $dependency');
        }
      }

      recursionStack.remove(serviceType);
    }

    for (final serviceType in _services.keys) {
      if (!visited.contains(serviceType)) {
        dfs(serviceType);
      }
    }
  }

  /// 按依赖顺序排序服务
  List<Type> _sortServicesByDependencies() {
    final sorted = <Type>[];
    final visited = <Type>{};

    void visit(Type serviceType) {
      if (visited.contains(serviceType)) return;
      visited.add(serviceType);

      for (final dependency in _dependencies[serviceType] ?? []) {
        visit(dependency);
      }

      sorted.add(serviceType);
    }

    for (final serviceType in _services.keys) {
      visit(serviceType);
    }

    return sorted;
  }

  /// 释放所有服务资源
  Future<void> dispose() async {
    if (!_initialized || _isDisposing) return;
    _isDisposing = true;

    try {
      // 按依赖顺序的反序释放服务
      final sortedServices = _sortServicesByDependencies().reversed;
      for (final serviceType in sortedServices) {
        try {
          final service = _services[serviceType]!;
          await service.dispose();
        } catch (e) {
          LoggerService.error('Failed to dispose service: $serviceType', error: e);
        }
      }

      _services.clear();
      _dependencies.clear();
      _initializing.clear();
      _initialized = false;
      _isDisposing = false;
      LoggerService.info('All services disposed');
    } catch (e) {
      _isDisposing = false;
      LoggerService.error('Failed to dispose services', error: e);
      rethrow;
    }
  }
}

/// Base class for all services
abstract class BaseService {
  /// Get service dependencies
  List<Type> get dependencies => const [];
  
  /// Initialize the service
  Future<void> initialize();
  
  /// Dispose the service
  Future<void> dispose();
}

/// Service lifecycle events
class ServiceEvent {
  final BaseService service;
  ServiceEvent(this.service);
}

class ServiceInitializedEvent extends ServiceEvent {
  ServiceInitializedEvent(super.service);
}

class ServiceFailedEvent extends ServiceEvent {
  final dynamic error;
  ServiceFailedEvent(super.service, this.error);
}

/// 服务异常
class ServiceException implements Exception {
  final String message;
  ServiceException(this.message);

  @override
  String toString() => 'ServiceException: $message';
} 