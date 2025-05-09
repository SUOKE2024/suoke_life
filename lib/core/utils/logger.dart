import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:logger/logger.dart';

/// 应用程序日志记录工具
///
/// 提供不同级别的日志记录功能，根据环境自动调整日志级别
class AppLogger {
  static final AppLogger _instance = AppLogger._internal();
  late final Logger _logger;

  /// 单例访问器
  factory AppLogger() => _instance;

  AppLogger._internal() {
    final logLevel = _getLogLevel();

    _logger = Logger(
      printer: PrettyPrinter(
        methodCount: 2,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
        printTime: true,
      ),
      level: logLevel,
      filter: ProductionFilter(),
    );

    debugPrint('日志级别设置为: ${logLevel.name}');
  }

  /// 获取环境配置的日志级别
  Level _getLogLevel() {
    if (!kReleaseMode) {
      return Level.debug;
    }

    final configLevel = dotenv.env['LOG_LEVEL'] ?? 'info';
    switch (configLevel.toLowerCase()) {
      case 'debug':
        return Level.debug;
      case 'info':
        return Level.info;
      case 'warning':
        return Level.warning;
      case 'error':
        return Level.error;
      default:
        return Level.info;
    }
  }

  /// 调试级别日志
  void d(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.d(message);
  }

  /// 信息级别日志
  void i(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.i(message);
  }

  /// 警告级别日志
  void w(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.w(message);
  }

  /// 错误级别日志
  void e(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e(message);
  }

  /// 致命错误日志
  void wtf(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.wtf(message);
  }
}
