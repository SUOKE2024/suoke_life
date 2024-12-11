/// Service that handles application logging.
/// 
/// Features:
/// - Log levels
/// - File logging
/// - Remote logging
/// - Error reporting
class LoggerService extends BaseService {
  static final instance = LoggerService._();
  LoggerService._();

  late final Logger _logger;
  late final String _logPath;
  bool _initialized = false;

  @override
  List<Type> get dependencies => [
    StorageService,
    NetworkService,
  ];

  @override
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Initialize log path
      final appDir = await getApplicationDocumentsDirectory();
      _logPath = '${appDir.path}/logs';
      
      // Create logs directory if it doesn't exist
      await Directory(_logPath).create(recursive: true);

      // Initialize logger
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
          ConsoleOutput(),
          FileOutput(file: File('$_logPath/app.log')),
        ]),
      );

      _initialized = true;
      info('Logger initialized');
    } catch (e) {
      print('Failed to initialize logger: $e');
    }
  }

  /// Log debug message
  static void debug(
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    String? context,
    Map<String, dynamic>? extras,
  }) {
    instance._log(
      'DEBUG',
      message,
      error: error,
      stackTrace: stackTrace,
      context: context,
      extras: extras,
    );
  }

  /// Log info message
  static void info(
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    String? context,
    Map<String, dynamic>? extras,
  }) {
    instance._log(
      'INFO',
      message,
      error: error,
      stackTrace: stackTrace,
      context: context,
      extras: extras,
    );
  }

  /// Log warning message
  static void warning(
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    String? context,
    Map<String, dynamic>? extras,
  }) {
    instance._log(
      'WARNING',
      message,
      error: error,
      stackTrace: stackTrace,
      context: context,
      extras: extras,
    );
  }

  /// Log error message
  static void error(
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    String? context,
    Map<String, dynamic>? extras,
  }) {
    instance._log(
      'ERROR',
      message,
      error: error,
      stackTrace: stackTrace,
      context: context,
      extras: extras,
    );
  }

  void _log(
    String level,
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    String? context,
    Map<String, dynamic>? extras,
  }) {
    if (!_initialized) return;

    try {
      final logMessage = _formatMessage(
        level,
        message,
        error: error,
        context: context,
        extras: extras,
      );

      switch (level) {
        case 'DEBUG':
          _logger.d(logMessage, error, stackTrace);
          break;
        case 'INFO':
          _logger.i(logMessage, error, stackTrace);
          break;
        case 'WARNING':
          _logger.w(logMessage, error, stackTrace);
          break;
        case 'ERROR':
          _logger.e(logMessage, error, stackTrace);
          _reportError(message, error, stackTrace, context, extras);
          break;
      }
    } catch (e) {
      print('Logging failed: $e');
    }
  }

  String _formatMessage(
    String level,
    String message, {
    dynamic error,
    String? context,
    Map<String, dynamic>? extras,
  }) {
    final buffer = StringBuffer();
    
    // Add timestamp
    buffer.write('[${DateTime.now().toIso8601String()}]');
    
    // Add level
    buffer.write('[$level]');
    
    // Add context if available
    if (context != null) {
      buffer.write('[$context]');
    }
    
    // Add message
    buffer.write(' $message');
    
    // Add error if available
    if (error != null) {
      buffer.write('\nError: $error');
    }
    
    // Add extras if available
    if (extras?.isNotEmpty ?? false) {
      buffer.write('\nExtras: $extras');
    }
    
    return buffer.toString();
  }

  Future<void> _reportError(
    String message,
    dynamic error,
    StackTrace? stackTrace,
    String? context,
    Map<String, dynamic>? extras,
  ) async {
    try {
      final analytics = DependencyManager.instance.get<AnalyticsService>();
      await analytics.logError(
        message,
        error: error,
        stackTrace: stackTrace,
        context: context,
        extras: extras,
      );
    } catch (e) {
      print('Error reporting failed: $e');
    }
  }

  @override
  Future<void> dispose() async {
    _initialized = false;
  }
}

/// Logger output that writes to multiple destinations
class MultiOutput extends LogOutput {
  final List<LogOutput> outputs;
  MultiOutput(this.outputs);

  @override
  void output(OutputEvent event) {
    for (final output in outputs) {
      output.output(event);
    }
  }
}

/// Logger output that writes to a file
class FileOutput extends LogOutput {
  final File file;
  FileOutput({required this.file});

  @override
  void output(OutputEvent event) {
    final output = event.lines.join('\n');
    file.writeAsStringSync('$output\n', mode: FileMode.append);
  }
} 