import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import '../repositories/user_repository.dart';
import '../entities/user.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 更新用户资料参数
class UpdateUserProfileParams extends Equatable {
  /// 用户ID
  final String userId;
  
  /// 资料数据
  final Map<String, dynamic> profileData;

  /// 构造函数
  const UpdateUserProfileParams({
    required this.userId,
    required this.profileData,
  });

  @override
  List<Object> get props => [userId, profileData];
}

/// 更新用户资料用例
class UpdateUserProfile implements UseCase<User, UpdateUserProfileParams> {
  /// 用户存储库
  final UserRepository repository;

  /// 构造函数
  UpdateUserProfile({required this.repository});

  @override
  Future<Either<Failure, User>> call(UpdateUserProfileParams params) async {
    return await repository.updateUserProfile(
      params.userId,
      params.profileData,
    );
  }
} 