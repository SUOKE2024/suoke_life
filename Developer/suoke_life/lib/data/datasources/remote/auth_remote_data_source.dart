import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/models/auth_token_model.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import '../auth_remote_data_source.dart';
import 'api_service.dart';

/// 认证远程数据源实现
class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final ApiService _apiService;

  AuthRemoteDataSourceImpl({required ApiService apiService}) : _apiService = apiService;

  @override
  Future<(UserModel, AuthTokenModel)> login(String email, String password) async {
    try {
      final response = await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/login',
        body: {
          'email': email,
          'password': password,
        },
      );

      final userModel = UserModel.fromJson(response['user']);
      final tokenModel = AuthTokenModel.fromJson(response['token']);

      return (userModel, tokenModel);
    } catch (e) {
      throw ServerException(
        message: '登录失败: ${e.toString()}',
        statusCode: 401,
      );
    }
  }

  @override
  Future<(UserModel, AuthTokenModel)> register(Map<String, dynamic> userData) async {
    try {
      final response = await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/register',
        body: userData,
      );

      final userModel = UserModel.fromJson(response['user']);
      final tokenModel = AuthTokenModel.fromJson(response['token']);

      return (userModel, tokenModel);
    } catch (e) {
      throw ServerException(
        message: '注册失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }

  @override
  Future<AuthTokenModel> refreshToken(String refreshToken) async {
    try {
      final response = await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/refresh',
        body: {
          'refreshToken': refreshToken,
        },
      );

      return AuthTokenModel.fromJson(response);
    } catch (e) {
      throw ServerException(
        message: '刷新令牌失败: ${e.toString()}',
        statusCode: 401,
      );
    }
  }

  @override
  Future<bool> logout() async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/logout',
        requiresAuth: true,
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '登出失败: ${e.toString()}',
        statusCode: 500,
      );
    }
  }

  @override
  Future<bool> verifyEmail(String email, String code) async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/verify-email',
        body: {
          'email': email,
          'code': code,
        },
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '验证邮箱失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }

  @override
  Future<bool> sendPasswordResetEmail(String email) async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/send-reset-email',
        body: {
          'email': email,
        },
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '发送重置密码邮件失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }

  @override
  Future<bool> resetPassword(String email, String code, String newPassword) async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/reset-password',
        body: {
          'email': email,
          'code': code,
          'newPassword': newPassword,
        },
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '重置密码失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }

  @override
  Future<bool> changePassword(String oldPassword, String newPassword) async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/change-password',
        body: {
          'oldPassword': oldPassword,
          'newPassword': newPassword,
        },
        requiresAuth: true,
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '修改密码失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }

  @override
  Future<bool> sendPhoneVerificationCode(String phoneNumber) async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/send-phone-code',
        body: {
          'phoneNumber': phoneNumber,
        },
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '发送手机验证码失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }

  @override
  Future<bool> verifyPhone(String phoneNumber, String code) async {
    try {
      await _apiService.post(
        '${ApiConstants.baseUrl}${ApiConstants.auth}/verify-phone',
        body: {
          'phoneNumber': phoneNumber,
          'code': code,
        },
      );

      return true;
    } catch (e) {
      throw ServerException(
        message: '验证手机号失败: ${e.toString()}',
        statusCode: 400,
      );
    }
  }
} 