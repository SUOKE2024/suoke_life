import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/user_preferences.dart';
import '../../domain/usecases/update_user_preferences.dart';
import '../../di/providers/user_providers.dart';

/// 用户偏好设置控制器状态
class UserPreferencesState {
  /// 加载状态
  final bool isLoading;
  
  /// 用户偏好设置数据
  final UserPreferences? preferences;
  
  /// 错误信息
  final String? errorMessage;

  /// 构造函数
  const UserPreferencesState({
    this.isLoading = false,
    this.preferences,
    this.errorMessage,
  });

  /// 初始状态
  factory UserPreferencesState.initial() {
    return const UserPreferencesState();
  }

  /// 加载状态
  factory UserPreferencesState.loading() {
    return const UserPreferencesState(isLoading: true);
  }

  /// 加载成功状态
  factory UserPreferencesState.success(UserPreferences preferences) {
    return UserPreferencesState(preferences: preferences);
  }

  /// 错误状态
  factory UserPreferencesState.error(String message) {
    return UserPreferencesState(errorMessage: message);
  }

  /// 创建具有更新字段的新实例
  UserPreferencesState copyWith({
    bool? isLoading,
    UserPreferences? preferences,
    String? errorMessage,
  }) {
    return UserPreferencesState(
      isLoading: isLoading ?? this.isLoading,
      preferences: preferences ?? this.preferences,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

/// 用户偏好设置控制器
class UserPreferencesController extends StateNotifier<UserPreferencesState> {
  /// 更新用户偏好设置用例
  final UpdateUserPreferences _updateUserPreferencesUseCase;

  /// 构造函数
  UserPreferencesController({
    required UpdateUserPreferences updateUserPreferencesUseCase,
  })  : _updateUserPreferencesUseCase = updateUserPreferencesUseCase,
        super(UserPreferencesState.initial());

  /// 更新用户偏好设置
  Future<void> updatePreferences(String userId, Map<String, dynamic> preferences) async {
    state = UserPreferencesState.loading();

    final result = await _updateUserPreferencesUseCase(
      UpdateUserPreferencesParams(userId: userId, preferences: preferences),
    );

    state = result.fold(
      (failure) => UserPreferencesState.error(failure.message),
      (preferences) => UserPreferencesState.success(preferences),
    );
  }
}

/// 用户偏好设置控制器Provider
final userPreferencesControllerProvider = StateNotifierProvider<UserPreferencesController, UserPreferencesState>((ref) {
  final updateUserPreferencesUseCase = ref.watch(updateUserPreferencesUseCaseProvider);
  return UserPreferencesController(updateUserPreferencesUseCase: updateUserPreferencesUseCase);
}); 