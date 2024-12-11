import 'dart:developer' as developer;
import 'dart:io';

import 'package:path/path.dart' as path;

enum LogLevel {
  debug,
  info,
  warning,
  error,
}

class AppLogger {
  static final AppLogger _instance = AppLogger._internal();
  static AppLogger get instance => _instance;

  late final File _logFile;
  bool _initialized = false;

  AppLogger._internal();

  Future<void> init() async {
    if (_initialized) return;

    final appDir = await getApplicationDocumentsDirectory();
    final logDir = Directory(path.join(appDir.path, 'logs'));
    if (!await logDir.exists()) {
      await logDir.create(recursive: true);
    }

    final today = DateTime.now().toIso8601String().split('T')[0];
    _logFile = File(path.join(logDir.path, 'app_$today.log'));
    _initialized = true;
  }

  Future<void> log(
    String message, {
    LogLevel level = LogLevel.info,
    Object? error,
    StackTrace? stackTrace,
  }) async {
    if (!_initialized) await init();

    final timestamp = DateTime.now().toIso8601String();
    final logMessage = '$timestamp [${level.name.toUpperCase()}] $message';

    // 打印到控制台
    developer.log(
      message,
      time: DateTime.now(),
      level: _getLevelValue(level),
      error: error,
      stackTrace: stackTrace,
    );

    // 写入文件
    try {
      await _logFile.writeAsString(
        '$logMessage\n',
        mode: FileMode.append,
      );

      if (error != null) {
        await _logFile.writeAsString(
          'Error: $error\n',
          mode: FileMode.append,
        );
      }

      if (stackTrace != null) {
        await _logFile.writeAsString(
          'StackTrace: $stackTrace\n',
          mode: FileMode.append,
        );
      }
    } catch (e) {
      developer.log(
        'Failed to write log to file: $e',
        level: 1000,
      );
    }
  }

  void debug(String message, {Object? error, StackTrace? stackTrace}) {
    log(message, level: LogLevel.debug, error: error, stackTrace: stackTrace);
  }

  void info(String message, {Object? error, StackTrace? stackTrace}) {
    log(message, level: LogLevel.info, error: error, stackTrace: stackTrace);
  }

  void warning(String message, {Object? error, StackTrace? stackTrace}) {
    log(message, level: LogLevel.warning, error: error, stackTrace: stackTrace);
  }

  void error(String message, {Object? error, StackTrace? stackTrace}) {
    log(message, level: LogLevel.error, error: error, stackTrace: stackTrace);
  }

  int _getLevelValue(LogLevel level) {
    switch (level) {
      case LogLevel.debug:
        return 500;
      case LogLevel.info:
        return 800;
      case LogLevel.warning:
        return 900;
      case LogLevel.error:
        return 1000;
    }
  }

  Future<List<String>> getLogs({int maxLines = 100}) async {
    if (!_initialized) await init();

    try {
      final lines = await _logFile.readAsLines();
      return lines.reversed.take(maxLines).toList();
    } catch (e) {
      developer.log('Failed to read logs: $e', level: 1000);
      return [];
    }
  }

  Future<void> clearLogs() async {
    if (!_initialized) await init();

    try {
      await _logFile.writeAsString('');
    } catch (e) {
      developer.log('Failed to clear logs: $e', level: 1000);
    }
  }
} 