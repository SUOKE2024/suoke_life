import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 密码强度枚举
enum PasswordStrength {
  /// 弱密码
  weak,
  
  /// 中等强度密码
  medium,
  
  /// 强密码
  strong
}

/// 风险级别枚举
enum RiskLevel {
  /// 低风险
  low,
  
  /// 中等风险
  medium,
  
  /// 高风险
  high,
  
  /// 严重风险
  critical
}

/// 认证结果
/// 
/// 在用户登录、注册或刷新令牌后返回的结果
class AuthResult {
  /// 用户
  final User user;
  
  /// 令牌
  final AuthToken token;
  
  /// 是否需要双因素认证
  final bool requires2FA;
  
  /// 是否需要双因素认证（别名，兼容性使用）
  bool get needsTwoFactorAuth => requires2FA;
  
  /// 双因素认证类型
  final String? twoFactorType;
  
  /// 双因素认证临时令牌
  final String? twoFactorToken;
  
  /// 双因素认证临时令牌（别名，兼容性使用）
  String? get temporaryToken => twoFactorToken;

  /// 访问令牌getter
  String get accessToken => token.accessToken;
  
  /// 刷新令牌getter
  String get refreshToken => token.refreshToken;
  
  /// 过期时间getter
  int? get expiresIn => token.expiresIn;

  /// 构造函数
  const AuthResult({
    required this.user,
    required this.token,
    this.requires2FA = false,
    this.twoFactorType,
    this.twoFactorToken,
  });
}

/// 用户会话
class UserSession {
  /// 会话ID
  final String id;
  
  /// 设备类型
  final String deviceType;
  
  /// 设备名称
  final String deviceName;
  
  /// 设备信息
  final String device;
  
  /// IP地址
  final String ipAddress;
  
  /// 位置
  final String location;
  
  /// 最后活跃时间
  final DateTime lastActive;
  
  /// 是否为当前会话
  final bool isCurrent;
  
  /// 兼容性getter
  bool get isCurrentSession => isCurrent;

  /// 构造函数
  const UserSession({
    required this.id,
    required this.deviceType,
    required this.deviceName,
    this.device = '',
    required this.ipAddress,
    required this.location,
    required this.lastActive,
    this.isCurrent = false,
  });
}

/// 密码安全评估结果
class PasswordSecurityResult {
  /// 是否安全
  final bool isSecure;
  
  /// 安全评分
  final int score;
  
  /// 安全建议
  final List<String> suggestions;
  
  /// 是否已泄露
  final bool isBreached;
  
  /// 泄露次数
  final int breachCount;
  
  /// 最后检查时间
  final DateTime? lastChecked;

  /// 构造函数
  const PasswordSecurityResult({
    required this.isSecure,
    required this.score,
    required this.suggestions,
    required this.isBreached,
    required this.breachCount,
    this.lastChecked,
  });
}

/// 可疑登录尝试
class SuspiciousLoginAttempt {
  /// ID
  final String id;
  
  /// 时间戳
  final DateTime timestamp;
  
  /// IP地址
  final String ipAddress;
  
  /// 位置
  final String location;
  
  /// 设备信息
  final String deviceInfo;
  
  /// 原因
  final String reason;
  
  /// 是否已阻止
  final bool wasBlocked;
  
  /// 风险级别
  final RiskLevel riskLevel;

  /// 构造函数
  const SuspiciousLoginAttempt({
    required this.id,
    required this.timestamp,
    required this.ipAddress,
    required this.location,
    required this.deviceInfo,
    required this.reason,
    required this.wasBlocked,
    this.riskLevel = RiskLevel.medium,
  });
}

/// 认证状态详情
class AuthStatusDetails {
  /// 是否已认证
  final bool isAuthenticated;
  
  /// 用户
  final User? user;
  
  /// 访问令牌
  final String? accessToken;
  
  /// 刷新令牌
  final String? refreshToken;
  
  /// 令牌过期时间
  final DateTime? tokenExpiry;
  
  /// 令牌是否有效
  bool get isTokenValid => tokenExpiry != null && 
      DateTime.now().isBefore(tokenExpiry!);
  
  /// 是否启用了双因素认证
  final bool has2FAEnabled;
  
  /// 是否启用了生物识别
  final bool hasBiometricEnabled;
  
  /// 最后登录IP
  final String? lastLoginIp;
  
  /// 最后登录时间
  final DateTime? lastLoginTime;
  
  /// 活跃会话数
  final int activeSessionsCount;

  /// 构造函数
  const AuthStatusDetails({
    required this.isAuthenticated,
    this.user,
    this.accessToken,
    this.refreshToken,
    this.tokenExpiry,
    this.has2FAEnabled = false,
    this.hasBiometricEnabled = false,
    this.lastLoginIp,
    this.lastLoginTime,
    this.activeSessionsCount = 0,
  });
}

/// 认证用例集合
class AuthUseCases {
  /// 认证仓库
  final AuthRepository repository;

  /// 构造函数
  const AuthUseCases({required this.repository});

  /// 使用邮箱和密码登录
  Future<Either<Failure, (User, AuthToken)>> login(String email, String password) async {
    return repository.login(email, password);
  }

  /// 使用微信登录
  Future<AuthResult> loginWithWechat(String code) async {
    return repository.loginWithWechat(code);
  }

  /// 使用小红书登录
  Future<AuthResult> loginWithXiaohongshu(String code, String redirectUri) async {
    return repository.loginWithXiaohongshu(code, redirectUri);
  }

  /// 使用抖音登录
  Future<AuthResult> loginWithDouyin(String code, String redirectUri) async {
    return repository.loginWithDouyin(code, redirectUri);
  }

  /// 使用手机号和验证码登录
  Future<AuthResult> loginWithPhone(String phoneNumber, String verificationCode) async {
    return repository.loginWithPhone(phoneNumber, verificationCode);
  }

  /// 发送短信验证码
  Future<bool> sendSmsVerificationCode(String phoneNumber) async {
    return repository.sendSmsVerificationCode(phoneNumber);
  }

  /// 注册新用户
  Future<Either<Failure, (User, AuthToken)>> register(Map<String, dynamic> userData) async {
    return repository.register(userData);
  }

  /// 验证双因素认证
  Future<AuthResult> verify2FA(String token, String authToken) async {
    return repository.verify2FA(token, authToken);
  }

  /// 刷新令牌
  Future<Either<Failure, AuthToken>> refreshToken(String refreshToken) async {
    return repository.refreshToken(refreshToken);
  }

  /// 登出
  Future<Either<Failure, bool>> logout() async {
    return repository.logout();
  }

  /// 获取当前用户
  Future<User> getCurrentUser() async {
    return repository.getCurrentUser();
  }

  /// 检查认证状态
  Future<bool> checkAuthStatus() async {
    return repository.checkAuthStatus();
  }

  /// 获取认证状态详情
  Future<AuthStatusDetails> getAuthStatusDetails() async {
    return repository.getAuthStatusDetails();
  }

  /// 获取用户会话列表
  Future<List<UserSession>> getSessions() async {
    return repository.getSessions();
  }
  
  /// 验证生物识别
  Future<AuthResult> verifyBiometric(String userId, String biometricToken) async {
    return repository.verifyBiometric(userId, biometricToken);
  }
}