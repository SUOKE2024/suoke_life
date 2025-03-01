import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/storage/hydrated_provider.dart';

/// 认证状态数据类
class AuthStateData extends HydratedState {
  final bool isAuthenticated;
  final String? userId;
  final String? username;
  final String? token;
  final DateTime? tokenExpiry;

  const AuthStateData({
    this.isAuthenticated = false,
    this.userId,
    this.username,
    this.token,
    this.tokenExpiry,
  });

  /// 创建认证状态
  factory AuthStateData.authenticated({
    required String userId,
    required String username,
    required String token,
    required DateTime tokenExpiry,
  }) {
    return AuthStateData(
      isAuthenticated: true,
      userId: userId,
      username: username,
      token: token,
      tokenExpiry: tokenExpiry,
    );
  }

  /// 创建未认证状态
  factory AuthStateData.unauthenticated() {
    return const AuthStateData(isAuthenticated: false);
  }

  /// 检查token是否过期
  bool get isTokenExpired {
    if (tokenExpiry == null) return true;
    return DateTime.now().isAfter(tokenExpiry!);
  }

  /// 复制状态
  AuthStateData copyWith({
    bool? isAuthenticated,
    String? userId,
    String? username,
    String? token,
    DateTime? tokenExpiry,
  }) {
    return AuthStateData(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      token: token ?? this.token,
      tokenExpiry: tokenExpiry ?? this.tokenExpiry,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'isAuthenticated': isAuthenticated,
      'userId': userId,
      'username': username,
      'token': token,
      'tokenExpiry': tokenExpiry?.toIso8601String(),
    };
  }

  /// 从JSON创建状态
  factory AuthStateData.fromJson(Map<String, dynamic> json) {
    return AuthStateData(
      isAuthenticated: json['isAuthenticated'] as bool? ?? false,
      userId: json['userId'] as String?,
      username: json['username'] as String?,
      token: json['token'] as String?,
      tokenExpiry: json['tokenExpiry'] != null
          ? DateTime.parse(json['tokenExpiry'] as String)
          : null,
    );
  }
}

/// 身份验证状态Notifier
class AuthStateNotifier extends HydratedStateNotifier<AuthStateData> {
  AuthStateNotifier() : super(AuthStateData.unauthenticated());

  /// 登录
  Future<bool> login(String username, String password) async {
    // TODO: 实现实际登录逻辑，调用API等
    
    // 模拟登录过程
    // 成功时保存Token和用户信息
    final loginSuccess = username.isNotEmpty && password.isNotEmpty;
    
    if (loginSuccess) {
      state = AuthStateData.authenticated(
        userId: 'user_${DateTime.now().millisecondsSinceEpoch}',
        username: username,
        token: 'sample_token_${DateTime.now().millisecondsSinceEpoch}',
        tokenExpiry: DateTime.now().add(const Duration(days: 7)),
      );
      return true;
    }
    return false;
  }

  /// 登出
  void logout() {
    state = AuthStateData.unauthenticated();
    clearPersistedState();
  }

  /// 刷新Token
  Future<bool> refreshToken() async {
    // TODO: 实现Token刷新逻辑
    if (!state.isAuthenticated) return false;
    
    // 模拟刷新过程
    state = state.copyWith(
      token: 'refreshed_token_${DateTime.now().millisecondsSinceEpoch}',
      tokenExpiry: DateTime.now().add(const Duration(days: 7)),
    );
    return true;
  }

  @override
  AuthStateData? fromJson(Map<String, dynamic> json) {
    return AuthStateData.fromJson(json);
  }
}

/// 全局身份验证状态提供者
final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthStateData>((ref) {
  return AuthStateNotifier();
}); 