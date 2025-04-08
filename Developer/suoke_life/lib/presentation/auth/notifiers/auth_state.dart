import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/entities/user.dart';

/// 认证状态
class AuthState {
  /// 是否已认证
  final bool isAuthenticated;
  
  /// 是否加载中
  final bool isLoading;
  
  /// 用户信息
  final User? user;
  
  /// 认证令牌
  final AuthToken? authToken;
  
  /// 错误信息
  final String? error;
  
  /// 是否需要两步验证
  final bool needsTwoFactorAuth;
  
  /// 临时令牌
  final String? temporaryToken;

  /// 构造函数
  const AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.user,
    this.authToken,
    this.error,
    this.needsTwoFactorAuth = false,
    this.temporaryToken,
  });

  /// 创建初始状态
  factory AuthState.initial() {
    return const AuthState(
      isAuthenticated: false,
      isLoading: false,
    );
  }

  /// 创建加载状态
  factory AuthState.loading() {
    return const AuthState(
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
    AuthToken? authToken,
    String? error,
    bool? needsTwoFactorAuth,
    String? temporaryToken,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      user: user,
      authToken: authToken,
      error: error,
      needsTwoFactorAuth: needsTwoFactorAuth ?? this.needsTwoFactorAuth,
      temporaryToken: temporaryToken,
    );
  }
} 