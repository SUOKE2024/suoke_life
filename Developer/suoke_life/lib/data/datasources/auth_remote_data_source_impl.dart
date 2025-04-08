import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/datasources/auth_remote_data_source.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/auth_token_model.dart';

/// 认证远程数据源实现
class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  /// HTTP客户端
  final http.Client client;
  
  /// 基础URL
  final String baseUrl;

  /// 构造函数
  AuthRemoteDataSourceImpl({
    required this.client,
    this.baseUrl = ApiConstants.baseUrl,
  });

  /// 默认请求头
  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };
  
  /// 带认证请求头
  Map<String, String> _authHeaders(String token) => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer $token',
      };

  @override
  Future<(UserModel, AuthTokenModel)> login(String email, String password) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/login'),
      headers: _headers,
      body: json.encode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      final userModel = UserModel.fromJson(jsonData['user']);
      final tokenModel = AuthTokenModel.fromJson(jsonData['token']);
      return (userModel, tokenModel);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '登录失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<(UserModel, AuthTokenModel)> register(Map<String, dynamic> userData) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/register'),
      headers: _headers,
      body: json.encode(userData),
    );

    if (response.statusCode == 201) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      final userModel = UserModel.fromJson(jsonData['user']);
      final tokenModel = AuthTokenModel.fromJson(jsonData['token']);
      return (userModel, tokenModel);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '注册失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<AuthTokenModel> refreshToken(String refreshToken) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/refresh'),
      headers: _headers,
      body: json.encode({
        'refresh_token': refreshToken,
      }),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return AuthTokenModel.fromJson(jsonData['token']);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '令牌刷新失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> logout() async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/logout'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '登出失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> verifyEmail(String email, String code) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/verify-email'),
      headers: _headers,
      body: json.encode({
        'email': email,
        'code': code,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '邮箱验证失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> sendPasswordResetEmail(String email) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/password-reset-email'),
      headers: _headers,
      body: json.encode({
        'email': email,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '发送密码重置邮件失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> resetPassword(String email, String code, String newPassword) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/reset-password'),
      headers: _headers,
      body: json.encode({
        'email': email,
        'code': code,
        'new_password': newPassword,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '密码重置失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> changePassword(String oldPassword, String newPassword) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/change-password'),
      headers: _headers,
      body: json.encode({
        'old_password': oldPassword,
        'new_password': newPassword,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '密码修改失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> sendPhoneVerificationCode(String phoneNumber) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/send-phone-code'),
      headers: _headers,
      body: json.encode({
        'phone_number': phoneNumber,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '发送短信验证码失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<bool> verifyPhone(String phoneNumber, String code) async {
    final response = await client.post(
      Uri.parse('$baseUrl${ApiConstants.auth}/verify-phone'),
      headers: _headers,
      body: json.encode({
        'phone_number': phoneNumber,
        'code': code,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '手机验证失败',
        statusCode: response.statusCode,
      );
    }
  }
} 