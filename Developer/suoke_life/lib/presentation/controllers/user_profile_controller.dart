import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/user.dart';
import '../../domain/usecases/update_user_profile.dart';
import '../../di/providers/user_providers.dart';

/// 用户资料控制器状态
class UserProfileState {
  /// 加载状态
  final bool isLoading;
  
  /// 用户数据
  final User? user;
  
  /// 错误信息
  final String? errorMessage;

  /// 构造函数
  const UserProfileState({
    this.isLoading = false,
    this.user,
    this.errorMessage,
  });

  /// 初始状态
  factory UserProfileState.initial() {
    return const UserProfileState();
  }

  /// 加载状态
  factory UserProfileState.loading() {
    return const UserProfileState(isLoading: true);
  }

  /// 加载成功状态
  factory UserProfileState.success(User user) {
    return UserProfileState(user: user);
  }

  /// 错误状态
  factory UserProfileState.error(String message) {
    return UserProfileState(errorMessage: message);
  }

  /// 创建具有更新字段的新实例
  UserProfileState copyWith({
    bool? isLoading,
    User? user,
    String? errorMessage,
  }) {
    return UserProfileState(
      isLoading: isLoading ?? this.isLoading,
      user: user ?? this.user,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

/// 用户资料控制器
class UserProfileController extends StateNotifier<UserProfileState> {
  /// 更新用户资料用例
  final UpdateUserProfile _updateUserProfileUseCase;

  /// 构造函数
  UserProfileController({
    required UpdateUserProfile updateUserProfileUseCase,
  })  : _updateUserProfileUseCase = updateUserProfileUseCase,
        super(UserProfileState.initial());

  /// 更新用户资料
  Future<void> updateProfile(String userId, Map<String, dynamic> profileData) async {
    state = UserProfileState.loading();

    final result = await _updateUserProfileUseCase(
      UpdateUserProfileParams(userId: userId, profileData: profileData),
    );

    state = result.fold(
      (failure) => UserProfileState.error(failure.message),
      (user) => UserProfileState.success(user),
    );
  }
}

/// 用户资料控制器Provider
final userProfileControllerProvider = StateNotifierProvider<UserProfileController, UserProfileState>((ref) {
  final updateUserProfileUseCase = ref.watch(updateUserProfileUseCaseProvider);
  return UserProfileController(updateUserProfileUseCase: updateUserProfileUseCase);
}); 