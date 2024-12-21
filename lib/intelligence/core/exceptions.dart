class AIException implements Exception {
  final String message;
  final String? code;
  final dynamic details;

  AIException(this.message, {this.code, this.details});

  @override
  String toString() => 'AIException: $message (code: $code)';
}

class AIAccessException extends AIException {
  AIAccessException(String message, {String? code, dynamic details})
      : super(message, code: code ?? 'ACCESS_DENIED', details: details);
}

class AIQuotaException extends AIException {
  AIQuotaException(String message, {String? code, dynamic details})
      : super(message, code: code ?? 'QUOTA_EXCEEDED', details: details);
} 