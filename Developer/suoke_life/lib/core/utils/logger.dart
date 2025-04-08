import 'package:logger/logger.dart' as logger_pkg;
import 'package:flutter/foundation.dart';

/// 应用统一日志记录器
final logger = logger_pkg.Logger(
  printer: logger_pkg.PrettyPrinter(
    methodCount: 2,
    errorMethodCount: 8,
    lineLength: 120,
    colors: true,
    printEmojis: true,
    printTime: true
  ),
  level: logger_pkg.Level.debug,
);

/// 日志级别枚举，用于控制日志输出
enum LogLevel {
  /// 详细信息
  verbose,
  
  /// 调试信息
  debug,
  
  /// 普通信息
  info,
  
  /// 警告信息
  warning,
  
  /// 错误信息
  error,
  
  /// 致命错误
  fatal,
}

/// 日志工具类
///
/// 提供应用程序日志记录功能
class Logger {
  /// 当前日志级别
  static LogLevel _currentLevel = kDebugMode ? LogLevel.verbose : LogLevel.info;
  
  /// 是否启用日志
  static bool _enabled = true;
  
  /// 设置日志级别
  static void setLogLevel(LogLevel level) {
    _currentLevel = level;
  }
  
  /// 启用日志
  static void enable() {
    _enabled = true;
  }
  
  /// 禁用日志
  static void disable() {
    _enabled = false;
  }
  
  /// 记录详细日志
  static void v(String tag, String message) {
    _log(LogLevel.verbose, tag, message);
  }
  
  /// 记录调试日志
  static void d(String tag, String message) {
    _log(LogLevel.debug, tag, message);
  }
  
  /// 记录信息日志
  static void i(String tag, String message) {
    _log(LogLevel.info, tag, message);
  }
  
  /// 记录警告日志
  static void w(String tag, String message) {
    _log(LogLevel.warning, tag, message);
  }
  
  /// 记录错误日志
  static void e(String tag, String message) {
    _log(LogLevel.error, tag, message);
  }
  
  /// 记录致命错误日志
  static void f(String tag, String message) {
    _log(LogLevel.fatal, tag, message);
  }
  
  /// 为API健康服务提供的信息日志方法
  static void info(String message) {
    i("API", message);
  }
  
  /// 为API健康服务提供的警告日志方法
  static void warning(String message) {
    w("API", message);
  }
  
  /// 为API健康服务提供的错误日志方法
  static void error(String message, [dynamic error, StackTrace? stackTrace]) {
    e("API", "$message ${error != null ? '错误: $error' : ''}");
    if (kDebugMode && stackTrace != null) {
      print(stackTrace);
    }
  }
  
  /// 记录日志
  static void _log(LogLevel level, String tag, String message) {
    if (!_enabled || level.index < _currentLevel.index) {
      return;
    }
    
    final now = DateTime.now();
    final timestamp = '${now.hour.toString().padLeft(2, '0')}:'
        '${now.minute.toString().padLeft(2, '0')}:'
        '${now.second.toString().padLeft(2, '0')}.'
        '${now.millisecond.toString().padLeft(3, '0')}';
    
    final levelStr = level.toString().split('.').last.toUpperCase();
    final output = '[$timestamp] $levelStr/$tag: $message';
    
    // 在调试模式下打印到控制台
    if (kDebugMode) {
      print(output);
    }
    
    // 在实际应用中，这里应该添加日志文件写入或远程日志上传等功能
  }
}

/// 日志工具类，提供便捷的日志记录方法
class LogUtil {
  static void v(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    if (error != null) {
      logger.v("$message", error, stackTrace);
    } else {
      logger.v("$message");
    }
  }

  static void d(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    if (error != null) {
      logger.d("$message", error, stackTrace);
    } else {
      logger.d("$message");
    }
  }

  static void i(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    if (error != null) {
      logger.i("$message", error, stackTrace);
    } else {
      logger.i("$message");
    }
  }

  static void w(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    if (error != null) {
      logger.w("$message", error, stackTrace);
    } else {
      logger.w("$message");
    }
  }

  static void e(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    if (error != null) {
      logger.e("$message", error, stackTrace);
    } else {
      logger.e("$message");
    }
  }
}

/// 配置日志系统
void configureLogger() {
  // 配置全局静态Logger类
  Logger.enable();
  if (kDebugMode) {
    Logger.setLogLevel(LogLevel.verbose);
  } else {
    Logger.setLogLevel(LogLevel.info);
  }
  
  // 配置logger库实例
  logger.level = kDebugMode ? logger_pkg.Level.verbose : logger_pkg.Level.info;
  
  Logger.i("Logger", "日志系统已配置，当前级别: ${kDebugMode ? 'VERBOSE' : 'INFO'}");
}
