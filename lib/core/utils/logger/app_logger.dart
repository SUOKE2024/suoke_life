import 'package:injectable/injectable.dart';

@singleton
class AppLogger {
  void error(String message, [dynamic error, StackTrace? stackTrace]) {
    print('ERROR: $message');
    if (error != null) print('Error details: $error');
    if (stackTrace != null) print('Stack trace: $stackTrace');
  }

  void info(String message) {
    print('INFO: $message');
  }

  void debug(String message) {
    print('DEBUG: $message');
  }

  void warning(String message) {
    print('WARNING: $message');
  }
} 