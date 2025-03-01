import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';
import '../config/environment.dart';

/// 简单的日志工具类
class Logger {
  final String tag;
  
  Logger({this.tag = 'SuokeLife'});
  
  /// 调试日志
  void d(String message) {
    if (kDebugMode) {
      print('D/$tag: $message');
    }
  }
  
  /// 信息日志
  void i(String message) {
    if (kDebugMode) {
      print('I/$tag: $message');
    }
  }
  
  /// 警告日志
  void w(String message) {
    if (kDebugMode) {
      print('W/$tag: $message');
    }
  }
  
  /// 错误日志
  void e(String message, [dynamic error, StackTrace? stackTrace]) {
    if (kDebugMode) {
      print('E/$tag: $message');
      if (error != null) {
        print('Error: $error');
      }
      if (stackTrace != null) {
        print('StackTrace: $stackTrace');
      }
    }
  }
}

/// 全局日志实例
final logger = Logger();

/// 配置日志记录器
void configureLogger() {
  // 设置日志级别
  Level logLevel;
  if (Environment.isDevelopment) {
    // 开发环境显示所有日志
    logLevel = Level.verbose;
  } else if (Environment.isProduction) {
    // 生产环境只显示警告和错误
    logLevel = Level.warning;
  } else {
    // 其他环境显示调试级别以上的日志
    logLevel = Level.debug;
  }
  
  // 创建自定义打印器
  final printer = PrettyPrinter(
    methodCount: Environment.isDevelopment ? 2 : 0,
    errorMethodCount: 8,
    lineLength: 120,
    colors: true,
    printEmojis: true,
    printTime: true,
  );
  
  // 创建和配置日志记录器
  logger._logger = Logger(
    filter: ProductionFilter(),
    level: logLevel,
    printer: printer,
    output: ConsoleOutput(),
  );
  
  // 替换Flutter默认的错误处理
  FlutterError.onError = (details) {
    logger.e(
      'Flutter错误',
      error: details.exception,
      stackTrace: details.stack,
    );
    
    // 让Flutter默认处理继续执行（这对于调试很有用）
    if (Environment.isDevelopment) {
      FlutterError.dumpErrorToConsole(details);
    }
  };
}

/// 日志使用示例:
/// ```
/// logger.v("详细信息");
/// logger.d("调试信息");
/// logger.i("信息");
/// logger.w("警告");
/// logger.e("错误", error: e, stackTrace: s);
/// logger.wtf("严重错误");
/// ``` 