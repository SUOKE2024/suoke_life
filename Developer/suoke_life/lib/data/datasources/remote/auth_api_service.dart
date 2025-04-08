import 'dart:convert';
import 'package:dio/dio.dart';
import '../../../domain/usecases/auth_usecases.dart';
import '../../../domain/entities/user.dart';
import '../../../domain/entities/auth_token.dart';
import '../../models/user_model.dart';
import '../../../core/exceptions/auth_exceptions.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/error/exceptions.dart';

/// 认证API服务接口
abstract class AuthApiService {
  /// 用户登录
  Future<AuthResult> login(String email, String password);

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
  Future<AuthResult> register(Map<String, dynamic> userData);

  /// 验证双因素认证
  Future<AuthResult> verify2FA(String token, String authToken);

  /// 刷新令牌
  Future<AuthResult> refreshToken(String refreshToken);

  /// 登出
  Future<bool> logout(String accessToken);

  /// 获取当前用户
  Future<User> getCurrentUser(String accessToken);

  /// 获取用户会话列表
  Future<List<UserSession>> getSessions(String accessToken);

  /// 注册生物识别
  Future<bool> registerBiometric(String userId, String biometricType, String accessToken);

  /// 使用生物识别验证
  Future<AuthResult> verifyBiometric(String userId, String biometricToken);
  
  /// 终止特定会话
  Future<bool> terminateSession(String sessionId, String accessToken);
  
  /// 终止所有其他会话
  Future<bool> terminateAllOtherSessions(String accessToken);
  
  /// 检查密码安全性
  Future<PasswordSecurityResult> checkPasswordSecurity(String password, String accessToken);
  
  /// 更改密码
  Future<bool> changePassword(String currentPassword, String newPassword, String accessToken);
  
  /// 启用双因素认证
  Future<bool> enable2FA(String method, String accessToken);
  
  /// 禁用双因素认证
  Future<bool> disable2FA(String verificationCode, String accessToken);
  
  /// 获取恢复代码
  Future<List<String>> getRecoveryCodes(String accessToken);
  
  /// 刷新恢复代码
  Future<List<String>> refreshRecoveryCodes(String accessToken);
  
  /// 检测是否有异常登录
  Future<List<SuspiciousLoginAttempt>> detectSuspiciousLogins(String accessToken);
  
  /// 绑定社交媒体账号
  Future<bool> linkSocialAccount(String provider, String code, String? redirectUri, String accessToken);
  
  /// 解绑社交媒体账号
  Future<bool> unlinkSocialAccount(String provider, String accessToken);
  
  /// 获取已绑定的社交媒体账号
  Future<Map<String, bool>> getLinkedSocialAccounts(String accessToken);
}

/// 认证API服务实现
class AuthApiServiceImpl implements AuthApiService {
  final Dio _dio;
  final String _baseUrl = ApiConstants.authServiceUrl;

  AuthApiServiceImpl({required Dio dio}) : _dio = dio;

  @override
  Future<AuthResult> login(String email, String password) async {
    try {
      final response = await _dio.post('$_baseUrl/login', data: {
        'email': email,
        'password': password,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];
        final needsTwoFactorAuth = data['needs_2fa'] ?? false;
        final temporaryToken = data['temporary_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
          requires2FA: needsTwoFactorAuth,
          twoFactorToken: temporaryToken,
        );
      } else {
        throw const InvalidCredentialsException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const InvalidCredentialsException();
      } else if (e.response?.statusCode == 404) {
        throw const UserNotFoundException();
      } else if (e.response?.statusCode == 423) {
        final minutes = e.response?.data['remaining_minutes'] ?? 30;
        throw AccountLockedException(remainingMinutes: minutes);
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }

  @override
  Future<AuthResult> loginWithWechat(String code) async {
    try {
      final response = await _dio.post('$_baseUrl/login/wechat', data: {
        'code': code,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw SocialAuthException(provider: '微信');
      }
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw SocialAuthException(provider: '微信');
      }
    } catch (e) {
      throw SocialAuthException(provider: '微信');
    }
  }

  @override
  Future<AuthResult> loginWithXiaohongshu(String code, String redirectUri) async {
    try {
      final response = await _dio.post('$_baseUrl/login/xiaohongshu', data: {
        'code': code,
        'redirect_uri': redirectUri,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw SocialAuthException(provider: '小红书');
      }
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw SocialAuthException(provider: '小红书');
      }
    } catch (e) {
      throw SocialAuthException(provider: '小红书');
    }
  }

  @override
  Future<AuthResult> loginWithDouyin(String code, String redirectUri) async {
    try {
      final response = await _dio.post('$_baseUrl/login/douyin', data: {
        'code': code,
        'redirect_uri': redirectUri,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw SocialAuthException(provider: '抖音');
      }
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw SocialAuthException(provider: '抖音');
      }
    } catch (e) {
      throw SocialAuthException(provider: '抖音');
    }
  }

  @override
  Future<AuthResult> loginWithPhone(String phoneNumber, String verificationCode) async {
    try {
      final response = await _dio.post('$_baseUrl/login/phone', data: {
        'phone_number': phoneNumber,
        'verification_code': verificationCode,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw const VerificationCodeException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        throw const VerificationCodeException();
      } else if (e.response?.statusCode == 404) {
        throw const UserNotFoundException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }

  @override
  Future<bool> sendSmsVerificationCode(String phoneNumber) async {
    try {
      final response = await _dio.post('$_baseUrl/verify/send-sms', data: {
        'phone_number': phoneNumber,
      });

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 429) {
        throw const SmsSendException(
          message: '发送短信过于频繁，请稍后再试',
        );
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const SmsSendException();
      }
    } catch (e) {
      throw const SmsSendException();
    }
  }

  @override
  Future<AuthResult> register(Map<String, dynamic> userData) async {
    try {
      final response = await _dio.post('$_baseUrl/register', data: userData);

      if (response.statusCode == 201) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw const UserAlreadyExistsException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        final errorData = e.response?.data;
        if (errorData != null && errorData['error'] == 'weak_password') {
          throw const WeakPasswordException();
        } else if (errorData != null && errorData['error'] == 'password_breached') {
          throw const PasswordBreachedException();
        } else {
          throw Exception(errorData?['message'] ?? '注册失败');
        }
      } else if (e.response?.statusCode == 409) {
        throw const UserAlreadyExistsException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }

  @override
  Future<AuthResult> verify2FA(String token, String authToken) async {
    try {
      final response = await _dio.post('$_baseUrl/verify/2fa', data: {
        'token': token,
        'auth_token': authToken,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw const TwoFactorAuthException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        throw const VerificationCodeException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const TwoFactorAuthException();
      }
    } catch (e) {
      throw const TwoFactorAuthException();
    }
  }

  @override
  Future<AuthResult> refreshToken(String refreshToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final newRefreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: newRefreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw const TokenExpiredException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }

  @override
  Future<bool> logout(String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/logout',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } catch (e) {
      // 即使API调用失败，我们也允许用户登出
      return true;
    }
  }

  @override
  Future<User> getCurrentUser(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/me',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        return UserModel.fromJson(response.data);
      } else {
        throw const UserNotFoundException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.response?.statusCode == 404) {
        throw const UserNotFoundException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }

  @override
  Future<List<UserSession>> getSessions(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/sessions',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        final List<dynamic> sessionsData = response.data['sessions'];
        return sessionsData.map((item) {
          return UserSession(
            id: item['id'],
            deviceType: item['device_type'] ?? 'unknown',
            deviceName: item['device_name'] ?? 'Unknown Device',
            device: item['device'] ?? 'unknown',
            ipAddress: item['ip_address'] ?? 'unknown',
            location: item['location'] ?? 'unknown',
            lastActive: DateTime.parse(item['last_active'] ?? DateTime.now().toIso8601String()),
            isCurrent: item['is_current'] ?? false,
          );
        }).toList();
      } else {
        throw Exception('获取会话列表失败');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }

  @override
  Future<bool> registerBiometric(String userId, String biometricType, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/biometric/register',
        data: {
          'user_id': userId,
          'biometric_type': biometricType,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const BiometricAuthException();
      }
    } catch (e) {
      throw const BiometricAuthException();
    }
  }

  @override
  Future<AuthResult> verifyBiometric(String userId, String biometricToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/biometric/verify',
        data: {
          'user_id': userId,
          'biometric_token': biometricToken,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final user = UserModel.fromJson(data['user']);
        final accessToken = data['access_token'];
        final refreshToken = data['refresh_token'];

        return AuthResult(
          user: user,
          token: AuthToken(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: data['expires_in'] ?? 3600,
          ),
        );
      } else {
        throw const BiometricAuthException();
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const BiometricAuthException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const BiometricAuthException();
      }
    } catch (e) {
      throw const BiometricAuthException();
    }
  }
  
  @override
  Future<bool> terminateSession(String sessionId, String accessToken) async {
    try {
      final response = await _dio.delete(
        '$_baseUrl/sessions/$sessionId',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw Exception('终止会话失败');
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<bool> terminateAllOtherSessions(String accessToken) async {
    try {
      final response = await _dio.delete(
        '$_baseUrl/sessions',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw Exception('终止会话失败');
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<PasswordSecurityResult> checkPasswordSecurity(String password, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/password/check',
        data: {'password': password},
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data;
        return PasswordSecurityResult(
          isSecure: data['is_secure'],
          score: data['score'],
          suggestions: List<String>.from(data['suggestions'] ?? []),
          isBreached: data['is_breached'] ?? false,
          breachCount: data['breach_count'] ?? 0,
          lastChecked: data['last_checked'] != null
              ? DateTime.parse(data['last_checked'])
              : null,
        );
      } else {
        throw Exception('检查密码安全性失败');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<bool> changePassword(String currentPassword, String newPassword, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/password/change',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        final errorData = e.response?.data;
        if (errorData != null && errorData['error'] == 'weak_password') {
          throw const WeakPasswordException();
        } else if (errorData != null && errorData['error'] == 'password_breached') {
          throw const PasswordBreachedException();
        } else if (errorData != null && errorData['error'] == 'invalid_current_password') {
          throw const InvalidCredentialsException(
            message: '当前密码不正确',
          );
        } else {
          throw Exception(errorData?['message'] ?? '修改密码失败');
        }
      } else if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<bool> enable2FA(String method, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/2fa/enable',
        data: {'method': method},
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const TwoFactorAuthException();
      }
    } catch (e) {
      throw const TwoFactorAuthException();
    }
  }
  
  @override
  Future<bool> disable2FA(String verificationCode, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/2fa/disable',
        data: {'verification_code': verificationCode},
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        throw const VerificationCodeException();
      } else if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const TwoFactorAuthException();
      }
    } catch (e) {
      throw const TwoFactorAuthException();
    }
  }
  
  @override
  Future<List<String>> getRecoveryCodes(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/2fa/recovery-codes',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        final List<dynamic> codes = response.data['recovery_codes'];
        return codes.map((code) => code.toString()).toList();
      } else {
        throw Exception('获取恢复代码失败');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<List<String>> refreshRecoveryCodes(String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/2fa/recovery-codes/refresh',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        final List<dynamic> codes = response.data['recovery_codes'];
        return codes.map((code) => code.toString()).toList();
      } else {
        throw Exception('刷新恢复代码失败');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<List<SuspiciousLoginAttempt>> detectSuspiciousLogins(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/security/suspicious-logins',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        final List<dynamic> attemptsData = response.data['attempts'];
        return attemptsData.map((data) {
          return SuspiciousLoginAttempt(
            id: data['id'],
            timestamp: DateTime.parse(data['timestamp']),
            ipAddress: data['ip_address'],
            location: data['location'],
            deviceInfo: data['device_info'],
            reason: data['reason'],
            wasBlocked: data['was_blocked'],
          );
        }).toList();
      } else {
        throw Exception('获取可疑登录尝试失败');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<bool> linkSocialAccount(String provider, String code, String? redirectUri, String accessToken) async {
    try {
      final data = {
        'provider': provider,
        'code': code,
        if (redirectUri != null) 'redirect_uri': redirectUri,
      };
      
      final response = await _dio.post(
        '$_baseUrl/social/link',
        data: data,
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.response?.statusCode == 409) {
        throw const UserAlreadyExistsException(
          message: '该社交账号已关联其他用户',
        );
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw SocialAuthException(
          provider: provider,
          message: '${provider}登录失败，请重试',
        );
      }
    } catch (e) {
      throw SocialAuthException(
        provider: provider,
        message: '${provider}登录失败，请重试',
      );
    }
  }
  
  @override
  Future<bool> unlinkSocialAccount(String provider, String accessToken) async {
    try {
      final response = await _dio.delete(
        '$_baseUrl/social/unlink/$provider',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
  
  @override
  Future<Map<String, bool>> getLinkedSocialAccounts(String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/social/linked-accounts',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = response.data['linked_accounts'];
        return data.map((key, value) => MapEntry(key, value as bool));
      } else {
        throw Exception('获取关联账号失败');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const AuthNetworkException();
      } else {
        throw const AuthNetworkException();
      }
    } catch (e) {
      throw const AuthNetworkException();
    }
  }
}
