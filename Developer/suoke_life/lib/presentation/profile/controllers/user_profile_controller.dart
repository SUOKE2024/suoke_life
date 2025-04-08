import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/usecases/update_user_profile.dart';

/// 用户资料状态基类
abstract class UserProfileState {
  const UserProfileState();
}

/// 用户资料初始状态
class UserProfileInitial extends UserProfileState {
  const UserProfileInitial();
}

/// 用户资料加载状态
class UserProfileLoading extends UserProfileState {
  const UserProfileLoading();
}

/// 用户资料成功状态
class UserProfileSuccess extends UserProfileState {
  /// 用户实体
  final User user;

  const UserProfileSuccess(this.user);
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserProfileSuccess && other.user == user;
  }

  @override
  int get hashCode => user.hashCode;
}

/// 用户资料错误状态
class UserProfileError extends UserProfileState {
  /// 错误消息
  final String message;

  const UserProfileError(this.message);
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserProfileError && other.message == message;
  }

  @override
  int get hashCode => message.hashCode;
}

/// 用户资料控制器
class UserProfileController extends StateNotifier<UserProfileState> {
  /// 更新用户资料用例
  final UpdateUserProfile _updateUserProfileUseCase;

  /// 创建用户资料控制器
  UserProfileController({
    required UpdateUserProfile updateUserProfileUseCase,
  }) : _updateUserProfileUseCase = updateUserProfileUseCase,
       super(const UserProfileInitial());

  /// 调试状态
  /// 用于测试
  UserProfileState get debugState => state;

  /// 更新用户资料
  Future<void> updateProfile({
    required String userId,
    required Map<String, dynamic> profileData,
  }) async {
    state = const UserProfileLoading();
    
    final result = await _updateUserProfileUseCase(
      UpdateUserProfileParams(
        userId: userId,
        profileData: profileData,
      ),
    );
    
    state = result.fold(
      (failure) => UserProfileError(failure.message),
      (user) => UserProfileSuccess(user),
    );
  }
}

/// 用户资料控制器提供者
final userProfileControllerProvider = StateNotifierProvider<UserProfileController, UserProfileState>((ref) {
  final updateUserProfile = ref.watch(updateUserProfileProvider);
  return UserProfileController(
    updateUserProfileUseCase: updateUserProfile,
  );
});

/// 更新用户资料用例提供者
final updateUserProfileProvider = Provider<UpdateUserProfile>((ref) {
  final userRepository = ref.watch(userRepositoryProvider);
  return UpdateUserProfile(repository: userRepository);
});

/// 用户存储库提供者
final userRepositoryProvider = Provider((ref) {
  throw UnimplementedError('请在di/providers/user_providers.dart中实现此提供者');
}); 