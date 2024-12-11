/// Base service class that provides common functionality for all services.
/// 
/// Features:
/// - Dependency declaration
/// - Lifecycle management
/// - Error handling
/// - Resource management
abstract class BaseService {
  /// Get service dependencies
  List<Type> get dependencies => const [];

  /// Initialize the service
  Future<void> initialize() async {}

  /// Dispose service resources
  Future<void> dispose() async {}

  /// Handle service errors
  void handleError(dynamic error, {StackTrace? stackTrace}) {
    LoggerService.error(
      'Service error',
      error: error,
      stackTrace: stackTrace,
    );
  }

  /// Track service events
  void trackEvent(String event, {Map<String, dynamic>? parameters}) {
    final analytics = DependencyManager.instance.get<AnalyticsService>();
    analytics.trackEvent(
      event,
      parameters: parameters,
      category: runtimeType.toString(),
    );
  }

  /// Log service information
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

  /// Get service configuration
  Future<T?> getConfig<T>(String key) async {
    final storage = DependencyManager.instance.get<StorageService>();
    return storage.get<T>('${runtimeType.toString()}_$key');
  }

  /// Set service configuration
  Future<void> setConfig<T>(String key, T value) async {
    final storage = DependencyManager.instance.get<StorageService>();
    await storage.set('${runtimeType.toString()}_$key', value);
  }

  /// Clear service configuration
  Future<void> clearConfig(String key) async {
    final storage = DependencyManager.instance.get<StorageService>();
    await storage.remove('${runtimeType.toString()}_$key');
  }
}

/// Log levels for service logging
enum LogLevel {
  debug,
  info,
  warning,
  error,
} 