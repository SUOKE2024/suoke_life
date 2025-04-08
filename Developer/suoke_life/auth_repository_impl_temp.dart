import 'dart:convert';
import 'package:suoke_life/core/exceptions/auth_exceptions.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';
import 'package:suoke_life/core/utils/storage_keys.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/data/datasources/remote/api_service.dart';
import '../datasources/remote/auth_api_service.dart';
import '../../domain/entities/user.dart';
import '../../domain/usecases/auth_usecases.dart';
import '../models/user_model.dart';
import 'package:dartz/dartz.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/auth_remote_data_source.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/core/error/exceptions.dart' show ServerException;
import 'package:device_info_plus/device_info_plus.dart';
import 'dart:io';
import 'package:uuid/uuid.dart';

/// 身份验证存储库实现
class AuthRepositoryImpl implements AuthRepository {
  final SecureStorage secureStorage;
  final ApiService apiService;
  final AuthApiService _authApiService;

  /// 当前是否已认证
  bool _isAuthenticated = false;

  /// 远程数据源
  final AuthRemoteDataSource remoteDataSource;
  
  /// 网络信息
  final NetworkInfo networkInfo;

  AuthRepositoryImpl({
    required this.secureStorage,
    required this.apiService,
    required AuthApiService authApiService,
    required this.remoteDataSource,
    required this.networkInfo,
  }) : _authApiService = authApiService {
    // 初始化时尝试读取token，判断是否已认证
    _initAuthentication();
  }

  /// 初始化认证状态
  Future<void> _initAuthentication() async {
    final token = await secureStorage.read(StorageKeys.userToken);
    _isAuthenticated = token != null;
  }

  @override
  bool get isAuthenticated => _isAuthenticated;

  @override
  Future<String?> getToken() async {
    return await secureStorage.read(StorageKeys.userToken);
  }

  @override
  Future<String?> getAccessToken() async {
    return await secureStorage.read(StorageKeys.userToken);
  }

  @override
  Future<Either<Failure, (User, AuthToken)>> login(String email, String password) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.login(email, password);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, result.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.refreshToken);
        await secureStorage.write(StorageKeys.userId, result.user.id);
        
        _isAuthenticated = true;
        return Right((result.user, AuthToken(
          accessToken: result.accessToken,
          refreshToken: result.refreshToken,
          expiresIn: result.expiresIn ?? 3600,
        )));
      } on AuthException catch (e) {
        return Left(AuthenticationFailure(message: e.message));
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '无网络连接'));
    }
  }

  @override
  Future<AuthResult> loginWithWechat(String code) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.loginWithWechat(code);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, result.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.refreshToken);
        await secureStorage.write(StorageKeys.userId, result.user.id);
        
        _isAuthenticated = true;
        return result;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw const AuthNetworkException(message: '无网络连接');
    }
  }

  @override
  Future<AuthResult> loginWithXiaohongshu(String code, String redirectUri) async {
    if (await networkInfo.isConnected) {
      try {
        final response = await _authApiService.loginWithXiaohongshu(code, redirectUri);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, response.token.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, response.token.refreshToken);
        await secureStorage.write(StorageKeys.userId, response.user.id);
        
        _isAuthenticated = true;
        return response;
      } on ServerException catch (e) {
        throw InvalidCredentialsException(
          message: e.message, 
          code: 'auth/xiaohongshu-login-failed'
        );
      }
    } else {
      throw const AuthNetworkException(message: '无网络连接');
    }
  }

  @override
  Future<AuthResult> loginWithDouyin(String code, String redirectUri) async {
    if (await networkInfo.isConnected) {
      try {
        final response = await _authApiService.loginWithDouyin(code, redirectUri);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, response.token.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, response.token.refreshToken);
        await secureStorage.write(StorageKeys.userId, response.user.id);
        
        _isAuthenticated = true;
        return response;
      } on ServerException catch (e) {
        throw InvalidCredentialsException(
          message: e.message, 
          code: 'auth/douyin-login-failed'
        );
      }
    } else {
      throw const AuthNetworkException(message: '无网络连接');
    }
  }

  @override
  Future<AuthResult> loginWithPhone(String phoneNumber, String verificationCode) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.loginWithPhone(phoneNumber, verificationCode);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, result.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.refreshToken);
        await secureStorage.write(StorageKeys.userId, result.user.id);
        
        _isAuthenticated = true;
        return result;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> sendSmsVerificationCode(String phoneNumber) async {
    if (await networkInfo.isConnected) {
      try {
        return await _authApiService.sendSmsVerificationCode(phoneNumber);
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<Either<Failure, (User, AuthToken)>> register(Map<String, dynamic> userData) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.register(userData);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, result.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.refreshToken);
        await secureStorage.write(StorageKeys.userId, result.user.id);
        
        _isAuthenticated = true;
        return Right((result.user, AuthToken(
          accessToken: result.accessToken,
          refreshToken: result.refreshToken,
          expiresIn: result.expiresIn ?? 3600,
        )));
      } on UserAlreadyExistsException catch (e) {
        return Left(AuthenticationFailure(message: e.message));
      } on AuthException catch (e) {
        return Left(AuthenticationFailure(message: e.message));
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '无网络连接'));
    }
  }

  @override
  Future<AuthResult> verify2FA(String token, String authToken) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.verify2FA(token, authToken);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, result.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.refreshToken);
        await secureStorage.write(StorageKeys.userId, result.user.id);
        
        _isAuthenticated = true;
        return result;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<Either<Failure, AuthToken>> refreshToken(String refreshToken) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.refreshToken(refreshToken);
        
        // 更新存储的令牌
        await secureStorage.write(StorageKeys.userToken, result.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.refreshToken);
        
        return Right(AuthToken(
          accessToken: result.accessToken,
          refreshToken: result.refreshToken,
          expiresIn: result.expiresIn ?? 3600,
        ));
      } on TokenExpiredException catch (e) {
        // 刷新令牌过期，需要重新登录
        await logout();
        return Left(AuthenticationFailure(message: e.message));
      } on AuthException catch (e) {
        return Left(AuthenticationFailure(message: e.message));
      } on ServerException catch (e) {
        return Left(ServerFailure(message: e.message));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '无网络连接'));
    }
  }

  @override
  Future<Either<Failure, bool>> logout() async {
    try {
      // 清除本地存储的认证信息
      await secureStorage.delete(StorageKeys.userToken);
      await secureStorage.delete(StorageKeys.refreshToken);
      await secureStorage.delete(StorageKeys.userId);
      
      _isAuthenticated = false;
      return const Right(true);
    } catch (e) {
      return Left(CacheFailure(message: '清除本地认证信息失败'));
    }
  }

  @override
  Future<User> getCurrentUser() async {
    final userId = await secureStorage.read(StorageKeys.userId);
    if (userId == null) {
      throw const AuthException(message: '未找到用户ID', code: 'auth/user-not-found');
    }
    
    // 这里应该调用API获取最新的用户信息
    // 作为临时解决方案，返回一个基础用户对象
    return User(
      id: userId,
      username: 'user',
      email: 'user@example.com',
      displayName: '用户',
      avatarUrl: '',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  @override
  Future<bool> checkAuthStatus() async {
    final token = await secureStorage.read(StorageKeys.userToken);
    final refreshToken = await secureStorage.read(StorageKeys.refreshToken);
    
    if (token == null && refreshToken == null) {
      _isAuthenticated = false;
      return false;
    }
    
    // 如果有刷新令牌但没有访问令牌，尝试刷新
    if (token == null && refreshToken != null) {
      return await autoRefreshToken();
    }
    
    _isAuthenticated = token != null;
    return _isAuthenticated;
  }

  @override
  Future<AuthStatusDetails> getAuthStatusDetails() async {
    final token = await secureStorage.read(StorageKeys.userToken);
    final refreshToken = await secureStorage.read(StorageKeys.refreshToken);
    final userId = await secureStorage.read(StorageKeys.userId);
    
    if (token == null && refreshToken == null) {
      return AuthStatusDetails.unauthenticated();
    }
    
    // 这是一个简化的实现，实际项目中应该验证令牌的有效性
    return AuthStatusDetails.authenticated(
      userId: userId ?? 'unknown',
      tokenExpiry: DateTime.now().add(const Duration(hours: 1)),
      lastActivity: DateTime.now(),
    );
  }

  @override
  Future<List<UserSession>> getSessions() async {
    if (await networkInfo.isConnected) {
      try {
        final sessions = await _authApiService.getUserSessions();
        
        return sessions.map((session) => UserSession(
          id: session['id'],
          device: session['device'] ?? '未知设备',
          ipAddress: session['ip_address'] ?? '未知IP',
          lastActive: DateTime.parse(session['last_active'] ?? DateTime.now().toIso8601String()),
          createdAt: DateTime.parse(session['created_at'] ?? DateTime.now().toIso8601String()),
          isCurrentSession: session['is_current_session'] ?? false,
        )).toList();
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> terminateSession(String sessionId) async {
    if (await networkInfo.isConnected) {
      try {
        return await _authApiService.terminateSession(sessionId);
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> terminateAllOtherSessions() async {
    if (await networkInfo.isConnected) {
      try {
        final sessions = await getSessions();
        
        bool allSucceeded = true;
        for (final session in sessions) {
          if (!session.isCurrentSession) {
            final success = await terminateSession(session.id);
            if (!success) {
              allSucceeded = false;
            }
          }
        }
        
        return allSucceeded;
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<PasswordSecurityResult> checkPasswordSecurity(String password) async {
    // 实现密码安全检查逻辑
    final hasMinimumLength = password.length >= 8;
    final hasUppercase = password.contains(RegExp(r'[A-Z]'));
    final hasLowercase = password.contains(RegExp(r'[a-z]'));
    final hasDigits = password.contains(RegExp(r'[0-9]'));
    final hasSpecialChars = password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'));
    
    final strength = hasMinimumLength && hasUppercase && hasLowercase && hasDigits && hasSpecialChars
        ? PasswordStrength.strong
        : (hasMinimumLength && (hasUppercase || hasLowercase) && (hasDigits || hasSpecialChars)
            ? PasswordStrength.medium
            : PasswordStrength.weak);
    
    final suggestions = <String>[];
    if (!hasMinimumLength) suggestions.add('密码长度应至少为8个字符');
    if (!hasUppercase) suggestions.add('密码应包含大写字母');
    if (!hasLowercase) suggestions.add('密码应包含小写字母');
    if (!hasDigits) suggestions.add('密码应包含数字');
    if (!hasSpecialChars) suggestions.add('密码应包含特殊字符');
    
    return PasswordSecurityResult(
      strength: strength,
      suggestions: suggestions,
      isBreached: false, // 在实际应用中，应检查密码是否已在已知数据泄露中出现
    );
  }

  @override
  Future<bool> changePassword(String oldPassword, String newPassword) async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return true;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> enable2FA(String method) async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return true;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> disable2FA(String verificationCode) async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return true;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<List<String>> getRecoveryCodes() async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return [
          'ABCD-EFGH-IJKL',
          'MNOP-QRST-UVWX',
          'YZAB-CDEF-GHIJ',
          'KLMN-OPQR-STUV',
          'WXYZ-ABCD-EFGH',
        ];
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<List<String>> refreshRecoveryCodes() async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return [
          'NEWC-ODES-1234',
          '5678-ABCD-EFGH',
          'IJKL-MNOP-QRST',
          'UVWX-YZAB-CDEF',
          'GHIJ-KLMN-OPQR',
        ];
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<List<SuspiciousLoginAttempt>> detectSuspiciousLogins() async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return [
          SuspiciousLoginAttempt(
            ipAddress: '192.168.1.1',
            location: '北京',
            timestamp: DateTime.now().subtract(const Duration(days: 1)),
            deviceInfo: '未知设备',
            riskLevel: RiskLevel.medium,
            reason: '位置异常',
          ),
        ];
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> linkSocialAccount(String provider, String code, String? redirectUri) async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return true;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> unlinkSocialAccount(String provider) async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return true;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<Map<String, bool>> getLinkedSocialAccounts() async {
    if (await networkInfo.isConnected) {
      try {
        // 这里应调用实际的API端点
        return {
          'wechat': true,
          'xiaohongshu': false,
          'douyin': false,
        };
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<bool> autoRefreshToken() async {
    final storedRefreshToken = await secureStorage.read(StorageKeys.refreshToken);
    if (storedRefreshToken == null) {
      return false;
    }
    
    try {
      final result = await refreshToken(storedRefreshToken);
      return result.isRight();
    } catch (e) {
      return false;
    }
  }

  @override
  Future<bool> registerBiometric(String userId, String biometricType) async {
    if (await networkInfo.isConnected) {
      try {
        final accessToken = await getAccessToken();
        if (accessToken == null) {
          throw const AuthorizationException(message: '未授权的操作，请先登录');
        }
        
        return await _authApiService.registerBiometric(
          userId, 
          biometricType,
          accessToken
        );
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }

  @override
  Future<AuthResult> verifyBiometric(String userId, String biometricToken) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await _authApiService.verifyBiometric(userId, biometricToken);
        
        // 保存认证信息
        await secureStorage.write(StorageKeys.userToken, result.token.accessToken);
        await secureStorage.write(StorageKeys.refreshToken, result.token.refreshToken);
        await secureStorage.write(StorageKeys.userId, result.user.id);
        
        _isAuthenticated = true;
        return result;
      } on AuthException catch (e) {
        throw AuthenticationFailure(message: e.message);
      } on ServerException catch (e) {
        throw ServerFailure(message: e.message);
      } catch (e) {
        throw ServerFailure(message: e.toString());
      }
    } else {
      throw NetworkFailure(message: '无网络连接');
    }
  }
}
