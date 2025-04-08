import 'package:dartz/dartz.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';
import 'package:suoke_life/core/utils/storage_keys.dart';

/// 身份验证存储库接口
abstract class AuthRepository {
  /// 当前是否已认证
  bool get isAuthenticated;

  /// 使用邮箱和密码登录
  Future<Either<Failure, (User, AuthToken)>> login(String email, String password);

  /// 使用微信登录
  Future<AuthResult> loginWithWechat(String code);

  /// 使用小红书登录
  Future<AuthResult> loginWithXiaohongshu(String code, String redirectUri);

  /// 使用抖音登录
  Future<AuthResult> loginWithDouyin(String code, String redirectUri);

  /// 使用手机号和验证码登录
  Future<AuthResult> loginWithPhone(String phoneNumber, String verificationCode);

  /// 发送短信验证码
  Future<bool> sendSmsVerificationCode(String phoneNumber);

  /// 注册新用户
  Future<Either<Failure, (User, AuthToken)>> register(Map<String, dynamic> userData);

  /// 验证双因素认证
  Future<AuthResult> verify2FA(String token, String authToken);

  /// 刷新令牌
  Future<Either<Failure, AuthToken>> refreshToken(String refreshToken);

  /// 登出
  Future<Either<Failure, bool>> logout();

  /// 获取当前用户
  Future<User> getCurrentUser();

  /// 检查认证状态
  Future<bool> checkAuthStatus();

  /// 获取认证状态详情
  Future<AuthStatusDetails> getAuthStatusDetails();

  /// 获取用户会话列表
  Future<List<UserSession>> getSessions();

  /// 终止特定会话
  Future<bool> terminateSession(String sessionId);

  /// 终止所有其他会话
  Future<bool> terminateAllOtherSessions();

  /// 检查密码安全性
  Future<PasswordSecurityResult> checkPasswordSecurity(String password);

  /// 更改密码
  Future<bool> changePassword(String oldPassword, String newPassword);

  /// 启用双因素认证
  Future<bool> enable2FA(String method);

  /// 禁用双因素认证
  Future<bool> disable2FA(String verificationCode);

  /// 获取恢复码
  Future<List<String>> getRecoveryCodes();

  /// 刷新恢复码
  Future<List<String>> refreshRecoveryCodes();

  /// 检测可疑登录尝试
  Future<List<SuspiciousLoginAttempt>> detectSuspiciousLogins();

  /// 关联社交账户
  Future<bool> linkSocialAccount(String provider, String code, String? redirectUri);

  /// 解除社交账户关联
  Future<bool> unlinkSocialAccount(String provider);

  /// 获取已关联的社交账户
  Future<Map<String, bool>> getLinkedSocialAccounts();

  /// 注册生物识别
  Future<bool> registerBiometric(String userId, String biometricType);

  /// 验证生物识别
  Future<AuthResult> verifyBiometric(String userId, String biometricToken);

  /// 获取令牌 
  Future<String?> getToken();
  
  /// 获取访问令牌
  Future<String?> getAccessToken();
  
  /// 自动刷新令牌
  Future<bool> autoRefreshToken();
}

/// 认证仓库实现
class AuthRepositoryImpl implements AuthRepository {
  final Ref _ref;
  final SecureStorage secureStorage;
  
  AuthRepositoryImpl(this._ref, this.secureStorage);
  
  @override
  bool get isAuthenticated => false; // 默认未认证，实际项目中应检查token
  
  @override
  Future<String?> getToken() async {
    // 返回模拟令牌
    return 'mock_token';
  }
  
  @override
  Future<String?> getAccessToken() async {
    // 返回模拟访问令牌
    return 'mock_access_token';
  }
  
  @override
  Future<bool> autoRefreshToken() async {
    // 模拟刷新令牌成功
    return true;
  }
  
  @override
  Future<Either<Failure, (User, AuthToken)>> login(String email, String password) async {
    // 实际项目中应调用认证API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: email.split('@')[0],
      email: email,
      displayName: '测试用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final token = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return Right((user, token));
  }
  
  @override
  Future<AuthResult> loginWithWechat(String code) async {
    // 实际项目中应调用微信登录API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: 'wechat_user',
      email: 'wechat@example.com',
      displayName: '微信用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final token = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return AuthResult(
      user: user,
      token: token,
    );
  }
  
  @override
  Future<AuthResult> loginWithXiaohongshu(String code, String redirectUri) async {
    // 实际项目中应调用小红书登录API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: 'xhs_user',
      email: 'xiaohongshu@example.com',
      displayName: '小红书用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final token = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return AuthResult(
      user: user,
      token: token,
    );
  }
  
  @override
  Future<AuthResult> loginWithDouyin(String code, String redirectUri) async {
    // 实际项目中应调用抖音登录API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: 'douyin_user',
      email: 'douyin@example.com',
      displayName: '抖音用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final token = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return AuthResult(
      user: user,
      token: token,
    );
  }
  
  @override
  Future<AuthResult> loginWithPhone(String phoneNumber, String verificationCode) async {
    // 实际项目中应调用手机号登录API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: 'phone_user',
      email: 'phone@example.com',
      phoneNumber: phoneNumber,
      displayName: '手机用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final token = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return AuthResult(
      user: user,
      token: token,
    );
  }
  
  @override
  Future<bool> sendSmsVerificationCode(String phoneNumber) async {
    // 实际项目中应调用发送短信验证码API
    await Future.delayed(const Duration(seconds: 1));
    return true;
  }
  
  @override
  Future<Either<Failure, (User, AuthToken)>> register(Map<String, dynamic> userData) async {
    // 实际项目中应调用注册API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: userData['username'] ?? '',
      email: userData['email'] ?? '',
      phoneNumber: userData['phoneNumber'] ?? '',
      displayName: userData['displayName'] ?? '',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final token = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return Right((user, token));
  }
  
  @override
  Future<AuthResult> verify2FA(String token, String authToken) async {
    // 实际项目中应调用验证双因素认证API
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: 'user_123',
      username: '2fa_user',
      email: '2fa@example.com',
      displayName: '双因素认证用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    final authTokenObj = AuthToken(
      accessToken: 'fake_access_token',
      refreshToken: 'fake_refresh_token',
      expiresIn: 3600,
    );
    
    return AuthResult(
      user: user,
      token: authTokenObj,
    );
  }
  
  @override
  Future<Either<Failure, AuthToken>> refreshToken(String refreshToken) async {
    // 实际项目中应调用刷新令牌API
    await Future.delayed(const Duration(seconds: 1));
    
    final token = AuthToken(
      accessToken: 'new_fake_access_token',
      refreshToken: 'new_fake_refresh_token',
      expiresIn: 3600,
    );
    
    return Right(token);
  }
  
  @override
  Future<Either<Failure, bool>> logout() async {
    // 实际项目中应清除认证信息
    await Future.delayed(const Duration(seconds: 1));
    
    try {
      await secureStorage.delete(StorageKeys.userToken);
      await secureStorage.delete(StorageKeys.refreshToken);
      await secureStorage.delete(StorageKeys.userId);
      return const Right(true);
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }
  
  @override
  Future<User> getCurrentUser() async {
    // 实际项目中应调用获取当前用户API
    await Future.delayed(const Duration(seconds: 1));
    
    return User(
      id: 'user_123',
      username: 'current_user',
      email: 'current@example.com',
      displayName: '当前用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
  
  @override
  Future<bool> checkAuthStatus() async {
    // 实际项目中应调用检查认证状态API
    final token = await getAccessToken();
    return token != null;
  }
  
  @override
  Future<AuthStatusDetails> getAuthStatusDetails() async {
    // 实际项目中应调用获取认证状态详情API
    await Future.delayed(const Duration(seconds: 1));
    
    final accessToken = await secureStorage.read(StorageKeys.userToken);
    
    if (accessToken == null) {
      return AuthStatusDetails(
        isAuthenticated: false,
        tokenExpiry: null,
        lastLoginTime: null,
        activeSessionsCount: 0,
      );
    }
    
    return AuthStatusDetails(
      isAuthenticated: true,
      tokenExpiry: DateTime.now().add(const Duration(hours: 1)),
      lastLoginTime: DateTime.now().subtract(const Duration(hours: 2)),
      activeSessionsCount: 1,
    );
  }
  
  @override
  Future<List<UserSession>> getSessions() async {
    // 实际项目中应调用获取会话列表API
    await Future.delayed(const Duration(seconds: 1));
    
    return [
      UserSession(
        id: 'session_1',
        deviceType: 'Mobile',
        deviceName: 'iPhone 13',
        ipAddress: '192.168.1.1',
        location: '北京',
        lastActive: DateTime.now(),
        isCurrent: true,
      ),
      UserSession(
        id: 'session_2',
        deviceType: 'Desktop',
        deviceName: 'Chrome on Windows',
        ipAddress: '192.168.1.2',
        location: '上海',
        lastActive: DateTime.now().subtract(const Duration(days: 1)),
        isCurrent: false,
      ),
    ];
  }

  @override
  Future<bool> terminateSession(String sessionId) async {
    // 模拟终止会话成功
    return true;
  }

  @override
  Future<bool> terminateAllOtherSessions() async {
    // 模拟终止所有其他会话成功
    return true;
  }

  @override
  Future<PasswordSecurityResult> checkPasswordSecurity(String password) async {
    // 返回模拟密码安全检查结果
    return PasswordSecurityResult(
      isSecure: true,
      score: 85,
      suggestions: ['使用更长的密码', '添加特殊字符'],
      isBreached: false,
      breachCount: 0,
    );
  }

  @override
  Future<bool> changePassword(String oldPassword, String newPassword) async {
    // 模拟更改密码成功
    return true;
  }

  @override
  Future<bool> enable2FA(String method) async {
    // 模拟启用双因素认证成功
    return true;
  }

  @override
  Future<bool> disable2FA(String verificationCode) async {
    // 模拟禁用双因素认证成功
    return true;
  }

  @override
  Future<List<String>> getRecoveryCodes() async {
    // 返回模拟恢复码
    return ['12345678', '87654321', 'abcdefgh'];
  }

  @override
  Future<List<String>> refreshRecoveryCodes() async {
    // 返回模拟刷新后的恢复码
    return ['newcode1', 'newcode2', 'newcode3'];
  }

  @override
  Future<List<SuspiciousLoginAttempt>> detectSuspiciousLogins() async {
    // 返回模拟可疑登录尝试
    return [
      SuspiciousLoginAttempt(
        id: '1',
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
        ipAddress: '192.168.1.1',
        location: '北京',
        deviceInfo: 'iPhone 12',
        reason: '不常见位置',
        wasBlocked: true,
      ),
    ];
  }

  @override
  Future<bool> linkSocialAccount(String provider, String code, String? redirectUri) async {
    // 模拟关联社交账户成功
    return true;
  }

  @override
  Future<bool> unlinkSocialAccount(String provider) async {
    // 模拟解除社交账户关联成功
    return true;
  }

  @override
  Future<Map<String, bool>> getLinkedSocialAccounts() async {
    // 返回模拟已关联的社交账户
    return {
      'wechat': true,
      'xiaohongshu': false,
      'douyin': false,
    };
  }

  @override
  Future<bool> registerBiometric(String userId, String biometricType) async {
    // 模拟注册生物识别成功
    return true;
  }

  @override
  Future<AuthResult> verifyBiometric(String userId, String biometricToken) async {
    // 返回模拟生物识别验证结果
    return AuthResult(
      user: User(
        id: 'user_id',
        username: 'username',
        email: 'user@example.com',
      ),
      token: AuthToken(
        accessToken: 'access_token',
        refreshToken: 'refresh_token',
        expiresIn: 3600,
      ),
    );
  }
}

/// 认证仓库Provider
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(ref, ref.read(secureStorageProvider));
});

