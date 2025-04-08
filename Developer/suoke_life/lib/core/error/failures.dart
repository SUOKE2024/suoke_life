import 'package:equatable/equatable.dart';

/// 失败基类
abstract class Failure extends Equatable {
  /// 失败消息
  final String message;

  /// 构造函数
  const Failure({required this.message});

  @override
  List<Object> get props => [message];
}

/// 服务器失败
class ServerFailure extends Failure {
  /// 构造函数
  const ServerFailure({required String message}) : super(message: message);
}

/// 网络失败
class NetworkFailure extends Failure {
  /// 构造函数
  const NetworkFailure({required String message}) : super(message: message);
}

/// 缓存失败
class CacheFailure extends Failure {
  /// 构造函数
  const CacheFailure({required String message}) : super(message: message);
}

/// 认证失败
class AuthFailure extends Failure {
  /// 构造函数
  const AuthFailure({required String message}) : super(message: message);
}

/// 输入验证失败
class ValidationFailure extends Failure {
  /// 构造函数
  const ValidationFailure({required String message}) : super(message: message);
}

/// 未知失败
class UnknownFailure extends Failure {
  /// 构造函数
  const UnknownFailure({required String message}) : super(message: message);
}

/// 权限失败
class PermissionFailure extends Failure {
  /// 构造函数
  const PermissionFailure({required String message}) : super(message: message);
}

/// 未找到失败
class NotFoundFailure extends Failure {
  /// 构造函数
  const NotFoundFailure({required String message}) : super(message: message);
}

/// 认证失败
class AuthenticationFailure extends Failure {
  /// 构造函数
  const AuthenticationFailure({required String message}) : super(message: message);
} 