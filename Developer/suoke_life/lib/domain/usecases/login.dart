import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import '../repositories/auth_repository.dart';
import '../entities/user.dart';
import '../entities/auth_token.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 登录参数
class LoginParams extends Equatable {
  /// 邮箱
  final String email;
  
  /// 密码
  final String password;

  /// 构造函数
  const LoginParams({
    required this.email,
    required this.password,
  });

  @override
  List<Object> get props => [email, password];
}

/// 登录用例
class Login implements UseCase<(User, AuthToken), LoginParams> {
  /// 认证存储库
  final AuthRepository repository;

  /// 构造函数
  Login({required this.repository});

  @override
  Future<Either<Failure, (User, AuthToken)>> call(LoginParams params) async {
    return await repository.login(params.email, params.password);
  }
} 