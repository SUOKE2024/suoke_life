class AppExceptionHandler {
  static void init() {
    FlutterError.onError = (details) {
      FlutterError.presentError(details);
      _reportError(details.exception, details.stack);
    };

    PlatformDispatcher.instance.onError = (error, stack) {
      _reportError(error, stack);
      return true;
    };
  }

  static void _reportError(dynamic error, StackTrace? stack) {
    AppLogger.error(
      'Uncaught error',
      error: error,
      stackTrace: stack,
    );
    
    if (error is! AppException) {
      error = AppException(error.toString());
    }
    
    _showErrorDialog(error as AppException);
  }

  static void _showErrorDialog(AppException error) {
    if (Get.isDialogOpen ?? false) return;
    
    Get.dialog(
      ErrorDialog(error: error),
      barrierDismissible: false,
    );
  }
} 