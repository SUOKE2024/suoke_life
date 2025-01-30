import 'error_types.dart';

class AppException implements Exception {
  final ErrorType type;
  final String message;
  final dynamic data;

  const AppException({
    required this.type,
    required this.message,
    this.data,
  });

  @override
  String toString() => 'AppException: $message (${type.name})';

  Map<String, dynamic> toJson() => {
    'type': type.name,
    'message': message,
    'data': data,
  };
}

class NetworkException extends AppException {
  NetworkException({required String message, dynamic data})
      : super(
          type: ErrorType.network,
          message: message,
          data: data,
        );
}

class AuthException extends AppException {
  AuthException({required String message, dynamic data})
      : super(
          type: ErrorType.auth,
          message: message,
          data: data,
        );
}

class ValidationException extends AppException {
  ValidationException({required String message, dynamic data})
      : super(
          type: ErrorType.validation,
          message: message,
          data: data,
        );
}

class BusinessException extends AppException {
  BusinessException({required String message, dynamic data})
      : super(
          type: ErrorType.business,
          message: message,
          data: data,
        );
}

class TimeoutException extends AppException {
  TimeoutException({String? message, dynamic data})
      : super(
          type: ErrorType.timeout,
          message: message ?? '请求超时',
          data: data,
        );
}

class UnknownException extends AppException {
  UnknownException({String? message, dynamic data})
      : super(
          type: ErrorType.unknown,
          message: message ?? '未知错误',
          data: data,
        );
} 