enum ErrorSeverity {
  low,
  medium,
  high,
}

class ErrorStrategy {
  final int? maxRetries;
  final Duration? retryDelay;
  final bool exponentialBackoff;
  final bool fallbackEnabled;
  final bool notifyUser;
  final ErrorSeverity severity;
  final Map<String, dynamic>? options;

  const ErrorStrategy({
    this.maxRetries,
    this.retryDelay,
    this.exponentialBackoff = false,
    this.fallbackEnabled = false,
    this.notifyUser = true,
    this.severity = ErrorSeverity.medium,
    this.options,
  });
}

class ErrorCounter {
  int total = 0;
  final List<DateTime> errorTimes = [];
  DateTime? lastError;

  void increment() {
    total++;
    final now = DateTime.now();
    errorTimes.add(now);
    lastError = now;
  }

  void reset() {
    total = 0;
    errorTimes.clear();
    lastError = null;
  }

  int getRecentCount(Duration window) {
    final cutoff = DateTime.now().subtract(window);
    return errorTimes.where((time) => time.isAfter(cutoff)).length;
  }

  void cleanup(DateTime cutoff) {
    errorTimes.removeWhere((time) => time.isBefore(cutoff));
  }
}

class ErrorStats {
  final int total;
  final int recent;
  final DateTime? lastError;
  final String errorType;

  const ErrorStats({
    required this.total,
    required this.recent,
    this.lastError,
    required this.errorType,
  });

  Map<String, dynamic> toMap() => {
    'total': total,
    'recent': recent,
    'last_error': lastError?.toIso8601String(),
    'error_type': errorType,
  };
} 