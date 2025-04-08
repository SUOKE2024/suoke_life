import 'package:dartz/dartz.dart';
import '../repositories/user_repository.dart';
import '../entities/user.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 获取用户资料参数
class Params {
  /// 用户ID
  final String userId;

  /// 构造函数
  const Params({required this.userId});
  
  @override
  String toString() => 'Params(userId: $userId)';
}

/// 获取用户资料用例
class GetUserProfile implements UseCase<User, Params> {
  /// 用户存储库
  final UserRepository repository;

  /// 构造函数
  GetUserProfile(this.repository);

  @override
  Future<Either<Failure, User>> call(Params params) async {
    return await repository.getUserProfile(params.userId);
  }
} 