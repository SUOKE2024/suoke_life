import 'package:injectable/injectable.dart';
import 'package:logger/logger.dart' as log;
import '../analytics/analytics_service.dart';

@singleton
class AppLogger {
  final log.Logger _logger;
  final AnalyticsService _analytics;

  AppLogger(this._analytics)
      : _logger = log.Logger(
          printer: log.PrettyPrinter(
            methodCount: 2,
            errorMethodCount: 8,
            lineLength: 120,
            colors: true,
            printEmojis: true,
            printTime: true,
          ),
        );

  void debug(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.d(message, error: error, stackTrace: stackTrace);
  }

  void info(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.i(message, error: error, stackTrace: stackTrace);
  }

  void warning(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.w(message, error: error, stackTrace: stackTrace);
    _analytics.trackEvent('warning_logged', {
      'message': message,
      'error': error?.toString(),
    });
  }

  void error(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e(message, error: error, stackTrace: stackTrace);
    _analytics.trackEvent('error_logged', {
      'message': message,
      'error': error?.toString(),
      'stackTrace': stackTrace?.toString(),
    });
  }

  void fatal(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.f(message, error: error, stackTrace: stackTrace);
    _analytics.trackEvent('fatal_error_logged', {
      'message': message,
      'error': error?.toString(),
      'stackTrace': stackTrace?.toString(),
    });
  }
} 