import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import '../repositories/user_repository.dart';
import '../entities/user_preferences.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 更新用户偏好设置参数
class UpdateUserPreferencesParams extends Equatable {
  /// 用户ID
  final String userId;
  
  /// 偏好设置数据
  final Map<String, dynamic> preferences;

  /// 构造函数
  const UpdateUserPreferencesParams({
    required this.userId,
    required this.preferences,
  });

  @override
  List<Object> get props => [userId, preferences];
}

/// 更新用户偏好设置用例
class UpdateUserPreferences implements UseCase<UserPreferences, UpdateUserPreferencesParams> {
  /// 用户存储库
  final UserRepository repository;

  /// 构造函数
  UpdateUserPreferences({required this.repository});

  @override
  Future<Either<Failure, UserPreferences>> call(UpdateUserPreferencesParams params) async {
    return await repository.updateUserPreferences(
      params.userId,
      params.preferences,
    );
  }
} 