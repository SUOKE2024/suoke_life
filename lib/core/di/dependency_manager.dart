import 'package:get/get.dart';
import '../services/service_manager.dart';
import '../storage/storage_manager.dart';
import '../network/api_client.dart';
// 导入其他管理器...

/// Core dependency manager that handles registration and resolution of dependencies.
/// 
/// Follows the initialization order:
/// 1. Core Services
/// 2. Base Modules  
/// 3. Feature Modules
/// 4. Utils
class DependencyManager {
  static final instance = DependencyManager._();
  DependencyManager._();

  final _bindings = <Type, InstanceBinding>{};
  final _singletons = <Type, dynamic>{};
  final _factories = <Type, Function>{};

  /// Initialize all dependencies in proper order
  Future<void> initialize() async {
    try {
      // 1. Core Services
      await _registerCoreServices();
      
      // 2. Base Modules
      await _registerBaseModules();
      
      // 3. Feature Modules  
      await _registerFeatureModules();
      
      // 4. Utils
      _registerUtils();
    } catch (e) {
      LoggerService.error('Failed to initialize dependencies', e);
      rethrow;
    }
  }

  /// Register core services required by the application
  Future<void> _registerCoreServices() async {
    // Storage
    await registerSingletonAsync(() async {
      final storage = StorageService();
      await storage.initialize();
      return storage;
    });

    // Network
    await registerSingletonAsync(() async {
      final network = NetworkService();
      await network.initialize();
      return network;
    });

    // Core services
    registerLazySingleton(() => EventBusService());
    registerLazySingleton(() => LoggerService());
    registerLazySingleton(() => ErrorHandlerService());
  }

  /// Register base modules
  Future<void> _registerBaseModules() async {
    registerModule(CoreModule());
    registerModule(NetworkModule());
    registerModule(StorageModule());
  }

  /// Register feature modules
  Future<void> _registerFeatureModules() async {
    registerModule(ChatModule());
    registerModule(AIModule());
    registerModule(GamesModule());
  }

  /// Register utility classes
  void _registerUtils() {
    registerFactory(() => DateFormatter());
    registerFactory(() => StringUtils());
    registerFactory(() => ValidationUtils());
  }

  // Registration methods
  void registerSingleton<T>(T instance) {
    _singletons[T] = instance;
  }

  Future<void> registerSingletonAsync<T>(Future<T> Function() asyncBuilder) async {
    final instance = await asyncBuilder();
    registerSingleton<T>(instance);
  }

  void registerLazySingleton<T>(T Function() builder) {
    _bindings[T] = LazyBinding(builder);
  }

  void registerFactory<T>(T Function() factory) {
    _factories[T] = factory;
  }

  void registerModule(BaseModule module) {
    module.dependencies().forEach((type, builder) {
      registerLazySingleton(builder);
    });
  }

  // Resolution methods
  T get<T>() {
    try {
      // Check singletons
      if (_singletons.containsKey(T)) {
        return _singletons[T] as T;
      }

      // Check lazy bindings
      if (_bindings.containsKey(T)) {
        final binding = _bindings[T]!;
        if (binding is LazyBinding) {
          final instance = binding.builder();
          _singletons[T] = instance;
          return instance as T;
        }
      }

      // Check factories
      if (_factories.containsKey(T)) {
        return _factories[T]!() as T;
      }

      throw DependencyException('No dependency found for type $T');
    } catch (e) {
      LoggerService.error('Failed to resolve dependency $T', e);
      rethrow;
    }
  }

  bool isRegistered<T>() {
    return _singletons.containsKey(T) || 
           _bindings.containsKey(T) || 
           _factories.containsKey(T);
  }

  void unregister<T>() {
    _singletons.remove(T);
    _bindings.remove(T);
    _factories.remove(T);
  }

  void reset() {
    _singletons.clear();
    _bindings.clear();
    _factories.clear();
  }
}

/// Base class for dependency bindings
abstract class InstanceBinding {
  dynamic get instance;
}

/// Lazy loading binding implementation
class LazyBinding implements InstanceBinding {
  final Function builder;
  dynamic _instance;

  LazyBinding(this.builder);

  @override
  dynamic get instance {
    _instance ??= builder();
    return _instance;
  }
}

/// Exception thrown for dependency resolution errors
class DependencyException implements Exception {
  final String message;
  DependencyException(this.message);

  @override
  String toString() => 'DependencyException: $message';
} 