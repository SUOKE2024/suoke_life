import 'package:flutter/foundation.dart';

class Logger {
  static const String _tag = 'SuoKeLife';
  
  /// 调试日志
  static void debug(String message) {
    if (kDebugMode) {
      print('[$_tag][DEBUG] $message');
    }
  }
  
  /// 信息日志
  static void info(String message) {
    if (kDebugMode) {
      print('[$_tag][INFO] $message');
    }
  }
  
  /// 警告日志
  static void warning(String message) {
    if (kDebugMode) {
      print('[$_tag][WARN] $message');
    }
  }
  
  /// 错误日志
  static void error(String message, [dynamic error, StackTrace? stackTrace]) {
    if (kDebugMode) {
      print('[$_tag][ERROR] $message');
      if (error != null) {
        print('Error: $error');
      }
      if (stackTrace != null) {
        print('StackTrace: $stackTrace');
      }
    }
  }
} 