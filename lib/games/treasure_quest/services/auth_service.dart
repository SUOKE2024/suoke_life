import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';
import '../models/player.dart';

class AuthService {
  static const String _baseUrl = 'https://api.suoke.life';
  final Dio _dio = Dio(BaseOptions(baseUrl: _baseUrl));
  final _storage = const FlutterSecureStorage();

  // 单例模式
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  // 修改密码
  Future<bool> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) return false;

      final response = await _dio.post(
        '/api/v1/auth/change-password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
          'confirm_password': confirmPassword,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('修改密码失败: $e');
      return false;
    }
  }

  // 更新隐私设置
  Future<bool> updatePrivacySettings({
    required bool showOnlineStatus,
    required bool showLocation,
    required bool allowFriendRequests,
    required bool showActivityStatus,
    required bool showCollections,
  }) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) return false;

      final response = await _dio.post(
        '/api/v1/user/privacy-settings',
        data: {
          'show_online_status': showOnlineStatus,
          'show_location': showLocation,
          'allow_friend_requests': allowFriendRequests,
          'show_activity_status': showActivityStatus,
          'show_collections': showCollections,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('更新隐私设置失败: $e');
      return false;
    }
  }

  // 获取隐私设置
  Future<Map<String, bool>?> getPrivacySettings() async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) return null;

      final response = await _dio.get(
        '/api/v1/user/privacy-settings',
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        return {
          'show_online_status': data['show_online_status'] ?? true,
          'show_location': data['show_location'] ?? true,
          'allow_friend_requests': data['allow_friend_requests'] ?? true,
          'show_activity_status': data['show_activity_status'] ?? true,
          'show_collections': data['show_collections'] ?? true,
        };
      }
      return null;
    } catch (e) {
      print('获取隐私设置失败: $e');
      return null;
    }
  }

  // 注销账号
  Future<bool> deleteAccount({
    required String password,
    required String reason,
  }) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) return false;

      final response = await _dio.post(
        '/api/v1/auth/delete-account',
        data: {
          'password': password,
          'reason': reason,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );

      if (response.statusCode == 200) {
        await _storage.deleteAll();
        return true;
      }
      return false;
    } catch (e) {
      print('注销账号���败: $e');
      return false;
    }
  }

  // 退出登录
  Future<void> logout() async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token != null) {
        await _dio.post(
          '/api/v1/auth/logout',
          options: Options(
            headers: {'Authorization': 'Bearer $token'},
          ),
        );
      }
    } catch (e) {
      print('退出登录失败: $e');
    } finally {
      await _storage.deleteAll();
    }
  }
} 