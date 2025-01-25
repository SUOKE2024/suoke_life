abstract class Failure {
  final String message;
  final String? code;
  final dynamic data;

  const Failure({
    required this.message,
    this.code,
    this.data,
  });
}

class ServerFailure extends Failure {
  const ServerFailure({
    required String message,
    String? code,
    dynamic data,
  }) : super(
          message: message,
          code: code,
          data: data,
        );
}

class CacheFailure extends Failure {
  const CacheFailure({
    required String message,
    String? code,
    dynamic data,
  }) : super(
          message: message,
          code: code,
          data: data,
        );
}

class NetworkFailure extends Failure {
  const NetworkFailure({
    required String message,
    String? code,
    dynamic data,
  }) : super(
          message: message,
          code: code,
          data: data,
        );
} 