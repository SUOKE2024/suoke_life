class AppErrorHandler {
  static void initialize() {
    // 设置全局错误处理
    FlutterError.onError = (details) {
      LoggerService.error(
        'Flutter Error',
        error: details.exception,
        stackTrace: details.stack,
      );
    };

    // 设置异步错误处理
    PlatformDispatcher.instance.onError = (error, stack) {
      LoggerService.error(
        'Platform Error',
        error: error,
        stackTrace: stack,
      );
      return true;
    };
  }
} 