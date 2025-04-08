/// 认证状态详情
class AuthStatusDetails {
  /// 是否已认证
  final bool isAuthenticated;
  
  /// 用户ID（如果已认证）
  final String? userId;
  
  /// 令牌是否有效
  final bool isTokenValid;
  
  /// 令牌过期时间
  final DateTime? tokenExpiry;
  
  /// 是否需要刷新令牌
  final bool needsRefresh;
  
  /// 最后活动时间
  final DateTime? lastActivity;
  
  /// 是否启用了双因素认证
  final bool isTwoFactorEnabled;
  
  /// 当前活跃的会话数
  final int activeSessions;

  /// 创建认证状态详情
  const AuthStatusDetails({
    this.isAuthenticated = false,
    this.userId,
    this.isTokenValid = false,
    this.tokenExpiry,
    this.needsRefresh = false,
    this.lastActivity,
    this.isTwoFactorEnabled = false,
    this.activeSessions = 0,
  });

  /// 创建未认证状态
  factory AuthStatusDetails.unauthenticated() {
    return const AuthStatusDetails(
      isAuthenticated: false,
      isTokenValid: false,
    );
  }

  /// 创建已认证状态
  factory AuthStatusDetails.authenticated({
    required String userId,
    required DateTime tokenExpiry,
    required DateTime lastActivity,
    bool isTwoFactorEnabled = false,
    int activeSessions = 1,
  }) {
    final now = DateTime.now();
    
    return AuthStatusDetails(
      isAuthenticated: true,
      userId: userId,
      isTokenValid: now.isBefore(tokenExpiry),
      tokenExpiry: tokenExpiry,
      needsRefresh: now.isAfter(tokenExpiry.subtract(const Duration(minutes: 5))),
      lastActivity: lastActivity,
      isTwoFactorEnabled: isTwoFactorEnabled,
      activeSessions: activeSessions,
    );
  }
} 