abstract class AppError implements Exception {
  final String message;
  final String? code;
  final dynamic details;

  AppError(this.message, {this.code, this.details});

  @override
  String toString() => 'AppError: $message (code: $code)';
}

class NetworkError extends AppError {
  NetworkError(String message, {String? code, dynamic details})
      : super(message, code: code, details: details);
}

class AuthError extends AppError {
  AuthError(String message, {String? code, dynamic details})
      : super(message, code: code, details: details);
}

class StorageError extends AppError {
  StorageError(String message, {String? code, dynamic details})
      : super(message, code: code, details: details);
}

class BusinessError extends AppError {
  BusinessError(String message, {String? code, dynamic details})
      : super(message, code: code, details: details);
}

class ValidationError extends AppError {
  final Map<String, String> errors;

  ValidationError(String message, this.errors, {String? code, dynamic details})
      : super(message, code: code, details: details);
} 