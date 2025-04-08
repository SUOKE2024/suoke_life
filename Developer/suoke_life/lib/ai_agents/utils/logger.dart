// 日志工具类
// 用于输出调试信息和错误

import 'dart:developer' as developer;
import '../config/agent_config.dart';

/// 日志级别枚举
enum LogLevel {
  debug,   // 调试信息
  info,    // 信息
  warning, // 警告
  error,   // 错误
  none     // 不输出日志
}

/// 日志工具类
class LoggerUtil {
  /// 当前日志级别
  static LogLevel _level = LogLevel.info;
  
  /// 设置日志级别
  static void setLevel(LogLevel level) {
    _level = level;
  }
  
  /// 输出调试日志
  static void debug(String message) {
    if (_shouldLog(LogLevel.debug)) {
      _log('DEBUG', message);
    }
  }
  
  /// 输出信息日志
  static void info(String message) {
    if (_shouldLog(LogLevel.info)) {
      _log('INFO', message);
    }
  }
  
  /// 输出警告日志
  static void warning(String message) {
    if (_shouldLog(LogLevel.warning)) {
      _log('WARN', message);
    }
  }
  
  /// 输出错误日志
  static void error(String message, [dynamic error, StackTrace? stackTrace]) {
    if (_shouldLog(LogLevel.error)) {
      _log('ERROR', message);
      
      if (error != null) {
        _log('ERROR', 'Error details: $error');
      }
      
      if (stackTrace != null) {
        _log('ERROR', 'Stack trace: $stackTrace');
      }
    }
  }
  
  /// 输出日志
  static void _log(String level, String message) {
    final timestamp = DateTime.now().toIso8601String();
    final formattedMessage = '[$timestamp] $level: $message';
    
    developer.log(formattedMessage, name: 'SUOKE.AGENT');
  }
  
  /// 判断是否应该输出日志
  static bool _shouldLog(LogLevel messageLevel) {
    // 如果调试模式开启，总是输出所有级别日志
    if (AgentConfig.enableDebug) {
      return true;
    }
    
    // 根据级别判断
    return messageLevel.index >= _level.index;
  }
} 