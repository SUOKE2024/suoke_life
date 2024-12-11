class LoggerManager {
  static final instance = LoggerManager._();
  LoggerManager._();

  late final Logger _logger;
  bool _initialized = false;

  Future<void> initialize({
    required String logPath,
    required bool enableConsole,
    required LogLevel minLevel,
  }) async {
    if (_initialized) return;

    _logger = Logger(
      printer: PrettyPrinter(
        methodCount: 2,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
        printTime: true,
      ),
      output: MultiOutput([
        if (enableConsole) ConsoleOutput(),
        FileOutput(file: File(logPath)),
      ]),
      level: minLevel,
    );

    _initialized = true;
  }

  void debug(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.d(message, error, stackTrace);
  }

  void info(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.i(message, error, stackTrace);
  }

  void warning(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.w(message, error, stackTrace);
  }

  void error(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e(message, error, stackTrace);
  }
} 