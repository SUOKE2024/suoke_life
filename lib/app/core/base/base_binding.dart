/// Base binding class that provides common functionality for all bindings.
/// 
/// Features:
/// - Dependency registration
/// - Service registration
/// - Controller registration
abstract class BaseBinding extends Binding {
  /// Register dependencies
  @override
  void dependencies() {
    // Register services
    registerServices();
    
    // Register repositories
    registerRepositories();
    
    // Register controllers
    registerControllers();
  }

  /// Register services
  void registerServices() {}

  /// Register repositories
  void registerRepositories() {}

  /// Register controllers
  void registerControllers() {}

  /// Register a lazy singleton
  void registerLazySingleton<T>(InstanceBuilderCallback<T> builder) {
    Get.lazyPut<T>(builder, fenix: true);
  }

  /// Register a singleton
  void registerSingleton<T>(T instance) {
    Get.put<T>(instance, permanent: true);
  }

  /// Register a factory
  void registerFactory<T>(InstanceBuilderCallback<T> builder) {
    Get.create<T>(builder);
  }

  /// Track binding events
  void trackEvent(String event, {Map<String, dynamic>? parameters}) {
    final analytics = DependencyManager.instance.get<AnalyticsService>();
    analytics.trackEvent(
      event,
      parameters: parameters,
      category: runtimeType.toString(),
    );
  }

  /// Log binding information
  void log(
    String message, {
    LogLevel level = LogLevel.info,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    switch (level) {
      case LogLevel.debug:
        LoggerService.debug(message, error: error, stackTrace: stackTrace);
        break;
      case LogLevel.info:
        LoggerService.info(message, error: error, stackTrace: stackTrace);
        break;
      case LogLevel.warning:
        LoggerService.warning(message, error: error, stackTrace: stackTrace);
        break;
      case LogLevel.error:
        LoggerService.error(message, error: error, stackTrace: stackTrace);
        break;
    }
  }
} 