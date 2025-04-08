import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/datasources/user_remote_data_source.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/user_preferences_model.dart';
import 'package:suoke_life/data/models/health_data_model.dart';

/// 用户远程数据源实现
class UserRemoteDataSourceImpl implements UserRemoteDataSource {
  /// HTTP客户端
  final http.Client client;
  
  /// 基础URL
  final String baseUrl;

  /// 构造函数
  UserRemoteDataSourceImpl({
    required this.client,
    this.baseUrl = ApiConstants.baseUrl,
  });

  /// 默认请求头
  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  @override
  Future<UserModel> getUserProfile(String userId) async {
    final response = await client.get(
      Uri.parse('$baseUrl${ApiConstants.users}/$userId'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return UserModel.fromJson(jsonData['data']);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '获取用户资料失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<UserModel> updateUserProfile(String userId, Map<String, dynamic> profileData) async {
    final response = await client.put(
      Uri.parse('$baseUrl${ApiConstants.users}/$userId'),
      headers: _headers,
      body: json.encode(profileData),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return UserModel.fromJson(jsonData['data']);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '更新用户资料失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<UserPreferencesModel> getUserPreferences(String userId) async {
    final response = await client.get(
      Uri.parse('$baseUrl${ApiConstants.users}/$userId/preferences'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return UserPreferencesModel.fromJson(jsonData['data']);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '获取用户偏好设置失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<UserPreferencesModel> updateUserPreferences(String userId, Map<String, dynamic> preferences) async {
    final response = await client.put(
      Uri.parse('$baseUrl${ApiConstants.users}/$userId/preferences'),
      headers: _headers,
      body: json.encode(preferences),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return UserPreferencesModel.fromJson(jsonData['data']);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '更新用户偏好设置失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<HealthDataModel> getUserHealthData(String userId, {String? period}) async {
    final queryParams = period != null ? {'period': period} : <String, String>{};
    final uri = Uri.parse('$baseUrl${ApiConstants.users}/$userId/health-data')
        .replace(queryParameters: queryParams);
    
    final response = await client.get(
      uri,
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return HealthDataModel.fromJson(jsonData['data']);
    } else {
      throw ServerException(
        message: json.decode(response.body)['message'] ?? '获取用户健康数据失败',
        statusCode: response.statusCode,
      );
    }
  }
} 