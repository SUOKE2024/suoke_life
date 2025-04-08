import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../domain/entities/user.dart';
import '../../../domain/usecases/auth_usecases.dart';
import '../../../core/exceptions/auth_exceptions.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:dartz/dartz.dart';

/// 认证状态
class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final User? user;
  final String? error;
  final bool needsTwoFactorAuth;
  final String? temporaryToken;
  final AuthToken? authToken;

  AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.user,
    this.error,
    this.needsTwoFactorAuth = false,
    this.temporaryToken,
    this.authToken,
  });

  /// 创建初始状态
  factory AuthState.initial() {
    return AuthState(
      isAuthenticated: false,
      isLoading: false,
    );
  }

  /// 创建加载状态
  factory AuthState.loading() {
    return AuthState(
      isAuthenticated: false,
      isLoading: true,
    );
  }

  /// 创建认证成功状态
  factory AuthState.authenticated(User user, AuthToken token) {
    return AuthState(
      isAuthenticated: true,
      isLoading: false,
      user: user,
      authToken: token,
    );
  }

  /// 创建认证失败状态
  factory AuthState.error(String message) {
    return AuthState(
      isAuthenticated: false,
      isLoading: false,
      error: message,
    );
  }

  /// 创建需要双因素认证状态
  factory AuthState.needsTwoFactorAuth(String temporaryToken) {
    return AuthState(
      isAuthenticated: false,
      isLoading: false,
      needsTwoFactorAuth: true,
      temporaryToken: temporaryToken,
    );
  }

  /// 复制并更新状态
  AuthState copyWith({
    bool? isAuthenticated,
    bool? isLoading,
    User? user,
    String? error,
    bool? needsTwoFactorAuth,
    String? temporaryToken,
    AuthToken? authToken,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      user: user ?? this.user,
      error: error,
      needsTwoFactorAuth: needsTwoFactorAuth ?? this.needsTwoFactorAuth,
      temporaryToken: temporaryToken ?? this.temporaryToken,
      authToken: authToken ?? this.authToken,
    );
  }
}

/// 认证状态管理器
class AuthStateNotifier extends StateNotifier<AuthState> {
  final AuthRepository authRepository;
  final SecureStorage secureStorage;

  AuthStateNotifier({
    required this.authRepository,
    required this.secureStorage,
  }) : super(AuthState.initial());

  /// 登录
  Future<void> login(String email, String password) async {
    state = AuthState.loading();
    
    final result = await authRepository.login(email, password);
    
    result.fold(
      (failure) => state = AuthState.error(failure.message),
      (data) {
        final (user, token) = data;
        state = AuthState.authenticated(user, token);
      }
    );
  }

  /// 注册
  Future<void> register(Map<String, dynamic> userData) async {
    state = AuthState.loading();
    
    final result = await authRepository.register(userData);
    
    result.fold(
      (failure) => state = AuthState.error(failure.message),
      (data) {
        final (user, token) = data;
        state = AuthState.authenticated(user, token);
      }
    );
  }

  /// 生物识别认证
  Future<void> verifyBiometric(String userId, String biometricToken) async {
    state = state.copyWith(isLoading: true);
    
    try {
      final result = await authRepository.verifyBiometric(userId, biometricToken);
      state = state.copyWith(
        isAuthenticated: true,
        isLoading: false,
        user: result.user,
        authToken: result.token,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e is AuthenticationFailure ? e.message : '生物识别认证失败',
      );
    }
  }

  /// 注册生物识别
  Future<void> registerBiometric(String userId, String biometricType) async {
    state = state.copyWith(isLoading: true);
    
    try {
      final success = await authRepository.registerBiometric(userId, biometricType);
      state = state.copyWith(
        isLoading: false,
        error: success ? null : '生物识别注册失败',
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e is AuthenticationFailure ? e.message : '生物识别注册失败',
      );
    }
  }

  /// 登出
  Future<void> logout() async {
    state = AuthState.loading();
    
    final result = await authRepository.logout();
    
    result.fold(
      (failure) => state = AuthState.error(failure.message),
      (success) => state = AuthState.initial(),
    );
  }
}
