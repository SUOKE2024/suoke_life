import 'package:equatable/equatable.dart';

/// 错误基类
abstract class Failure extends Equatable {
  final String message;
  final String? code;
  
  const Failure({
    required this.message,
    this.code,
  });
  
  @override
  List<Object?> get props => [message, code];
}

/// 服务器错误
class ServerFailure extends Failure {
  final int? statusCode;
  
  const ServerFailure({
    required String message,
    String? code,
    this.statusCode,
  }) : super(
    message: message,
    code: code,
  );
  
  @override
  List<Object?> get props => [...super.props, statusCode];
}

/// 网络错误
class NetworkFailure extends Failure {
  const NetworkFailure({
    required String message,
    String? code,
  }) : super(
    message: message,
    code: code,
  );
}

/// 缓存错误
class CacheFailure extends Failure {
  const CacheFailure({
    required String message,
    String? code,
  }) : super(
    message: message,
    code: code,
  );
}

/// 数据库错误
class DatabaseFailure extends Failure {
  final String? operation;
  final String? table;
  
  const DatabaseFailure({
    required String message,
    String? code,
    this.operation,
    this.table,
  }) : super(
    message: message,
    code: code,
  );
  
  @override
  List<Object?> get props => [...super.props, operation, table];
}

/// 未授权错误
class UnauthorizedFailure extends Failure {
  const UnauthorizedFailure({
    required String message,
    String? code,
  }) : super(
    message: message,
    code: code,
  );
}

/// 验证错误
class ValidationFailure extends Failure {
  final Map<String, List<String>>? errors;
  
  const ValidationFailure({
    required String message,
    String? code,
    this.errors,
  }) : super(
    message: message,
    code: code,
  );
  
  @override
  List<Object?> get props => [...super.props, errors];
}

/// 同步错误
class SyncFailure extends Failure {
  final String? table;
  
  const SyncFailure({
    required String message,
    String? code,
    this.table,
  }) : super(
    message: message,
    code: code,
  );
  
  @override
  List<Object?> get props => [...super.props, table];
}

/// 内部错误
class InternalFailure extends Failure {
  const InternalFailure({
    required String message,
    String? code,
  }) : super(
    message: message,
    code: code,
  );
}