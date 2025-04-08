import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import '../repositories/auth_repository.dart';
import '../entities/user.dart';
import '../entities/auth_token.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 注册参数
class RegisterParams extends Equatable {
  /// 用户注册数据
  final Map<String, dynamic> userData;

  /// 构造函数
  const RegisterParams({
    required this.userData,
  });

  @override
  List<Object> get props => [userData];
}

/// 注册用例
class Register implements UseCase<(User, AuthToken), RegisterParams> {
  /// 认证存储库
  final AuthRepository repository;

  /// 构造函数
  Register({required this.repository});

  @override
  Future<Either<Failure, (User, AuthToken)>> call(RegisterParams params) async {
    return await repository.register(params.userData);
  }
} 