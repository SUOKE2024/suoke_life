import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/user.dart';
import '../../data/repositories/user_repository_impl.dart';
import '../../core/network/api_client.dart';
import '../providers/auth_providers.dart';

/// 当前用户提供者
/// 提供当前登录用户的信息
final currentUserProvider = FutureProvider<User?>((ref) async {
  final authState = ref.watch(authStateProvider);
  
  if (!authState.isAuthenticated || authState.userId == null) {
    return null;
  }
  
  try {
    final userRepo = ref.read(userRepositoryProvider);
    return await userRepo.getUserById(authState.userId!);
  } catch (e) {
    // 如果获取用户信息失败，但认证状态仍然有效，返回基本用户信息
    return User(
      id: authState.userId!,
      username: authState.username ?? '用户',
    );
  }
});

/// 用户存储库提供者
final userRepositoryProvider = Provider<UserRepositoryImpl>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return UserRepositoryImpl(apiClient: apiClient);
});

/// 用户个人资料状态
class UserProfileState {
  final User? user;
  final bool isLoading;
  final String? errorMessage;
  
  const UserProfileState({
    this.user,
    this.isLoading = false,
    this.errorMessage,
  });
  
  UserProfileState copyWith({
    User? user,
    bool? isLoading,
    String? errorMessage,
  }) {
    return UserProfileState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

/// 用户个人资料Notifier
class UserProfileNotifier extends StateNotifier<UserProfileState> {
  final UserRepositoryImpl _userRepository;
  final Ref _ref;
  
  UserProfileNotifier(this._userRepository, this._ref)
      : super(const UserProfileState());
  
  /// 更新用户资料
  Future<bool> updateUserProfile(User updatedUser, File? avatarFile) async {
    // 设置加载状态
    state = state.copyWith(isLoading: true, errorMessage: null);
    
    try {
      // 先上传头像（如果有）
      String? newAvatarUrl;
      if (avatarFile != null) {
        newAvatarUrl = await _uploadAvatar(avatarFile);
      }
      
      // 更新用户数据
      final user = updatedUser.copyWith(
        avatarUrl: newAvatarUrl ?? updatedUser.avatarUrl,
      );
      
      // 调用API更新用户资料
      final success = await _userRepository.updateUser(user);
      
      if (success) {
        // 更新状态
        state = state.copyWith(
          user: user,
          isLoading: false,
        );
        
        // 刷新当前用户数据
        _ref.invalidate(currentUserProvider);
        
        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          errorMessage: '更新用户资料失败',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '更新用户资料时发生错误: ${e.toString()}',
      );
      return false;
    }
  }
  
  /// 上传头像
  Future<String?> _uploadAvatar(File avatarFile) async {
    try {
      // 模拟上传头像成功
      await Future.delayed(const Duration(seconds: 1));
      return 'https://randomuser.me/api/portraits/men/${DateTime.now().millisecondsSinceEpoch % 100}.jpg';
    } catch (e) {
      // 上传失败，但不影响其他资料更新
      return null;
    }
  }
}

/// 用户个人资料提供者
final userProfileProvider = StateNotifierProvider<UserProfileNotifier, UserProfileState>((ref) {
  final userRepository = ref.watch(userRepositoryProvider);
  return UserProfileNotifier(userRepository, ref);
}); 