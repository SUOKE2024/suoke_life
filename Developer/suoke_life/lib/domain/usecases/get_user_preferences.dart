import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import '../repositories/user_repository.dart';
import '../entities/user_preferences.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 获取用户偏好设置参数
class Params extends Equatable {
  /// 用户ID
  final String userId;

  /// 构造函数
  const Params({required this.userId});

  @override
  List<Object> get props => [userId];
}

/// 获取用户偏好设置用例
class GetUserPreferences implements UseCase<UserPreferences, Params> {
  /// 用户存储库
  final UserRepository repository;

  /// 构造函数
  GetUserPreferences({required this.repository});

  @override
  Future<Either<Failure, UserPreferences>> call(Params params) async {
    return await repository.getUserPreferences(params.userId);
  }
} 