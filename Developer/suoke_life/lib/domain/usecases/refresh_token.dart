import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import '../repositories/auth_repository.dart';
import '../entities/auth_token.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 刷新令牌参数
class RefreshTokenParams extends Equatable {
  /// 刷新令牌
  final String refreshToken;

  /// 构造函数
  const RefreshTokenParams({
    required this.refreshToken,
  });

  @override
  List<Object> get props => [refreshToken];
}

/// 刷新令牌用例
class RefreshToken implements UseCase<AuthToken, RefreshTokenParams> {
  /// 认证存储库
  final AuthRepository repository;

  /// 构造函数
  RefreshToken({required this.repository});

  @override
  Future<Either<Failure, AuthToken>> call(RefreshTokenParams params) async {
    return await repository.refreshToken(params.refreshToken);
  }
}