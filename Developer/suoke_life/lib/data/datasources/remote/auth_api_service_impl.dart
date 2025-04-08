import 'dart:convert';
import 'package:dio/dio.dart';
import '../../../domain/usecases/auth_usecases.dart';
import '../../../domain/entities/user.dart';
import '../../models/user_model.dart';
import '../../../core/exceptions/auth_exceptions.dart';
import 'auth_api_service.dart';

/// 认证API服务实现
class AuthApiServiceImpl implements AuthApiService {
  final Dio dio;
  final String baseUrl;

  AuthApiServiceImpl({
    required this.dio, 
    this.baseUrl = 'http://118.31.223.213/api/auth'
  });

  @override
  Future<AuthResult> login(String email, String password) async {
    try {
      final response = await dio.post(
        '$baseUrl/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        return AuthResult(
          user: UserModel.fromJson(data['user']).toEntity(),
          accessToken: data['access_token'],
          refreshToken: data['refresh_token'],
          expiresIn: data['expires_in'],
        );
      } else {
        throw InvalidCredentialsException(
          message: response.data['message'] ?? '用户名或密码错误',
        );
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw const InvalidCredentialsException();
      } else if (e.type == DioExceptionType.connectionTimeout) {
        throw const AuthNetworkException();
      } else {
        throw AuthException(
          message: e.message ?? '登录失败，请稍后再试',
          code: 'auth/login-failed',
        );
      }
    }
  }

  @override
  Future<AuthResult> loginWithWechat(String code) async {
    try {
      final response = await dio.post(
        '$baseUrl/login/wechat',
        data: {'code': code},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        return AuthResult(
          user: UserModel.fromJson(data['user']).toEntity(),
          accessToken: data['access_token'],
          refreshToken: data['refresh_token'],
          expiresIn: data['expires_in'],
        );
      } else {
        throw AuthException(
          message: response.data['message'] ?? '微信登录失败',
          code: 'auth/wechat-login-failed',
        );
      }
    } catch (e) {
      if (e is DioException) {
        throw AuthException(
          message: e.message ?? '微信登录失败，请稍后再试',
          code: 'auth/wechat-login-failed',
        );
      }
      rethrow;
    }
  }

  @override
  Future<AuthResult> loginWithXiaohongshu(String code, String redirectUri) async {
    try {
      final response = await dio.post(
        '$baseUrl/login/xiaohongshu',
        data: {
          'code': code,
          'redirect_uri': redirectUri,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        return AuthResult(
          user: UserModel.fromJson(data['user']).toEntity(),
          accessToken: data['access_token'],
          refreshToken: data['refresh_token'],
          expiresIn: data['expires_in'],
        );
      } else {
        throw AuthException(
          message: response.data['message'] ?? '小红书登录失败',
          code: 'auth/xiaohongshu-login-failed',
        );
      }
    } catch (e) {
      if (e is DioException) {
        throw AuthException(
          message: e.message ?? '小红书登录失败，请稍后再试',
          code: 'auth/xiaohongshu-login-failed',
        );
      }
      rethrow;
    }
  }

  // 实现其他必要方法，暂时使用最小可行实现
  @override
  Future<AuthResult> loginWithDouyin(String code, String redirectUri) async {
    // 暂时模拟实现
    await Future.delayed(const Duration(milliseconds: 500));
    throw UnimplementedError('抖音登录尚未实现');
  }

  @override
  Future<AuthResult> loginWithPhone(String phoneNumber, String verificationCode) async {
    // 暂时模拟实现
    await Future.delayed(const Duration(milliseconds: 500));
    throw UnimplementedError('手机号登录尚未实现');
  }

  @override
  Future<bool> sendSmsVerificationCode(String phoneNumber) async {
    // 暂时模拟实现
    await Future.delayed(const Duration(milliseconds: 500));
    return true;
  }

  @override
  Future<AuthResult> register(Map<String, dynamic> userData) async {
    try {
      final response = await dio.post(
        '$baseUrl/register',
        data: userData,
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = response.data;
        return AuthResult(
          user: UserModel.fromJson(data['user']).toEntity(),
          accessToken: data['access_token'],
          refreshToken: data['refresh_token'],
          expiresIn: data['expires_in'],
        );
      } else {
        throw AuthException(
          message: response.data['message'] ?? '注册失败',
          code: 'auth/register-failed',
        );
      }
    } catch (e) {
      if (e is DioException) {
        if (e.response?.statusCode == 409) {
          throw const UserAlreadyExistsException();
        }
        throw AuthException(
          message: e.message ?? '注册失败，请稍后再试',
          code: 'auth/register-failed',
        );
      }
      rethrow;
    }
  }

  @override
  Future<bool> logout(String accessToken) async {
    try {
      final response = await dio.post(
        '$baseUrl/logout',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      return response.statusCode == 200;
    } catch (e) {
      // 即使失败也返回成功，因为我们希望本地能成功登出
      return true;
    }
  }

  @override
  Future<User> getCurrentUser(String accessToken) async {
    try {
      final response = await dio.get(
        '$baseUrl/me',
        options: Options(
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

      if (response.statusCode == 200) {
        return UserModel.fromJson(response.data).toEntity();
      } else {
        throw const UserNotFoundException();
      }
    } catch (e) {
      if (e is DioException && e.response?.statusCode == 401) {
        throw const TokenExpiredException();
      }
      rethrow;
    }
  }

  // 为其余方法提供基本的未实现逻辑，后续可以完善
  @override
  Future<AuthResult> refreshToken(String refreshToken) async {
    // 暂时模拟实现
    await Future.delayed(const Duration(milliseconds: 500));
    throw UnimplementedError('刷新令牌方法尚未实现');
  }

  @override
  Future<AuthResult> verify2FA(String token, String authToken) async {
    // 暂时模拟实现
    await Future.delayed(const Duration(milliseconds: 500));
    throw UnimplementedError('验证双因素认证方法尚未实现');
  }

  // 其他必要方法的基本实现...
  // 这里省略了大部分方法的实现，实际开发中需要完善
} 